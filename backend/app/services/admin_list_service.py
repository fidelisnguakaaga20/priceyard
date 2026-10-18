"""Bounded Admin pages and complete, schema-checked legacy JSON streams."""
from collections.abc import Iterator
from typing import Generic, TypeVar

import anyio
from pydantic import BaseModel
from sqlalchemy import func, select, true
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, aliased
from starlette.concurrency import run_in_threadpool
from starlette.responses import StreamingResponse

PAGE_SIZE = 100
T = TypeVar("T", bound=BaseModel)


class AdminRecordPage(BaseModel, Generic[T]):
    items: list[T]
    total: int
    offset: int
    limit: int = PAGE_SIZE


def _ordering(entity, order):
    return [getattr(entity, name).desc() if descending else getattr(entity, name).asc()
            for name, descending in order]


def admin_record_page(db: Session, model, schema: type[T], *, offset: int, order) -> AdminRecordPage[T]:
    # One statement gives count and rows the same DB snapshot, including an
    # empty/out-of-range page. Count never hydrates the rest of the catalog.
    total = select(func.count().label("total")).select_from(model).cte("matched_total")
    page = select(model).order_by(*_ordering(model, order)).offset(offset).limit(PAGE_SIZE).cte("page_rows")
    entity = aliased(model, page)
    rows = db.execute(select(entity, total.c.total).select_from(total).outerjoin(entity, true())
                      .order_by(*_ordering(entity, order))).all()
    return AdminRecordPage(items=[schema.model_validate(item) for item, _ in rows if item is not None],
                           total=rows[0][1], offset=offset)


def stream_admin_records(engine: Engine, model, schema: type[T], *, order, where=()) -> Iterator[str]:
    statement = select(model).where(*where).order_by(*_ordering(model, order)).execution_options(yield_per=100)

    def content():
        with Session(engine) as db:
            result = db.scalars(statement)
            try:
                yield "["
                first = True
                for item in result:
                    value = schema.model_validate(item).model_dump_json()
                    yield ("" if first else ",") + value
                    first = False
                yield "]"
            finally:
                result.close()
    return content()


class AdminJSONResponse(StreamingResponse):
    def __init__(self, content, *, private=True):
        self._content = content
        super().__init__(content, media_type="application/json", headers={"Cache-Control": "private, no-store"} if private else None)

    async def __call__(self, scope, receive, send):
        try:
            await super().__call__(scope, receive, send)
        finally:
            # StreamingResponse's thread-pool iterator alone does not promise
            # closure after a failed send/disconnect. Own and close the source.
            with anyio.CancelScope(shield=True):
                await run_in_threadpool(self._content.close)
