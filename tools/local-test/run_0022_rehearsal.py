"""Bounded, local-only launcher for the separately reviewed 0022 RAM rehearsal.

Never contacts a database or provider. Refuses pre-existing Docker/WSL activity
and configuration; temporary configuration is removed only after exact checks.
"""
import csv
import ctypes
import hashlib
import io
import json
import os
from pathlib import Path
import subprocess
import time
import uuid

ROOT = Path(r"C:\Users\HP\AppData\Local\PriceYardPrivateBackup")
RUN = ROOT / "PrivateRestoreEfs" / "supabase-backup-20261019T213738Z"
REPO = Path(__file__).resolve().parents[2]
PYTHON = REPO / ".git/priceyard-local-recovery-20261015/p00/runtime/venv/Scripts/python.exe"
CONTROLLER = Path(__file__).with_name("rehearse_verified_0022_ram.py")
DESKTOP = Path(r"C:\Program Files\Docker\Docker\Docker Desktop.exe")
CLI = r"C:\Program Files\Docker\Docker\resources\bin\docker.exe"
WSL = r"C:\Windows\System32\wsl.exe"
TASKLIST = r"C:\Windows\System32\tasklist.exe"
POWERSHELL = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
CONFIG_BYTES = b"[wsl2]\nmemory=2GB\nprocessors=1\nswap=0\n"
CONFIG_SHA = hashlib.sha256(CONFIG_BYTES).hexdigest()
NO_WINDOW = subprocess.CREATE_NO_WINDOW


def scrubbed_environment():
    allowed = ("SYSTEMROOT", "WINDIR", "USERPROFILE", "APPDATA", "LOCALAPPDATA",
               "TEMP", "TMP", "PATH")
    result = {key: os.environ[key] for key in allowed if key in os.environ}
    result["PYTHONDONTWRITEBYTECODE"] = "1"
    return result


def protected(path):
    from ctypes import wintypes
    getter = ctypes.WinDLL("kernel32", use_last_error=True).GetFileAttributesW
    getter.argtypes, getter.restype = [wintypes.LPCWSTR], wintypes.DWORD
    attrs = getter(str(path))
    if attrs == 0xffffffff or attrs & 0x400 or not attrs & 0x4000:
        raise RuntimeError("EFS_PROTECTION_REQUIRED")


def available_memory():
    class Memory(ctypes.Structure):
        _fields_ = [("length", ctypes.c_ulong), ("load", ctypes.c_ulong)] + [
            (field, ctypes.c_ulonglong) for field in (
                "total_physical", "available_physical", "total_page", "available_page",
                "total_virtual", "available_virtual", "available_extended")]
    value = Memory()
    value.length = ctypes.sizeof(value)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(value)):
        raise RuntimeError("MEMORY_CHECK_FAILED")
    return value.available_physical


