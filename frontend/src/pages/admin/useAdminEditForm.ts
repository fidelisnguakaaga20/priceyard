import { useEffect, useRef, useState } from "react";
import type { ChangeEvent } from "react";
import { apiFetch, ApiError } from "../../services/api";

const missingRecord = "Record not found. Enter an existing ID or leave it blank to create.";
const loadingRecord = "Wait for the selected record to load.";

/** Populate existing controls; an optional paged-list lookup uses the existing ID endpoint. */
export function useAdminEditForm<T extends { id: number }>(data: T[], loading: boolean, setError: (message: string) => void,
  lookup?: { path: string; token: string | null }) {
  const formRef = useRef<HTMLFormElement>(null);
  const [editId, setEditId] = useState("");
  const loadedId = useRef<string | null>(null);

  function onIdChange(event: ChangeEvent<HTMLInputElement>) {
    const input = event.currentTarget;
    const id = input.value;
    input.form?.reset();
    input.value = id;
    input.setCustomValidity(id ? loadingRecord : "");
    loadedId.current = null;
    setError("");
    setEditId(id);
  }

  useEffect(() => {
    const form = formRef.current;
    const candidate = form?.elements.namedItem("id");
    if (!form || !(candidate instanceof HTMLInputElement) || !editId || loading || loadedId.current === editId) return;
    const idInput = candidate;
    const selectedForm = form;
    let current = true;
    const controller = new AbortController();
    function populate(record: T) {
      if (!current || idInput.value !== editId) return;
      if (record.id !== Number(editId)) { failed(missingRecord); return; }
      for (const control of Array.from(selectedForm.elements)) {
        if ((control instanceof HTMLInputElement || control instanceof HTMLTextAreaElement || control instanceof HTMLSelectElement)
            && control.name !== "id" && Object.prototype.hasOwnProperty.call(record, control.name)) {
          const value = (record as Record<string, unknown>)[control.name];
          control.value = value == null ? "" : String(value);
        }
      }
      loadedId.current = editId;
      idInput.setCustomValidity("");
      setError("");
    }
    function failed(message: string) {
      if (!current || idInput.value !== editId) return;
      idInput.setCustomValidity(message); setError(message);
    }
    const record = data.find(item => item.id === Number(editId));
    if (record) populate(record);
    else if (lookup?.token && Number.isSafeInteger(Number(editId)) && Number(editId) > 0 && Number(editId) <= 2_147_483_647) {
      void apiFetch<T>(`${lookup.path}/${Number(editId)}`, { signal: controller.signal }, lookup.token)
        .then(populate).catch(err => failed(err instanceof ApiError && err.status === 404 ? missingRecord : "Unable to load the selected record. Re-enter its ID to retry."));
    } else failed(missingRecord);
    return () => { current = false; controller.abort(); };
  }, [data, loading, editId, setError, lookup?.path, lookup?.token]);

  function canSubmit() {
    const input = formRef.current?.elements.namedItem("id");
    if (!(input instanceof HTMLInputElement) || !input.value) return true;
    if (loadedId.current !== input.value) {
      setError(input.validationMessage || loadingRecord);
      input.reportValidity();
      return false;
    }
    return input.checkValidity();
  }

  return { formRef, onIdChange, canSubmit };
}
