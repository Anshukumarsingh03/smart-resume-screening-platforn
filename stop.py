"""Stop the TalentLens server recorded by the quiet launcher."""
import ctypes
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent
PID_FILE = ROOT / "backend" / "data" / "server.pid"


def tell(text: str) -> None:
    ctypes.windll.user32.MessageBoxW(0, text, "TalentLens", 0x40)


def main() -> None:
    if not PID_FILE.exists():
        tell("TalentLens has no recorded server process. Your database and resumes are unchanged.")
        return
    pid = PID_FILE.read_text(encoding="ascii").strip()
    if not pid.isdigit():
        PID_FILE.unlink(missing_ok=True)
        tell("The saved server record was invalid. Your project data is unchanged.")
        return
    check = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command",
                            f"(Get-CimInstance Win32_Process -Filter 'ProcessId={pid}').CommandLine"],
                           capture_output=True, text=True, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    command = check.stdout.lower()
    if check.returncode == 0 and "uvicorn" in command and "backend.main:app" in command:
        subprocess.run(["taskkill", "/PID", pid, "/T", "/F"], capture_output=True,
                       creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
        PID_FILE.unlink(missing_ok=True)
        tell("TalentLens has stopped. Your database and uploaded resumes are saved.")
    else:
        PID_FILE.unlink(missing_ok=True)
        tell("The saved server process is no longer running. Your database and resumes are unchanged.")


if __name__ == "__main__":
    main()
