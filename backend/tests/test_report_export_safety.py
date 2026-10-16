import csv
from datetime import datetime, timezone
from decimal import Decimal
from io import StringIO
from types import SimpleNamespace
import unittest

from app.services.report_export_service import CSV_HEADERS, build_price_report_csv


class ReportExportSafetyTests(unittest.TestCase):
    def item(self, **changes):
        values = dict(commodity=SimpleNamespace(name="Egusi"), market=SimpleNamespace(name="Kwali Market"), price_low=Decimal("210000.00"), price_high=Decimal("220000.00"), previous_price_low=None, previous_price_high=None, movement="unknown", update_date_time=datetime(2026, 10, 16, tzinfo=timezone.utc), confidence_level="Low confidence", possible_meaning=None, suggested_action="Watch", market_signals=[], quality_signals=[])
        values.update(changes)
        return SimpleNamespace(**values)

    def row(self, item):
        rows = list(csv.reader(StringIO(build_price_report_csv([item]))))
        self.assertEqual(rows[0], CSV_HEADERS)
        self.assertEqual(len(rows[1]), len(CSV_HEADERS))
        return rows[1]

    def test_formula_text_is_exported_as_literal_text(self):
        for value in ("=1+1", "+1+1", "-1+1", "@SUM(1,1)", " =1+1", "\t=1+1", "\r=1+1", "\n=1+1", "\ufeff=1+1"):
            with self.subTest(value=repr(value)):
                self.assertEqual(self.row(self.item(commodity=SimpleNamespace(name=value)))[0], "'"+value)

    def test_market_and_editorial_text_receive_same_protection(self):
        row = self.row(self.item(market=SimpleNamespace(name="=1+1"), possible_meaning="=2+2", suggested_action="+3+3", confidence_level="@test"))
        self.assertEqual(row[1], "'=1+1")
        self.assertEqual(row[8:11], ["'@test", "'=2+2", "'+3+3"])

    def test_formatted_market_signal_cannot_start_formula(self):
        signal = SimpleNamespace(id=1, signal_type="=1+1", signal_description="synthetic", possible_meaning=None, suggested_action=None)
        self.assertEqual(self.row(self.item(market_signals=[signal]))[11], "'=1+1: synthetic")

    def test_numeric_prices_and_empty_values_unchanged(self):
        row = self.row(self.item())
        self.assertEqual(row[2:6], ["210000.00", "220000.00", "", ""])
        self.assertEqual(row[9], "")

    def test_ordinary_unicode_and_quoted_text_preserved(self):
        text = 'Observation, "checked" — no guarantee\nsecond line'
        row = self.row(self.item(possible_meaning=text))
        self.assertEqual(row[0:2], ["Egusi", "Kwali Market"])
        self.assertEqual(row[9], text)
