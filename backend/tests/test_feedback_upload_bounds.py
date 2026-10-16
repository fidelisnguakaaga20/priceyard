import base64
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from app.schemas import feedback_schema
from app.schemas.feedback_schema import FeedbackCreate, MAX_SCREENSHOT_BYTES


class FeedbackUploadBoundsTests(unittest.TestCase):
    def test_oversized_encoding_is_rejected_before_decoding(self):
        decode = Mock(return_value=b"x" * (MAX_SCREENSHOT_BYTES + 1))
        encoded = "A" * (4 * ((MAX_SCREENSHOT_BYTES + 2) // 3) + 4)
        with patch.object(feedback_schema, "base64", SimpleNamespace(b64decode=decode)):
            with self.assertRaises(ValidationError):
                FeedbackCreate(rating=5, screenshot_data="data:image/png;base64," + encoded)
        self.assertEqual(decode.call_count, 0, "Oversized content must be rejected before decoding")

    def test_existing_exact_limit_is_still_accepted(self):
        value = "data:image/png;base64," + base64.b64encode(b"x" * MAX_SCREENSHOT_BYTES).decode()
        self.assertEqual(FeedbackCreate(rating=5, screenshot_data=value).screenshot_data, value)

    def test_just_over_decoded_limit_rejected_even_if_encoding_length_matches(self):
        value = "data:image/png;base64," + base64.b64encode(b"x" * (MAX_SCREENSHOT_BYTES + 1)).decode()
        with self.assertRaises(ValidationError):
            FeedbackCreate(rating=5, screenshot_data=value)

    def test_original_optional_and_malformed_inputs(self):
        for value in (None, ""):
            self.assertIsNone(FeedbackCreate(rating=5, screenshot_data=value).screenshot_data)
        for value in ("data:text/html;base64,WA==", "data:image/png;base64,not base64", "data:image/png;base64,é", "data:image/png;base64"):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                FeedbackCreate(rating=5, screenshot_data=value)

    def test_valid_original_image_and_feedback_fields_remain_unchanged(self):
        value = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
        payload = FeedbackCreate(rating=4, screenshot_data=value, complaint_or_suggestion="Synthetic feedback", continue_using_feedback=True)
        self.assertEqual(payload.screenshot_data, value)
        self.assertEqual(payload.complaint_or_suggestion, "Synthetic feedback")
        self.assertTrue(payload.continue_using_feedback)
