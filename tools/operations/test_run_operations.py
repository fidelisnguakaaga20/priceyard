"""Synthetic-only checks for scheduler bounds, privacy and resumable progress."""
from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import io
import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit
import zipfile

import run_operations as ops


def headers(content_type="application/json", **other):
    result = Message()
    result["Content-Type"] = content_type
    for key, value in other.items():
        result[key] = value
    return result


def archive(value, name="checkpoint.json"):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as zipped:
        zipped.writestr(name, json.dumps({"checkpoint": value}))
    return stream.getvalue()


def report(*, checkpoint=None, complete=True, busy=False, outcome="confirmed"):
    outcomes = dict.fromkeys(ops.OUTCOMES, 0)
    if not busy:
        outcomes[outcome] = 1
    return {"busy": busy, "complete": complete, "processed": sum(outcomes.values()),
            "outcomes": outcomes, "checkpoint": checkpoint}


class FakeClient:
    def __init__(self, jsons=(), requests=(), remaining=200):
        self.jsons, self.requests = list(jsons), list(requests)
        self.calls, self.left = [], remaining

    def json(self, url, **kwargs):
        self.calls.append(("json", url, kwargs))
        value = self.jsons.pop(0)
        if isinstance(value, Exception):
            raise value
        return value

    def request(self, url, **kwargs):
        self.calls.append(("request", url, kwargs))
        return self.requests.pop(0)

    def remaining(self):
        return self.left


