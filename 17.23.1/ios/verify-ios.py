#!/usr/bin/env python3
"""Check Rusda iOS artifacts after Mach-O patching and signing."""

from pathlib import Path
import subprocess
import sys


BAD = (
    b"FridaScriptEngine",
    b"GLib-GIO",
    b"GDBusProxy",
    b"GumScript",
    b"gum-js-loop",
    b"gmain",
    b"gdbus",
    b"frida_agent_main",
)
GOOD = (
    b"enignEtpircSadirF",
    b"OIG-biLG",
    b"yxorPsuBDG",
    b"tpircSmuG",
    b"russellloop",
    b"rmain",
    b"rubus",
    b"rusda_agent_main",
)


def main(root: Path) -> int:
    files = [
        root / "dist-ios/bin/rusda-server",
        root / "dist-ios/bin/rusda-inject",
        root / "dist-ios/lib/rusda-1.0/rusda-gadget.dylib",
        root / "build-ios-arm64/subprojects/frida-core/lib/agent/rusda-agent.dylib",
        root / "build-ios-arm64/subprojects/frida-core/compat/arch-support.bundle.p/arm64e/lib/agent/rusda-agent.dylib",
    ]
    failed = False
    for path in files:
        if not path.is_file():
            print(f"FAIL missing: {path}")
            failed = True
            continue
        data = path.read_bytes()
        bad = [x.decode() for x in BAD if x in data]
        good = [x.decode() for x in GOOD if x in data]
        signature = subprocess.run(["codesign", "--verify", str(path)], capture_output=True)
        arch = subprocess.run(["xcrun", "lipo", "-info", str(path)], capture_output=True, text=True)
        ok = not bad and signature.returncode == 0 and arch.returncode == 0
        failed |= not ok
        print(f"{'PASS' if ok else 'FAIL'} {path.name} {len(data)} bytes")
        print(f"  architecture: {arch.stdout.strip()}")
        print(f"  patched markers: {', '.join(good)}")
        if bad:
            print(f"  unpatched markers: {', '.join(bad)}")
        if signature.returncode:
            print(f"  codesign: {signature.stderr.decode(errors='replace').strip()}")
    return 1 if failed else 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: verify-ios.py FRIDA_SOURCE_ROOT")
    raise SystemExit(main(Path(sys.argv[1])))
