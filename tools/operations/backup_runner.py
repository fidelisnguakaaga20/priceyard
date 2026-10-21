"""Opt-in, same-owner Windows backup adapter; never runs on import.

Reuses the exact reviewed backup core outside Git. It does not install a task,
read application configuration, upload files, restore databases or run migrations.
"""
from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import hashlib
import getpass
import json
import os
from pathlib import Path
import sys
import subprocess

ROOT = Path(r"C:\Users\HP\AppData\Local\PriceYardPrivateBackup")
CORE = ROOT / "Start-PriceYardDirectEncryptedBackup.py"
CORE_SHA = "bcd92f38c3ca888117c6c9cd5488c8ed66e4639ed37f42ebdae4dddf4731d686"
REVISION = "0022_login_revocation"
PURPOSE = "priceyard-recurring-backup-0022-v1"
ENTROPY = PURPOSE.encode("ascii")
ENROLLMENT = ROOT / "PrivateRestoreEfs" / "recurring-backup-0022.dpapi"
STATUS = ROOT / "recurring-backup-status.json"
_JOB_HANDLES = []  # Held until process exit, when Windows kills any surviving child.


def adapt_core(source: str) -> str:
    """Three exact adaptations; all export/TLS/EFS/integrity code stays intact."""
    changes = (
        ("REVISION = '0021_feedback_screenshot'", "REVISION = '0022_login_revocation'"),
        (
            "def main():\n    global RUN, PASSWORD, ARCHIVE_PASSWORD, ENV\n"
            "    if not sys.stdin.isatty() or not sys.stdout.isatty():\n"
            "        raise RuntimeError('Interactive owner console required; production was not contacted')",
            "def main():\n    global RUN, PASSWORD, ARCHIVE_PASSWORD, ENV\n"
            "    _verify_scheduled_context()",
        ),
        ("    arguments = sys.argv[1:]", "    arguments = []  # enrolled mode never accepts credentials in arguments"),
    )
    for old, new in changes:
        if source.count(old) != 1:
            raise RuntimeError("Reviewed backup source structure changed; stop for review")
        source = source.replace(old, new)
    return source


def validate_enrollment(value: object) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {"purpose", "project", "revision", "database_password", "archive_passphrase"}:
        raise RuntimeError("Invalid protected enrollment")
    if (value["purpose"], value["project"], value["revision"]) != (PURPOSE, "lrvpjfbtmftjkzaxbunk", REVISION):
        raise RuntimeError("Protected enrollment target differs")
    password, archive = value["database_password"], value["archive_passphrase"]
    if not isinstance(password, str) or not password or len(password) > 4096 or "\x00" in password:
        raise RuntimeError("Invalid enrolled database password")
    if not isinstance(archive, str) or len(archive) < 24 or len(archive) > 1024 or any(ord(c) < 32 or ord(c) > 126 for c in archive):
        raise RuntimeError("Archive passphrase must contain at least 24 printable ASCII characters")
    if archive == password:
        raise RuntimeError("Database password and archive passphrase must differ")
    return value


def protected_file(path: Path) -> None:
    """Fail closed before reading secrets or creating plaintext."""
    from ctypes import wintypes
    get = ctypes.WinDLL("kernel32", use_last_error=True).GetFileAttributesW
    get.argtypes = [wintypes.LPCWSTR]
    get.restype = wintypes.DWORD
    attr = get(str(path))
    if attr == 0xFFFFFFFF or attr & 0x400 or not attr & 0x4000:
        raise RuntimeError("Required EFS/no-reparse protection missing")
    for parent in path.parents:
        attrs = get(str(parent))
        if attrs == 0xFFFFFFFF or attrs & 0x400:
            raise RuntimeError("Redirected backup path refused")


def unprotect(data: bytes) -> bytes:
    """DPAPI CurrentUser, with fixed purpose entropy and all UI forbidden."""
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    def blob(value):
        buffer = (ctypes.c_ubyte * len(value)).from_buffer_copy(value)
        return Blob(len(value), buffer), buffer

    source, source_buffer = blob(data)
    entropy, entropy_buffer = blob(ENTROPY)
    output = Blob()
    crypt = ctypes.WinDLL("crypt32", use_last_error=True).CryptUnprotectData
    crypt.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.POINTER(Blob), ctypes.c_void_p,
                      ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    crypt.restype = wintypes.BOOL
    if not crypt(ctypes.byref(source), None, ctypes.byref(entropy), None, None, 1, ctypes.byref(output)):
        raise RuntimeError("Protected enrollment unavailable to this Windows account")
    try:
        return ctypes.string_at(output.data, output.size)
    finally:
        ctypes.memset(output.data, 0, output.size)
        free = ctypes.WinDLL("kernel32", use_last_error=True).LocalFree
        free.argtypes = [ctypes.c_void_p]
        free.restype = ctypes.c_void_p
        free(output.data)


