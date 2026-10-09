#!/usr/bin/env python3
"""Apply equal-length rusda fingerprint changes to a thin 64-bit Mach-O.

Run before codesign. This intentionally leaves protocol identifiers intact.
"""

from pathlib import Path
import struct
import sys


MAGIC_64_LE = b"\xcf\xfa\xed\xfe"
LC_SEGMENT_64 = 0x19
STRING_SECTIONS = {"__cstring", "__const"}

STRING_PATCHES = {
    b"FridaScriptEngine": b"enignEtpircSadirF",
    b"GLib-GIO": b"OIG-biLG",
    b"GDBusProxy": b"yxorPsuBDG",
    b"GumScript": b"tpircSmuG",
    b"gum-js-loop": b"russellloop",
    b"gmain": b"rmain",
    b"gdbus": b"rubus",
}

WHOLE_FILE_PATCHES = {
    b"frida_agent_main": b"rusda_agent_main",
    b"libfrida-gadget-raw": b"librusda-gadget-raw",
    b"libfrida-agent-raw": b"librusda-agent-raw",
}


def name_at(data: bytes, offset: int) -> str:
    return data[offset:offset + 16].split(b"\0", 1)[0].decode("ascii")


def ranges(data: bytes) -> tuple[list[tuple[str, int, int]], tuple[int, int] | None]:
    if data[:4] != MAGIC_64_LE:
        raise ValueError("Expected a thin little-endian 64-bit Mach-O")
    if len(data) < 32:
        raise ValueError("Truncated Mach-O header")

    ncmds, sizeofcmds = struct.unpack_from("<II", data, 16)
    if 32 + sizeofcmds > len(data):
        raise ValueError("Truncated Mach-O load commands")
    sections = []
    linkedit = None
    cursor = 32
    for _ in range(ncmds):
        cmd, cmdsize = struct.unpack_from("<II", data, cursor)
        if cmdsize < 8 or cursor + cmdsize > 32 + sizeofcmds:
            raise ValueError("Invalid Mach-O load command")
        if cmd == LC_SEGMENT_64:
            if cmdsize < 72:
                raise ValueError("Invalid Mach-O segment")
            segment = name_at(data, cursor + 8)
            fileoff, filesize = struct.unpack_from("<QQ", data, cursor + 40)
            nsects = struct.unpack_from("<I", data, cursor + 64)[0]
            if cmdsize < 72 + 80 * nsects:
                raise ValueError("Truncated Mach-O sections")
            if segment == "__LINKEDIT" and filesize:
                linkedit = (fileoff, fileoff + filesize)
            for i in range(nsects):
                section_cursor = cursor + 72 + 80 * i
                section = name_at(data, section_cursor)
                size = struct.unpack_from("<Q", data, section_cursor + 40)[0]
                offset = struct.unpack_from("<I", data, section_cursor + 48)[0]
                if section in STRING_SECTIONS and size:
                    sections.append((section, offset, offset + size))
        cursor += cmdsize

    for _, start, end in sections:
        if end > len(data):
            raise ValueError("Mach-O section extends past file")
    if linkedit is not None and linkedit[1] > len(data):
        raise ValueError("Mach-O LINKEDIT extends past file")
    if not sections:
        raise ValueError("No Mach-O string sections found")
    return sections, linkedit


def patch(path: Path) -> None:
    data = bytearray(path.read_bytes())
    sections, linkedit = ranges(data)
    counts = {old.decode("ascii"): 0 for old in (*STRING_PATCHES, *WHOLE_FILE_PATCHES)}

    for _, start, end in sections:
        content = bytes(data[start:end])
        for old, new in STRING_PATCHES.items():
            if len(old) != len(new):
                raise ValueError(f"Non-equal-length patch: {old!r}")
            counts[old.decode("ascii")] += content.count(old)
            content = content.replace(old, new)
        data[start:end] = content

    for old, new in WHOLE_FILE_PATCHES.items():
        if len(old) != len(new):
            raise ValueError(f"Non-equal-length patch: {old!r}")
        counts[old.decode("ascii")] += data.count(old)
        data[:] = data.replace(old, new)

    if linkedit is not None:
        start, end = linkedit
        content = bytes(data[start:end]).replace(b"frida", b"rusda").replace(b"FRIDA", b"RUSDA")
        data[start:end] = content

    path.write_bytes(data)
    print(f"[*] Mach-O rusda patch: {path}: " + ", ".join(f"{key}={value}" for key, value in counts.items()))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: topatch-macho.py FILE")
    patch(Path(sys.argv[1]))
