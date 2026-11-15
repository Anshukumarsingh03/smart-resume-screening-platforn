"""Quiet one-click launcher for the local TalentLens demo."""
from __future__ import annotations

import ctypes
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
import webbrowser

ROOT = Path(__file__).resolve().parent
VENV = ROOT / ".venv"
PYTHON = VENV / "Scripts" / "python.exe"
PYTHONW = VENV / "Scripts" / "pythonw.exe"
DATA = ROOT / "backend" / "data"
URL = "http://127.0.0.1:8000"
LOG = DATA / "launcher.log"
PID_FILE = DATA / "server.pid"
NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


def message(text: str, title: str = "TalentLens") -> None:
    ctypes.windll.user32.MessageBoxW(0, text, title, 0x10)


def run_logged(command: list[str], timeout: int = 600) -> None:
    with LOG.open("a", encoding="utf-8") as log:
        log.write("\n> " + " ".join(command) + "\n")
        log.flush()
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT,
                                creationflags=NO_WINDOW, timeout=timeout)
    if result.returncode:
        raise RuntimeError(f"Setup command failed (exit {result.returncode}). See {LOG}.")


def healthy() -> bool:
    try:
        with urllib.request.urlopen(URL + "/api/health", timeout=1) as response:
            return response.status == 200
    except (OSError, urllib.error.URLError):
        return False


def free_port() -> bool:
    with socket.socket() as sock:
        return sock.connect_ex(("127.0.0.1", 8000)) != 0


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)
    if healthy():
        webbrowser.open(URL)
        return
    if not free_port():
        message("Port 8000 is already in use. Close the other app or use Stop TalentLens, then try again.")
        return

    if not PYTHON.exists():
        py = shutil.which("py")
        python = shutil.which("python")
        if py:
            run_logged([py, "-3", "-m", "venv", str(VENV)], 120)
        elif python:
            run_logged([python, "-m", "venv", str(VENV)], 120)
        else:
            message("Python 3.10 or newer is required. Install Python from python.org, enable 'Add Python to PATH', then double-click Start TalentLens.vbs again.")
            return

    if not PYTHON.exists():
        raise RuntimeError("Could not create the project Python environment. See launcher.log.")
    run_logged([str(PYTHON), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(ROOT / "requirements.txt")])

    env = os.environ.copy()
    env["DEMO_MODE"] = "true"
    env["DATA_DIR"] = str(DATA)
    log = LOG.open("a", encoding="utf-8")
    child = subprocess.Popen([str(PYTHONW if PYTHONW.exists() else PYTHON), "-m", "uvicorn",
                              "backend.main:app", "--host", "127.0.0.1", "--port", "8000",
                              "--log-level", "warning"], cwd=ROOT, env=env,
                             stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT,
                             creationflags=NO_WINDOW)
    log.close()
    PID_FILE.write_text(str(child.pid), encoding="ascii")
    for _ in range(90):
        if healthy():
            webbrowser.open(URL)
            return
        if child.poll() is not None:
            raise RuntimeError(f"The server stopped during startup. See {LOG}.")
        time.sleep(1)
    raise RuntimeError(f"The server did not become ready in 90 seconds. See {LOG}.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        DATA.mkdir(parents=True, exist_ok=True)
        with LOG.open("a", encoding="utf-8") as log:
            log.write(f"\nLauncher error: {exc}\n")
        message(f"TalentLens could not start.\n\n{exc}")
