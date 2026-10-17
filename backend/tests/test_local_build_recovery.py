"""Build-marker safety without creating files or starting build processes."""
from contextlib import ExitStack
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch


class LocalBuildRecoveryTests(unittest.TestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[2]
        spec = importlib.util.spec_from_file_location("local_build_recovery", root / "tools/local-test/build_frontend.py")
        self.tool = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.tool)
        self.runtime = root / "tools/local-test/runtime/mocked-build-check"

    def controls(self, stack, *, purpose="synthetic-only-no-application-credentials", port_open=False, outcomes=(0, 0)):
        stack.enter_context(patch.object(self.tool, "RUNTIME", self.runtime))
        stack.enter_context(patch("sys.argv", ["build_frontend.py", "--reuse"]))
        probe = stack.enter_context(patch.object(self.tool.socket, "socket"))
        probe.return_value.__enter__.return_value.connect_ex.return_value = 0 if port_open else 1
        stack.enter_context(patch.object(Path, "exists", return_value=False))
        marker = json.dumps({"path": str(self.runtime / "frontend-synthetic-unit"), "purpose": purpose})
        read = stack.enter_context(patch.object(Path, "read_text", return_value=marker))
        stack.enter_context(patch.object(Path, "is_dir", return_value=True))
        stack.enter_context(patch.object(Path, "is_symlink", return_value=False))
        stack.enter_context(patch.object(Path, "rglob", return_value=[]))
        copy = stack.enter_context(patch.object(self.tool.shutil, "copyfile"))
        stack.enter_context(patch.object(self.tool.shutil, "copytree"))
        write = stack.enter_context(patch.object(Path, "write_text"))
        move = stack.enter_context(patch.object(Path, "replace"))
        run = stack.enter_context(patch.object(self.tool.subprocess, "run", side_effect=[SimpleNamespace(returncode=value) for value in outcomes]))
        return read, copy, write, move, run

    def test_failed_resume_never_creates_ready_marker(self):
        with ExitStack() as stack:
            _, _, write, move, run = self.controls(stack, outcomes=(7,))
            self.assertEqual(self.tool.main(), 7)
            self.assertEqual(run.call_count, 1)
            write.assert_not_called()
            move.assert_not_called()

    def test_successful_resume_restores_ready_only_after_both_build_steps(self):
        with ExitStack() as stack:
            _, _, write, move, run = self.controls(stack)
            self.assertEqual(self.tool.main(), 0)
            self.assertEqual(run.call_count, 2)
            write.assert_called_once()
            move.assert_called_once_with(self.runtime / "frontend.json")
            self.assertIn("synthetic-only-no-application-credentials", write.call_args.args[0])

    def test_resume_refuses_unapproved_marker_before_copy_or_build(self):
        with ExitStack() as stack:
            _, copy, write, move, run = self.controls(stack, purpose="unapproved")
            with self.assertRaisesRegex(RuntimeError, "marked workspace"):
                self.tool.main()
            copy.assert_not_called()
            run.assert_not_called()
            write.assert_not_called()
            move.assert_not_called()

    def test_resume_refuses_active_test_port_before_reading_marker(self):
        with ExitStack() as stack:
            read, copy, write, move, run = self.controls(stack, port_open=True)
            with self.assertRaisesRegex(RuntimeError, "Stop local preview/PostgreSQL"):
                self.tool.main()
            for action in (read, copy, write, move, run):
                action.assert_not_called()
