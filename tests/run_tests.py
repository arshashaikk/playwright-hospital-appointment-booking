"""Test runner: starts its own servers, runs the Behave suite, stops the servers.

  python run_tests.py                      # clean app, every scenario  -> expect all PASS
  python run_tests.py --bug wrong_doctor   # inject a bug, run only scenarios tagged for it
                                           #   -> expect FAILURES (bug detected)
  python run_tests.py --all-bugs           # inject each of the 4 bugs in turn, print a summary
  python run_tests.py --tags smoke         # behave tag filter on a clean app
  python run_tests.py --headed --slowmo 300
  python run_tests.py -- features/booking_flow.feature     # anything after -- goes to behave

By default the runner uses its OWN ports (backend 8100, frontend 5273), so it never collides with
the dev servers you run on 8000 / 5173. Use --use-running to test those instead (clean runs only).
"""
import argparse
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent
BUGS = ["double_book", "weak_phone", "wrong_doctor", "duplicate_submit"]
IS_WIN = os.name == "nt"

# set in main()
BACKEND_PORT = 8100
FRONTEND_PORT = 5273
STARTED_BY_US = True


def backend_url() -> str:
    return f"http://127.0.0.1:{BACKEND_PORT}"


def frontend_url() -> str:
    return f"http://localhost:{FRONTEND_PORT}"


def up(url: str) -> bool:
    try:
        urllib.request.urlopen(url, timeout=2)
        return True
    except Exception:  # noqa: BLE001
        return False


def active_bugs() -> set[str] | None:
    try:
        with urllib.request.urlopen(f"{backend_url()}/api/health", timeout=2) as r:
            return set(json.load(r)["bugs"])
    except Exception:  # noqa: BLE001
        return None


def wait_for(url: str, name: str, timeout: int = 60) -> None:
    end = time.time() + timeout
    while time.time() < end:
        if up(url):
            return
        time.sleep(0.5)
    raise SystemExit(f"{name} did not start within {timeout}s")


def kill(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if IS_WIN:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True)
    else:
        proc.terminate()


def backend_python() -> str:
    for rel in ("Scripts/python.exe", "bin/python"):
        p = PROJECT / "backend" / ".venv" / rel
        if p.exists():
            return str(p)
    raise SystemExit("backend/.venv not found - create it and install backend/requirements.txt")


def start_backend(bugs: set[str]) -> subprocess.Popen | None:
    current = active_bugs()
    if current is not None:
        if current == bugs:
            print(f"[runner] reusing backend on :{BACKEND_PORT} (bugs: {sorted(bugs) or 'none'})")
            return None
        raise SystemExit(
            f"Backend on :{BACKEND_PORT} runs with bugs={sorted(current)} but {sorted(bugs)} are needed. "
            "Stop it and run again (or drop --use-running)."
        )
    env = {**os.environ, "BUGS": ",".join(sorted(bugs))}
    print(f"[runner] starting backend on :{BACKEND_PORT} (bugs: {sorted(bugs) or 'none'})")
    proc = subprocess.Popen(
        [backend_python(), "-m", "uvicorn", "app.main:app", "--port", str(BACKEND_PORT)],
        cwd=PROJECT / "backend", env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    wait_for(f"{backend_url()}/api/health", "backend")
    return proc


def start_frontend() -> subprocess.Popen | None:
    if up(frontend_url()):
        print(f"[runner] reusing frontend on :{FRONTEND_PORT}")
        return None
    print(f"[runner] starting frontend on :{FRONTEND_PORT}")
    env = {**os.environ, "PORT": str(FRONTEND_PORT), "API_TARGET": backend_url()}
    proc = subprocess.Popen(
        "npm run dev", cwd=PROJECT / "frontend", shell=True, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    wait_for(frontend_url(), "frontend")
    return proc


def run_behave(tag: str | None, extra: list[str], headed: bool, slowmo: int) -> int:
    cmd = [sys.executable, "-m", "behave", "--no-skipped"]
    if tag:
        cmd.append(f"--tags=@{tag}")
    if headed:
        cmd += ["-D", "headed=true"]
    if slowmo:
        cmd += ["-D", f"slowmo={slowmo}"]
    cmd += extra
    env = {**os.environ, "BASE_URL": frontend_url(), "API_URL": backend_url()}
    return subprocess.run(cmd, cwd=ROOT, env=env).returncode


def main() -> int:
    global BACKEND_PORT, FRONTEND_PORT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bug", choices=BUGS, help="inject one bug and run only scenarios tagged for it")
    ap.add_argument("--all-bugs", action="store_true", help="inject each bug in turn")
    ap.add_argument("--tags", help="behave tag to filter on (clean run only), e.g. smoke")
    ap.add_argument("--use-running", action="store_true", help="test the dev servers on 8000/5173")
    ap.add_argument("--headed", action="store_true")
    ap.add_argument("--slowmo", type=int, default=0)
    ap.add_argument("behave_args", nargs="*", help="extra behave args (after --)")
    args = ap.parse_args()

    if args.use_running:
        BACKEND_PORT, FRONTEND_PORT = 8000, 5173
        if args.bug or args.all_bugs:
            print("[runner] note: bug runs need to restart the backend; stop your dev backend first.")

    procs: list[subprocess.Popen] = []
    try:
        if args.all_bugs:
            summary = {}
            frontend = start_frontend()
            procs += [frontend] if frontend else []
            for bug in BUGS:
                backend = start_backend({bug})
                code = run_behave(bug, args.behave_args, args.headed, args.slowmo)
                summary[bug] = "DETECTED" if code != 0 else "NOT DETECTED"
                if backend:
                    kill(backend)
                    time.sleep(1)
            print("\n===== Bug detection summary =====")
            for bug, verdict in summary.items():
                print(f"  {bug:<18} {verdict}")
            return 0 if all(v == "DETECTED" for v in summary.values()) else 1

        backend = start_backend({args.bug} if args.bug else set())
        procs += [backend] if backend else []
        frontend = start_frontend()
        procs += [frontend] if frontend else []
        code = run_behave(args.bug or args.tags, args.behave_args, args.headed, args.slowmo)
        if args.bug:
            print(f"\n[runner] bug '{args.bug}': {'DETECTED (tests failed as expected)' if code else 'NOT DETECTED'}")
            return 0 if code else 1
        return code
    finally:
        for p in procs:
            kill(p)


if __name__ == "__main__":
    sys.exit(main())