ENV = {"GITHUB_TOKEN": "synthetic-github-token", "GITHUB_REPOSITORY": ops.REPOSITORY,
       "GITHUB_REF": "refs/heads/master",
       "ACTIONS_ID_TOKEN_REQUEST_URL": "https://run-actions-test.actions.githubusercontent.com/idtoken?api-version=2.0",
       "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "synthetic-request-token"}
JWT = "header." + "synthetic" * 10 + ".signature"


class HttpTests(unittest.TestCase):
    def test_default_client_disables_environment_proxies(self):
        with patch.object(ops, "build_opener") as factory:
            ops.Client()
        proxy_handler = factory.call_args.args[0]
        self.assertEqual(proxy_handler.proxies, {})

    def test_https_and_redirects_fail_closed(self):
        client = ops.Client(opener=Mock())
        for url in ("http://example.org", "https://user:pass@example.org", "https://example.org:444"):
            with self.subTest(url=url), self.assertRaises(ops.SafeFailure):
                client.request(url)
        client.opener.open.assert_not_called()
        client.opener.open.side_effect = HTTPError("https://example.org", 302, "secret-detail", {}, None)
        with self.assertRaises(ops.SafeFailure) as failure:
            client.request("https://example.org")
        self.assertNotIn("secret-detail", str(failure.exception))

    def test_network_error_is_sanitized(self):
        opener = Mock()
        opener.open.side_effect = URLError("private-diagnostic-token")
        with self.assertRaises(ops.SafeFailure) as failure:
            ops.Client(opener=opener).request(ops.API + "/health")
        self.assertNotIn("private-diagnostic-token", str(failure.exception))

    def test_response_has_size_and_json_type_bounds(self):
        response = Mock(status=200, headers=headers("text/html"))
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b"{}"
        opener = Mock()
        opener.open.return_value = response
        client = ops.Client(opener=opener)
        with self.assertRaises(ops.SafeFailure):
            client.json(ops.API + "/health")
        response.headers = headers()
        response.read.return_value = b"x" * (ops.MAX_BODY + 1)
        with self.assertRaises(ops.SafeFailure):
            client.json(ops.API + "/health")
        response.read.assert_called_with(ops.MAX_BODY + 1)

    def test_oidc_is_bound_to_github_and_recovery_audience(self):
        client = FakeClient(jsons=[{"value": JWT}])
        self.assertEqual(ops.oidc_token(client, ENV), JWT)
        request = client.calls[0]
        self.assertEqual(parse_qs(urlsplit(request[1]).query)["audience"], [ops.RECOVERY])
        self.assertEqual(request[2]["headers"]["Authorization"], "Bearer synthetic-request-token")
        for url in ("https://evil.example/idtoken", "http://run.actions.githubusercontent.com/idtoken",
                    "https://run.actions.githubusercontent.com.evil.test/idtoken"):
            with self.subTest(url=url), self.assertRaises(ops.SafeFailure):
                ops.oidc_token(FakeClient(), {**ENV, "ACTIONS_ID_TOKEN_REQUEST_URL": url})


class CheckpointTests(unittest.TestCase):
    def client(self, token="gAAAA_synthetic==", **artifact_changes):
        artifact = {"id": 25, "name": ops.ARTIFACT, "size_in_bytes": 300, "expired": False,
                    "workflow_run": {"id": 20, "head_branch": "master"}, **artifact_changes}
        run = {"path": ops.WORKFLOW, "head_branch": "master", "event": "schedule",
               "head_repository": {"full_name": ops.REPOSITORY}}
        return FakeClient(jsons=[{"artifacts": [artifact], "total_count": 1}, run], requests=[
            (302, headers(Location="https://test.blob.core.windows.net/artifact?signed=synthetic"), b""),
            (200, headers("application/zip"), archive(token)),
        ])

    def test_first_run_can_start_but_listing_failure_cannot_reset_progress(self):
        self.assertIsNone(ops.load_checkpoint(FakeClient(jsons=[{"artifacts": [], "total_count": 0}]), ENV))
        with self.assertRaises(ops.SafeFailure):
            ops.load_checkpoint(FakeClient(jsons=[ops.SafeFailure("Synthetic outage.")]), ENV)
        with self.assertRaises(ops.SafeFailure):
            ops.load_checkpoint(FakeClient(jsons=[{"artifacts": [], "total_count": 1}]), ENV)

    def test_checkpoint_download_does_not_forward_github_authorization(self):
        client = self.client()
        self.assertEqual(ops.load_checkpoint(client, ENV), "gAAAA_synthetic==")
        self.assertIn("headers", client.calls[-2][2])
        self.assertNotIn("headers", client.calls[-1][2])

    def test_wrong_workflow_or_download_origin_cannot_supply_checkpoint(self):
        client = self.client()
        client.jsons[1]["path"] = ".github/workflows/other.yml"
        with self.assertRaises(ops.SafeFailure):
            ops.load_checkpoint(client, ENV)
        client = self.client()
        client.requests[0] = (302, headers(Location="https://attacker.test/archive"), b"")
        with self.assertRaises(ops.SafeFailure):
            ops.load_checkpoint(client, ENV)
        self.assertEqual(len(client.calls), 3)

    def test_zip_traversal_and_plaintext_fields_are_not_accepted(self):
        client = self.client()
        client.requests[1] = (200, headers("application/zip"), archive("token", "../checkpoint.json"))
        with self.assertRaises(ops.SafeFailure):
            ops.load_checkpoint(client, ENV)
        for token in ("customer 123", {"payment_id": 12}, "a" * 4097):
            with self.subTest(token_type=type(token).__name__), self.assertRaises(ops.SafeFailure):
                ops._token(token)

    def test_branch_guard_rejects_nonproduction_workflow(self):
        with self.assertRaises(ops.SafeFailure):
            ops.load_checkpoint(FakeClient(), {**ENV, "GITHUB_REF": "refs/heads/development"})


class RecoveryTests(unittest.TestCase):
    def test_two_pages_resume_then_clear_without_exposing_ids(self):
        client = FakeClient(jsons=[{"value": JWT}, report(complete=False, checkpoint="gAAAA_next=="), report()])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            ops.recover(client, ENV, "gAAAA_previous==", path)
            self.assertEqual(json.loads(path.read_text()), {"checkpoint": None})
        self.assertEqual(len(client.calls), 3)
        self.assertEqual(json.loads(client.calls[1][2]["data"]), {"checkpoint": "gAAAA_previous=="})
        self.assertEqual(json.loads(client.calls[2][2]["data"]), {"checkpoint": "gAAAA_next=="})

    def test_progress_is_saved_before_errors_require_attention(self):
        client = FakeClient(jsons=[{"value": JWT}, report(complete=False, checkpoint="gAAAA_next==", outcome="error")])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            with self.assertRaises(ops.SafeFailure):
                ops.recover(client, ENV, None, path)
            self.assertEqual(json.loads(path.read_text()), {"checkpoint": "gAAAA_next=="})

    def test_busy_keeps_position_and_alerts(self):
        client = FakeClient(jsons=[{"value": JWT}, report(complete=False, busy=True, checkpoint="gAAAA_same==")])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            with self.assertRaises(ops.SafeFailure):
                ops.recover(client, ENV, "gAAAA_same==", path)
            self.assertEqual(json.loads(path.read_text()), {"checkpoint": "gAAAA_same=="})

    def test_invalid_aggregate_or_token_does_not_overwrite_previous_position(self):
        for invalid in (report(checkpoint="gAAAA_wrong=="), {**report(), "payment_id": 99},
                        {**report(), "processed": True}, {**report(), "processed": 26}):
            client = FakeClient(jsons=[{"value": JWT}, invalid])
            with tempfile.TemporaryDirectory() as temp:
                path = Path(temp) / "checkpoint.json"
                ops.save_checkpoint(path, "gAAAA_original==")
                with self.assertRaises(ops.SafeFailure):
                    ops.recover(client, ENV, None, path)
                self.assertEqual(json.loads(path.read_text()), {"checkpoint": "gAAAA_original=="})

    def test_maximum_two_pages_even_with_more_work(self):
        client = FakeClient(jsons=[{"value": JWT}, report(complete=False, checkpoint="gAAAA_one=="),
                                   report(complete=False, checkpoint="gAAAA_two==")])
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            ops.recover(client, ENV, None, path)
            self.assertEqual(json.loads(path.read_text()), {"checkpoint": "gAAAA_two=="})
        self.assertEqual(len(client.calls), 3)

    def test_insufficient_time_sends_no_payment_request(self):
        client = FakeClient(jsons=[{"value": JWT}], remaining=70)
        with tempfile.TemporaryDirectory() as temp, self.assertRaises(ops.SafeFailure):
            ops.recover(client, ENV, None, Path(temp) / "checkpoint.json")
        self.assertEqual(len(client.calls), 1)


class MainTests(unittest.TestCase):
    def test_workflow_recovery_is_explicitly_enabled_after_rollout(self):
        workflow = Path(__file__).resolve().parents[2] / ".github/workflows/priceyard-operations.yml"
        source = workflow.read_text(encoding="utf-8")
        gate = re.search(r"    if: >-\n((?:      .*\n)+)", source).group(1)
        self.assertIn("github.ref == 'refs/heads/master' &&", gate)
        self.assertIn("(vars.PRICEYARD_OPERATIONS_ENABLED == 'true' ||", gate)
        self.assertIn("(github.event_name == 'workflow_dispatch' &&", gate)
        self.assertIn("(inputs.mode == 'health-only' || inputs.mode == 'simulate-failure')))", gate)
        self.assertNotIn("inputs.mode == 'recover'", gate)

    def test_alert_simulation_never_contacts_application_or_provider(self):
        client = Mock()
        with redirect_stderr(io.StringIO()) as error:
            result = ops.main({"OPS_MODE": "simulate-failure"}, client)
        self.assertEqual(result, 1)
        self.assertIn("Controlled alert test", error.getvalue())
        self.assertFalse(client.mock_calls)

    def test_health_only_has_no_identity_checkpoint_or_recovery_call(self):
        client = FakeClient(jsons=[{"status": "healthy"}, {"status": "healthy"}],
                            requests=[(200, headers("text/html"), b"<title>PriceYard</title>")])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(ops.main({"OPS_MODE": "health-only"}, client), 0)
        self.assertEqual([call[1] for call in client.calls],
                         [ops.FRONTEND + "/api/health", ops.API + "/health", ops.FRONTEND + "/login"])

    def test_failed_recovery_step_exposes_only_constant_output_flag(self):
        with tempfile.TemporaryDirectory() as temp:
            path, output = Path(temp) / "checkpoint.json", Path(temp) / "outputs"
            client = FakeClient(jsons=[{"artifacts": [], "total_count": 0}, {"status": "healthy"},
                                       {"status": "healthy"}, {"value": JWT},
                                       report(complete=False, checkpoint="gAAAA_private==", outcome="review_required")],
                                requests=[(200, headers("text/html"), b"PriceYard")])
            environ = {**ENV, "OPS_MODE": "recover", "OPS_STATE_PATH": str(path), "GITHUB_OUTPUT": str(output)}
            with redirect_stderr(io.StringIO()) as error:
                self.assertEqual(ops.main(environ, client), 1)
            self.assertNotIn("gAAAA_private", error.getvalue())
            self.assertEqual(output.read_text(), "checkpoint-written=true\n")

    def test_frontend_failure_alerts_without_disabling_backend_recovery(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "checkpoint.json"
            client = FakeClient(jsons=[{"artifacts": [], "total_count": 0},
                                       ops.SafeFailure("Synthetic frontend outage."),
                                       {"value": JWT}, report()])
            environ = {**ENV, "OPS_MODE": "recover", "OPS_STATE_PATH": str(path)}
            with redirect_stderr(io.StringIO()) as error:
                self.assertEqual(ops.main(environ, client), 1)
            self.assertIn("Synthetic frontend outage", error.getvalue())
            self.assertEqual(json.loads(path.read_text()), {"checkpoint": None})
            self.assertEqual(client.calls[-1][1], ops.RECOVERY)


if __name__ == "__main__":
    unittest.main()
