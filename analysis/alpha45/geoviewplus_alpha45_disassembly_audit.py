#!/usr/bin/env python3
"""GeoViewPlus 0.5 Alpha45: audit Alpha44 MOV SI,imm16 candidates with GNU objdump.

This is a linear-sweep diagnostic, NOT a full GEOS 1.x code/resource parser.
Requires Python 3.10+ and GNU objdump with i8086 support.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, shutil, subprocess, tempfile, zipfile
from pathlib import Path

SOURCE_FILES = (
    "GEOWORKS/WORLD/WRITE.GEO",
    "GEOWORKS/WORLD/PROGRAMM.E/WRITE.GEO",
)
R11_BASE = 0x9B22
R11_SIZE = 0x066C
HANDLES = tuple(range(0x26, 0x38, 2))
LINE_RE = re.compile(r"^\s*([0-9a-fA-F]+):\s*((?:[0-9a-fA-F]{2}\s+)+)\s*([a-zA-Z][a-zA-Z0-9.]*)\s*(.*?)\s*$")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def find_all(data: bytes, needle: bytes) -> list[int]:
    out, pos = [], 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1

def disassemble_linear(blob: bytes, objdump: str) -> dict[int, dict]:
    with tempfile.NamedTemporaryFile(prefix="geoviewplus_alpha45_", suffix=".bin") as f:
        f.write(blob); f.flush()
        cmd = [objdump, "-D", "-b", "binary", "-m", "i8086", "-Mintel", f.name]
        p = subprocess.run(cmd, check=True, capture_output=True, text=True, errors="replace")
    ins = {}
    for line in p.stdout.splitlines():
        m = LINE_RE.match(line)
        if not m:
            continue
        off = int(m.group(1), 16)
        raw = bytes.fromhex(m.group(2))
        ins[off] = {"offset": off, "bytes": raw, "mnemonic": m.group(3).lower(), "operands": m.group(4)}
    if not ins:
        raise RuntimeError("objdump output could not be parsed")
    return ins

def analyze(archive: Path, out: Path, objdump: str = "objdump") -> dict:
    out.mkdir(parents=True, exist_ok=True)
    if shutil.which(objdump) is None:
        raise RuntimeError(f"GNU objdump not found: {objdump}")
    with zipfile.ZipFile(archive) as zf:
        bad = zf.testzip()
        if bad:
            raise ValueError(f"ZIP CRC error in {bad}")
        names = set(zf.namelist())
        missing = [p for p in SOURCE_FILES if p not in names]
        if missing:
            raise ValueError(f"Missing source files: {missing}")
        blobs = [zf.read(p) for p in SOURCE_FILES]
    if len(blobs[0]) != len(blobs[1]):
        raise ValueError("WRITE.GEO variants have different lengths")
    a, b = blobs
    if a[R11_BASE:R11_BASE+R11_SIZE] != b[R11_BASE:R11_BASE+R11_SIZE]:
        raise ValueError("R11 differs between WRITE.GEO variants")

    # Full-file linear sweep is diagnostic only: GEO files mix code and data.
    ins_a = disassemble_linear(a, objdump)
    ins_b = disassemble_linear(b, objdump)
    hits_a = {h: find_all(a, b"\xBE" + h.to_bytes(2, "little")) for h in HANDLES}
    hits_b = {h: find_all(b, b"\xBE" + h.to_bytes(2, "little")) for h in HANDLES}
    rows = []
    for h in HANDLES:
        for pos in hits_a[h]:
            ia, ib = ins_a.get(pos), ins_b.get(pos)
            mov_a = bool(ia and ia["mnemonic"] == "mov" and re.search(r"\bsi\s*,\s*0x0*%x\b" % h, ia["operands"], re.I))
            mov_b = bool(ib and ib["mnemonic"] == "mov" and re.search(r"\bsi\s*,\s*0x0*%x\b" % h, ib["operands"], re.I))
            following = []
            if ia:
                for item in [ins_a[k] for k in sorted(ins_a) if k >= pos][:7]:
                    following.append(f"{item['offset']:05X}: {item['bytes'].hex(' ').upper()} {item['mnemonic']} {item['operands']}".strip())
            rows.append({
                "chunk_handle_candidate": f"0x{h:04X}",
                "file_offset": f"0x{pos:05X}",
                "opcode_bytes": a[pos:pos+3].hex(" ").upper(),
                "linear_sweep_instruction_start": bool(ia),
                "linear_sweep_decodes_mov_si_same_immediate": mov_a,
                "linear_sweep_mnemonic": ia["mnemonic"] if ia else "",
                "linear_sweep_operands": ia["operands"] if ia else "",
                "second_variant_instruction_start": bool(ib),
                "second_variant_decodes_mov_si_same_immediate": mov_b,
                "second_variant_operands": ib["operands"] if ib else "",
                "same_instruction_decode_in_both_variants": bool(ia and ib and ia["bytes"] == ib["bytes"] and ia["mnemonic"] == ib["mnemonic"] and ia["operands"] == ib["operands"]),
                "next_7_linear_instructions": " | ".join(following),
                "before_8_bytes": a[max(0,pos-8):pos].hex(" ").upper(),
                "after_20_bytes": a[pos+3:pos+23].hex(" ").upper(),
                "outside_R11": not (R11_BASE <= pos < R11_BASE+R11_SIZE),
            })
    rows.sort(key=lambda r: int(r["file_offset"], 16))
    with (out/"GEO_alpha45_instruction_contexts.csv").open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    counts_a = {f"0x{h:04X}": len(hits_a[h]) for h in HANDLES}
    counts_b = {f"0x{h:04X}": len(hits_b[h]) for h in HANDLES}
    summary = {
        "archive": archive.name,
        "zip_crc_ok": True,
        "archive_members": len(names),
        "source_files": list(SOURCE_FILES),
        "write_geo_size": len(a),
        "write_geo_sha256": {SOURCE_FILES[0]: sha256(a), SOURCE_FILES[1]: sha256(b)},
        "r11_file_offset": f"0x{R11_BASE:04X}",
        "r11_size": R11_SIZE,
        "r11_identical_between_variants": True,
        "target_handles": [f"0x{x:04X}" for x in HANDLES],
        "candidate_counts_first_variant": counts_a,
        "candidate_counts_second_variant": counts_b,
        "candidate_total_first_variant": sum(counts_a.values()),
        "candidate_total_second_variant": sum(counts_b.values()),
        "candidate_offsets_identical_between_variants": all(hits_a[h] == hits_b[h] for h in HANDLES),
        "objdump_linear_sweep_instruction_starts": sum(1 for r in rows if r["linear_sweep_instruction_start"]),
        "objdump_linear_sweep_mov_si_matches": sum(1 for r in rows if r["linear_sweep_decodes_mov_si_same_immediate"]),
        "second_variant_linear_sweep_instruction_starts": sum(1 for r in rows if r["second_variant_instruction_start"]),
        "second_variant_linear_sweep_mov_si_matches": sum(1 for r in rows if r["second_variant_decodes_mov_si_same_immediate"]),
        "same_instruction_decode_both_variants": sum(1 for r in rows if r["same_instruction_decode_in_both_variants"]),
        "all_candidates_outside_r11": all(r["outside_R11"] for r in rows),
        "disassembler": subprocess.run([objdump, "--version"], capture_output=True, text=True).stdout.splitlines()[0],
        "method_limit": "GNU objdump was run as a linear sweep from file offset 0 over the entire GEO file. A GEOS GEO file mixes headers, resource tables, code and data; this is not a substitute for parsing code/resource boundaries and valid entry points. Candidate instruction starts remain provisional.",
        "next_validation": "Identify code-bearing resources and entry points, then disassemble from valid entry points and verify control flow and handle resolution."
    }
    (out/"GEO_alpha45_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return summary

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("--out", type=Path, default=Path("alpha45_output"))
    p.add_argument("--objdump", default="objdump")
    a = p.parse_args()
    print(json.dumps(analyze(a.archive, a.out, a.objdump), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