def main():
    env = scrubbed_environment()
    config = Path(env["USERPROFILE"]) / ".wslconfig"
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime()) + "-" + uuid.uuid4().hex[:8]
    journal_path = ROOT / ("0022-resource-run-" + stamp + ".json")
    archive_path = ROOT / ("0022-resource-wslconfig-" + stamp + ".txt")
    log_path = RUN / ("0022-controller-" + stamp + "-private.log")
    journal = {"status": "failed", "production_connection": False,
               "original_wslconfig_absent": False, "temporary_config_created": False,
               "temporary_config_sha256": CONFIG_SHA, "desktop_started_by_runner": False,
               "desktop_cleanup_passed": False, "temporary_config_removed": False}
    started = False

    def command(args, timeout=10):
        return subprocess.run(args, env=env, capture_output=True, timeout=timeout,
                              creationflags=NO_WINDOW)

    def save():
        journal_path.write_text(json.dumps(journal, indent=2) + "\n", encoding="utf-8")

    def running_distros():
        result = command([WSL, "--list", "--running", "--quiet"])
        if result.returncode:
            raise RuntimeError("WSL_STATE_CHECK_FAILED")
        output = result.stdout.decode("utf-16-le").lstrip("\ufeff").strip()
        return [line.strip() for line in output.splitlines() if line.strip()]

    def process_names():
        result = command([TASKLIST, "/FO", "CSV", "/NH"])
        if result.returncode:
            raise RuntimeError("PROCESS_STATE_CHECK_FAILED")
        return {row[0].lower() for row in csv.reader(
            io.StringIO(result.stdout.decode("mbcs"))) if row}

    def stop_own_docker_fallback():
        journal["desktop_cleanup_fallback_used"] = True
        save()
        script = r"""
$ErrorActionPreference='Stop'
$earliest=LAUNCH_EPOCH_MS
$dockerRoot='C:\Program Files\Docker\Docker\'
$items=@(Get-Process -Name 'Docker Desktop','com.docker.backend' -ErrorAction SilentlyContinue)
$verified=@()
foreach($item in $items) {
  try {
    $path=[IO.Path]::GetFullPath($item.Path)
    $ticks=$item.StartTime.ToUniversalTime().Ticks
  } catch { if($null -eq (Get-Process -Id $item.Id -ErrorAction SilentlyContinue)) { continue }; throw }
  if(-not $path.StartsWith($dockerRoot,[StringComparison]::OrdinalIgnoreCase) -or
     [IO.Path]::GetFileName($path) -ine ($item.ProcessName+'.exe') -or
     (($ticks-621355968000000000)/10000) -lt $earliest) { throw 'Process identity changed; preserved' }
  $verified+=@{Id=$item.Id;Path=$path;Ticks=$ticks}
}
foreach($item in $verified) {
  $current=Get-Process -Id $item.Id -ErrorAction SilentlyContinue
  if($null -eq $current) { continue }
  if([IO.Path]::GetFullPath($current.Path) -ine $item.Path -or
     $current.StartTime.ToUniversalTime().Ticks -ne $item.Ticks) { throw 'Process identity changed; preserved' }
  try { Stop-Process -Id $item.Id -Force -ErrorAction Stop }
  catch { if(Get-Process -Id $item.Id -ErrorAction SilentlyContinue) { throw } }
}
""".replace("LAUNCH_EPOCH_MS", str(journal["desktop_launch_epoch_ms"]))
        return command([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", script],
                       timeout=15).returncode == 0

    try:
        for path in (PYTHON, CONTROLLER, DESKTOP):
            if not path.is_file():
                raise RuntimeError("REQUIRED_LOCAL_TOOL_MISSING")
        protected(RUN)
        if available_memory() < 3 * 1024 ** 3:
            raise RuntimeError("THREE_GIB_AVAILABLE_RAM_REQUIRED")
        if os.path.lexists(config):
            raise RuntimeError("EXISTING_WSLCONFIG_PRESERVED")
        journal["original_wslconfig_absent"] = True
        busy = {"docker desktop.exe", "com.docker.backend.exe", "vmmemwsl", "vmmem"}
        if process_names() & busy or running_distros():
            raise RuntimeError("EXISTING_DOCKER_OR_WSL_ACTIVITY_PRESERVED")
        journal["status"] = "running"
        save()
        with config.open("xb") as handle:
            handle.write(CONFIG_BYTES)
        journal["temporary_config_created"] = True
        save()
        startup = subprocess.STARTUPINFO()
        startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startup.wShowWindow = subprocess.SW_HIDE
        journal["desktop_launch_epoch_ms"] = int(time.time() * 1000)
        save()
        process = subprocess.Popen([str(DESKTOP)], env=env, startupinfo=startup,
                                   creationflags=NO_WINDOW, stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        started = True
        journal["desktop_started_by_runner"] = True
        journal["desktop_launcher_pid"] = process.pid
        save()
        base = [CLI, "--config", str(ROOT / "docker-feasibility-cli"),
                "--host", "npipe:////./pipe/dockerDesktopLinuxEngine"]
        deadline = time.monotonic() + 90
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise RuntimeError("DOCKER_STARTUP_TIMEOUT")
            try:
                result = command(base + ["info", "--format", "{{.OSType}}"], timeout=min(6, remaining))
                if result.returncode == 0 and result.stdout.strip() == b"linux":
                    break
            except subprocess.TimeoutExpired:
                pass
            if time.monotonic() >= deadline:
                raise RuntimeError("DOCKER_STARTUP_TIMEOUT")
            time.sleep(min(5, max(0, deadline - time.monotonic())))
        with log_path.open("xb") as output:
            protected(log_path)  # Check protection before allowing child output.
            child = subprocess.Popen([str(PYTHON), "-B", str(CONTROLLER)], cwd=REPO,
                                     env=env, creationflags=NO_WINDOW,
                                     stdout=output, stderr=subprocess.STDOUT)
            try:
                code = child.wait(timeout=240)
            except subprocess.TimeoutExpired:
                child.terminate()
                child.wait(timeout=10)
                raise RuntimeError("CONTROLLER_TIMEOUT_PRIVATE_EVIDENCE_PRESERVED")
        journal["controller_exit_code"] = code
        journal["controller_log"] = str(log_path)
        if code:
            raise RuntimeError("CONTROLLER_FAILED_PRIVATE_EVIDENCE_PRESERVED")
        journal["status"] = "passed"
    except Exception as error:
        # Exception text from subprocesses/private logs must never reach stdout.
        journal["status"] = "failed"
        journal["failure_type"] = type(error).__name__
        journal["failure_code"] = str(error) if type(error) is RuntimeError else "LOCAL_GUARD_OR_TOOL_FAILURE"
    finally:
        if started:
            try:
                command([CLI, "desktop", "stop", "--timeout", "30"], timeout=40)
                if "docker-desktop" in running_distros():
                    command([WSL, "--terminate", "docker-desktop"], timeout=20)
                journal["desktop_cleanup_passed"] = (
                    "docker-desktop" not in running_distros() and not process_names() & busy)
            except Exception:
                journal["desktop_cleanup_passed"] = False
            if not journal["desktop_cleanup_passed"]:
                try:
                    fallback = stop_own_docker_fallback()
                    journal["desktop_cleanup_passed"] = (
                        fallback and not process_names() & busy and not running_distros())
                except Exception:
                    journal["desktop_cleanup_passed"] = False
        if journal["temporary_config_created"]:
            try:
                if config.is_symlink() or config.read_bytes() != CONFIG_BYTES:
                    raise RuntimeError("TEMPORARY_CONFIG_CHANGED_PRESERVED")
                with archive_path.open("xb") as handle:
                    handle.write(CONFIG_BYTES)
                if hashlib.sha256(archive_path.read_bytes()).hexdigest() != CONFIG_SHA:
                    raise RuntimeError("CONFIG_ARCHIVE_CHECK_FAILED")
                journal["temporary_config_archive"] = str(archive_path)
                if started and not journal["desktop_cleanup_passed"]:
                    raise RuntimeError("CONFIG_PRESERVED_PENDING_DOCKER_CLEANUP")
                config.unlink()  # Only our exact unchanged, individually checked file.
                journal["temporary_config_removed"] = True
            except Exception:
                journal["config_cleanup_requires_review"] = True
        if started and not journal["desktop_cleanup_passed"]:
            journal["status"] = "failed"
        if journal.get("config_cleanup_requires_review"):
            journal["status"] = "failed"
        save()
    passed = journal["status"] == "passed"
    print("PASSED: isolated 0022 rehearsal and resource cleanup." if passed else
          "STOPPED: private local evidence preserved; no production changes.")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