def protect(data: bytes) -> bytes:
    """Enroll with the same DPAPI scope/entropy as the unattended reader."""
    from ctypes import wintypes

    class Blob(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    source_buffer = (ctypes.c_ubyte * len(data)).from_buffer_copy(data)
    entropy_buffer = (ctypes.c_ubyte * len(ENTROPY)).from_buffer_copy(ENTROPY)
    source, entropy = Blob(len(data), source_buffer), Blob(len(ENTROPY), entropy_buffer)
    output = Blob()
    crypt = ctypes.WinDLL("crypt32", use_last_error=True).CryptProtectData
    crypt.argtypes = [ctypes.POINTER(Blob), wintypes.LPCWSTR, ctypes.POINTER(Blob), ctypes.c_void_p,
                      ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    crypt.restype = wintypes.BOOL
    if not crypt(ctypes.byref(source), PURPOSE, ctypes.byref(entropy), None, None, 1, ctypes.byref(output)):
        raise RuntimeError("Cannot create owner-protected backup enrollment")
    try:
        return ctypes.string_at(output.data, output.size)
    finally:
        ctypes.memset(source_buffer, 0, len(source_buffer))
        free = ctypes.WinDLL("kernel32", use_last_error=True).LocalFree
        free.argtypes = [ctypes.c_void_p]
        free.restype = ctypes.c_void_p
        free(output.data)


def load_core(path: Path = CORE) -> str:
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != CORE_SHA:
        raise RuntimeError("Reviewed backup core hash differs; stop for review")
    return adapt_core(raw.decode("utf-8-sig").replace("\r\n", "\n"))


def verify_owner_context() -> None:
    """Always repeat actual SID/ACL/EFS/key guards, even if invoked directly."""
    windows = os.environ.get("SYSTEMROOT", r"C:\Windows")
    launcher = Path(__file__).resolve().with_name("backup_windows.ps1")
    result = subprocess.run(
        [str(Path(windows) / "System32/WindowsPowerShell/v1.0/powershell.exe"),
         "-NoProfile", "-NonInteractive", "-File", str(launcher), "-Action", "Verify"],
        stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        timeout=30, creationflags=subprocess.CREATE_NO_WINDOW,
    )
    if result.returncode:
        raise RuntimeError("Windows backup owner, ACL, EFS or key verification failed")


def protect_child_lifetime() -> None:
    """A terminated task must not leave pg_dump/7z running in the background."""
    from ctypes import wintypes

    class BasicLimits(ctypes.Structure):
        _fields_ = [("process_time", ctypes.c_int64), ("job_time", ctypes.c_int64),
                    ("flags", wintypes.DWORD), ("minimum_working_set", ctypes.c_size_t),
                    ("maximum_working_set", ctypes.c_size_t), ("active_processes", wintypes.DWORD),
                    ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD), ("scheduling", wintypes.DWORD)]

    class IoCounters(ctypes.Structure):
        _fields_ = [(name, ctypes.c_uint64) for name in
                    ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]

    class ExtendedLimits(ctypes.Structure):
        _fields_ = [("basic", BasicLimits), ("io", IoCounters),
                    ("process_memory", ctypes.c_size_t), ("job_memory", ctypes.c_size_t),
                    ("peak_process_memory", ctypes.c_size_t), ("peak_job_memory", ctypes.c_size_t)]

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    kernel.CreateJobObjectW.restype = wintypes.HANDLE
    kernel.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    kernel.SetInformationJobObject.restype = wintypes.BOOL
    kernel.GetCurrentProcess.restype = wintypes.HANDLE
    kernel.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    kernel.AssignProcessToJobObject.restype = wintypes.BOOL
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    job = kernel.CreateJobObjectW(None, None)
    if not job:
        raise RuntimeError("Cannot establish bounded backup child lifetime")
    limits = ExtendedLimits()
    limits.basic.flags = 0x2000  # JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE, inherited by children.
    if not kernel.SetInformationJobObject(job, 9, ctypes.byref(limits), ctypes.sizeof(limits)):
        kernel.CloseHandle(job)
        raise RuntimeError("Cannot establish bounded backup child lifetime")
    if not kernel.AssignProcessToJobObject(job, kernel.GetCurrentProcess()):
        kernel.CloseHandle(job)
        raise RuntimeError("Cannot attach this backup to its bounded Windows job")
    _JOB_HANDLES.append(job)


def write_status(state: str, **extra) -> None:
    # No exception/provider strings, credentials, database rows or archive paths.
    previous = {}
    if STATUS.is_file():
        try:
            previous = json.loads(STATUS.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            pass
    payload = {"purpose": PURPOSE, "status": state, "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "last_success_at": previous.get("last_success_at"), "database_restoration_verified": False, **extra}
    if state == "passed":
        payload["last_success_at"] = payload["checked_at"]
    pending = STATUS.with_suffix(".pending")
    pending.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    pending.replace(STATUS)


def enroll() -> int:
    if os.name != "nt" or not sys.stdin.isatty() or not sys.stdout.isatty():
        raise RuntimeError("Private owner console required for one-time enrollment")
    verify_owner_context()
    protected_file(ENROLLMENT.parent)
    if ENROLLMENT.exists():
        raise RuntimeError("Existing protected enrollment preserved; no overwrite")
    source = load_core()
    namespace = {"__name__": "priceyard_enrollment_only", "__file__": str(CORE)}
    exec(compile(source, str(CORE), "exec"), namespace)
    print("One-time private enrollment only. No database connection or backup will occur.")
    print("Keep the separate archive passphrase in your existing password manager or safe paper storage.")
    entered = getpass.getpass("Paste existing Render DATABASE_URL here (hidden; not a command): ")
    try:
        password = namespace["password_from_render_url"](entered)
    finally:
        entered = None
        namespace["clear_current_clipboard"]()
    archive = getpass.getpass("Separate backup archive passphrase, at least 24 characters (hidden): ")
    repeat = getpass.getpass("Repeat archive passphrase (hidden): ")
    if archive != repeat:
        raise RuntimeError("Archive passphrases differ; enrollment was not saved")
    value = validate_enrollment({"purpose": PURPOSE, "project": "lrvpjfbtmftjkzaxbunk", "revision": REVISION,
                                 "database_password": password, "archive_passphrase": archive})
    data = json.dumps(value).encode("utf-8")
    sealed = protect(data)
    if unprotect(sealed) != data:
        raise RuntimeError("Protected enrollment validation failed")
    with ENROLLMENT.open("xb") as file:
        protected_file(ENROLLMENT)
        file.write(sealed); file.flush(); os.fsync(file.fileno())
    value.clear()
    namespace.clear()
    password = archive = repeat = data = None
    print("Protected enrollment saved and verified. No production connection was made.")
    return 0


def run() -> int:
    if os.name != "nt" or os.environ.get("PRICEYARD_BACKUP_APPROVED_SCHEDULE") != PURPOSE:
        raise RuntimeError("Use the reviewed same-owner Windows launcher")
    verify_owner_context()
    protected_file(ENROLLMENT)
    if ENROLLMENT.stat().st_size > 32768:
        raise RuntimeError("Protected enrollment is unexpectedly large")
    source = load_core()  # Validate immutable source before decrypting enrollment.
    protect_child_lifetime()
    import msvcrt
    lock = ROOT / "PrivateRestoreEfs" / "recurring-backup.lock"
    with lock.open("a+b") as handle:
        protected_file(lock)
        handle.seek(0)
        if not handle.read(1):
            handle.write(b"0"); handle.flush()
        handle.seek(0)
        try:
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        except OSError:
            return 3  # Existing bounded run owns the lock; never overlap.
        try:
            credentials = validate_enrollment(json.loads(unprotect(ENROLLMENT.read_bytes()).decode("utf-8")))
            namespace = {"__name__": "priceyard_approved_recurring_backup", "__file__": str(CORE)}

            def verify_context():
                protected_file(ENROLLMENT)
                if os.environ.get("PRICEYARD_BACKUP_APPROVED_SCHEDULE") != PURPOSE:
                    raise RuntimeError("Scheduled context changed")

            def enrolled_hidden(prompt):
                if prompt != "Existing Supabase database password (hidden): ":
                    raise RuntimeError("Unexpected interactive prompt refused")
                return credentials["database_password"]

            exec(compile(source, str(CORE), "exec"), namespace)
            namespace.update(_verify_scheduled_context=verify_context, hidden=enrolled_hidden,
                             choose_archive_password=lambda: credentials["archive_passphrase"])
            write_status("running")
            try:
                namespace["main"]()
            finally:
                # Python cannot promise complete erasure of immutable strings.
                credentials.clear()
                namespace["PASSWORD"] = namespace["ARCHIVE_PASSWORD"] = None
                if isinstance(namespace.get("ENV"), dict):
                    namespace["ENV"].pop("PGPASSWORD", None)
            write_status("passed", encrypted_archive_checked=True)
            return 0
        finally:
            handle.seek(0)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--run-approved", action="store_true")
    modes.add_argument("--enroll-private", action="store_true")
    args = parser.parse_args()
    if not args.run_approved and not args.enroll_private:
        parser.print_help()
        return 0
    try:
        return enroll() if args.enroll_private else run()
    except Exception:
        # Do not expose raw native errors or request another interactive prompt.
        if os.name == "nt" and ROOT.is_dir():
            try:
                write_status("failed")
            except Exception:
                pass
        print("PriceYard recurring backup failed safely; no migration or restore was run.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
