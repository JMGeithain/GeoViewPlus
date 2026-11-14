#!/usr/bin/env python3
"""GeoViewPlus 0.5 Alpha46: parse GeoWorks 1.x geode resources and R11 references.

This parser implements only the version-1 branch documented by GeoDump:
GEOS file header magic at offset 0, additional geode header at 0xC0,
then libraries, exports, and the four segment descriptor arrays.

GNU objdump is used only to decode individual HAF_CODE resources in 8086 mode.
Its resource-local linear sweep is still not a control-flow proof.
"""
from __future__ import annotations
import argparse, csv, hashlib, json, re, shutil, subprocess, tempfile, zipfile
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_FILES = (
    "GEOWORKS/WORLD/WRITE.GEO",
    "GEOWORKS/WORLD/PROGRAMM.E/WRITE.GEO",
)
GEOS_ID = 0x53CF45C7
APP_HEADER_OFFSET = 0xC0
APP_HEADER_SIZE = 0x60
LIB_ENTRY_SIZE = 14
EXPORT_ENTRY_SIZE = 4
TARGET_HANDLES = tuple(range(0x26, 0x38, 2))
R11_SEGMENT = 11

HAF_FLAGS = {
    0x80: "ZERO_INIT", 0x40: "LOCK", 0x20: "NO_ERR", 0x10: "UI",
    0x08: "READ_ONLY", 0x04: "OBJECT_RESOURCE", 0x02: "CODE",
    0x01: "CONFORMING",
}
HF_FLAGS = {
    0x80: "FIXED", 0x40: "SHARABLE", 0x20: "DISCARDABLE", 0x10: "SWAPABLE",
    0x08: "LMEM", 0x04: "DEBUG", 0x02: "DISCARDED", 0x01: "SWAPPED",
}
INSN_RE = re.compile(r"^\s*([0-9a-fA-F]+):\s*((?:[0-9a-fA-F]{2}\s+)+)\s*([a-zA-Z][\w.]*)\s*(.*?)\s*$")

def u16(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset+2], "little")

def u32(data: bytes, offset: int) -> int:
    return int.from_bytes(data[offset:offset+4], "little")

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def find_all(data: bytes, needle: bytes) -> list[int]:
    result, pos = [], 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            return result
        result.append(pos)
        pos += 1

def flag_names(value: int, masks: dict[int, str]) -> list[str]:
    return [name for bit, name in masks.items() if value & bit]

def disassemble_resource(data: bytes, objdump: str) -> tuple[dict[int, dict], list[int]]:
    """Linear-sweep one resource from its own offset zero, not from file offset."""
    with tempfile.NamedTemporaryFile(prefix="gvp_a46_", suffix=".bin") as f:
        f.write(data)
        f.flush()
        cmd = [objdump, "-D", "-b", "binary", "-m", "i8086", "-Mintel", f.name]
        proc = subprocess.run(cmd, check=True, capture_output=True, text=True, errors="replace")
    instructions: dict[int, dict] = {}
    order: list[int] = []
    for line in proc.stdout.splitlines():
        m = INSN_RE.match(line)
        if not m:
            continue
        off = int(m.group(1), 16)
        raw = bytes.fromhex(m.group(2))
        instructions[off] = {
            "offset": off,
            "bytes": raw,
            "mnemonic": m.group(3).lower(),
            "operands": m.group(4).strip(),
        }
        order.append(off)
    if not instructions:
        raise RuntimeError("objdump produced no parseable instructions for a code resource")
    return instructions, order

def parse_geode(data: bytes) -> dict:
    if len(data) < APP_HEADER_OFFSET + APP_HEADER_SIZE:
        raise ValueError("GEO file too short for version-1 geode header")
    if u32(data, 0) != GEOS_ID:
        raise ValueError("Not a GeoWorks 1.x GEOS file header (magic mismatch)")
    if u16(data, 4) != 0:
        raise ValueError("Version-1 file header class is not executable/application")

    h = APP_HEADER_OFFSET
    app = {
        "legacy_numseg": u16(data, h + 0x10),
        "legacy_numlib": u16(data, h + 0x12),
        "legacy_numexp": u16(data, h + 0x14),
        "stack_size": u16(data, h + 0x16),
        "x2_offset": u16(data, h + 0x18),
        "x2_segment": u16(data, h + 0x1A),
        "token_resource_item": u16(data, h + 0x1C),
        "token_resource_segment": u16(data, h + 0x1E),
        "attributes": u16(data, h + 0x22),
        "type": u16(data, h + 0x24),
        "kernel_protocol_version": u16(data, h + 0x0C),
        "kernel_protocol_revision": u16(data, h + 0x0E),
        "permanent_name": data[h + 0x34:h + 0x3C].decode("ascii", "replace").rstrip(" \0"),
        "permanent_extension": data[h + 0x3C:h + 0x40].decode("ascii", "replace").rstrip(" \0"),
        "numexp": u16(data, h + 0x52),
        "numlib": u16(data, h + 0x54),
        "numseg": u16(data, h + 0x58),
    }
    if (app["legacy_numseg"], app["legacy_numlib"], app["legacy_numexp"]) != (app["numseg"], app["numlib"], app["numexp"]):
        raise ValueError("Legacy and current duplicate counts in the geode header disagree")
    if app["type"] != 1:
        raise ValueError(f"Expected application geode type 1, got {app['type']}")

    numseg, numlib, numexp = app["numseg"], app["numlib"], app["numexp"]
    lib_start = h + APP_HEADER_SIZE
    export_start = lib_start + numlib * LIB_ENTRY_SIZE
    seg_table_start = export_start + numexp * EXPORT_ENTRY_SIZE
    len_start = seg_table_start
    pos_start = len_start + numseg * 2
    fixlen_start = pos_start + numseg * 4
    flags_start = fixlen_start + numseg * 2
    table_end = flags_start + numseg * 2
    if table_end > len(data):
        raise ValueError("Segment descriptor arrays extend beyond file")

    libraries = []
    for i in range(numlib):
        p = lib_start + i * LIB_ENTRY_SIZE
        libraries.append({
            "index": i,
            "name": data[p:p+8].decode("ascii", "replace").rstrip(" \0"),
            "type": u16(data, p+8),
            "protocol_version": u16(data, p+10),
            "protocol_revision": u16(data, p+12),
        })

    exports = []
    for i in range(numexp):
        p = export_start + i * EXPORT_ENTRY_SIZE
        exports.append({"ordinal": i, "offset": u16(data, p), "segment": u16(data, p+2)})

    segments = []
    for i in range(numseg):
        length = u16(data, len_start + i*2)
        file_pos = u32(data, pos_start + i*4)
        fixlen = u16(data, fixlen_start + i*2)
        flags = u16(data, flags_start + i*2)
        aligned_len = (length + 0x0F) & ~0x0F
        fixup_pos = file_pos + aligned_len
        if fixlen % 4:
            raise ValueError(f"Segment {i}: fixup length {fixlen:#x} is not a multiple of 4")
        if file_pos > len(data) or file_pos + length > len(data) or fixup_pos + fixlen > len(data):
            raise ValueError(f"Segment {i}: data/fixup range outside file")
        haf, hf = (flags >> 8) & 0xFF, flags & 0xFF
        segments.append({
            "index": i,
            "length": length,
            "file_offset": file_pos,
            "fixup_length": fixlen,
            "fixup_offset": fixup_pos,
            "fixup_count": fixlen // 4,
            "flags": flags,
            "haf_byte": haf,
            "hf_byte": hf,
            "haf_names": flag_names(haf, HAF_FLAGS),
            "hf_names": flag_names(hf, HF_FLAGS),
            "is_code": bool(haf & 0x02),
            "is_lmem": bool(hf & 0x08),
        })

    ranges = sorted((s["file_offset"], s["fixup_offset"] + s["fixup_length"], s["index"])
                    for s in segments if s["length"] or s["fixup_length"])
    for left, right in zip(ranges, ranges[1:]):
        if left[1] > right[0]:
            raise ValueError(f"Segment storage overlap: {left[2]} and {right[2]}")

    return {
        "app": app,
        "libraries": libraries,
        "exports": exports,
        "segment_table": {
            "start": seg_table_start,
            "length_array_start": len_start,
            "position_array_start": pos_start,
            "fixup_length_array_start": fixlen_start,
            "flags_array_start": flags_start,
            "end": table_end,
        },
        "segments": segments,
    }

def analyze(archive: Path, out: Path, objdump: str = "objdump") -> dict:
    archive, out = Path(archive), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if shutil.which(objdump) is None:
        raise RuntimeError(f"GNU objdump not found: {objdump}")
    with zipfile.ZipFile(archive) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise ValueError(f"ZIP CRC failure: {bad}")
        names = set(zf.namelist())
        missing = [p for p in SOURCE_FILES if p not in names]
        if missing:
            raise ValueError(f"Missing source file(s): {missing}")
        a, b = (zf.read(p) for p in SOURCE_FILES)
        kernel = zf.read("GEOWORKS/KERNEL.EXE") if "GEOWORKS/KERNEL.EXE" in names else b""

    parsed_a, parsed_b = parse_geode(a), parse_geode(b)
    if parsed_a["segment_table"] != parsed_b["segment_table"]:
        raise ValueError("Segment descriptor table differs between WRITE.GEO variants")
    if parsed_a["segments"] != parsed_b["segments"]:
        raise ValueError("Parsed segment descriptors differ between WRITE.GEO variants")
    if len(a) != len(b):
        raise ValueError("WRITE.GEO variants have different file lengths")

    segs = parsed_a["segments"]
    segment_bytes = {s["index"]: a[s["file_offset"]:s["file_offset"]+s["length"]]
                     for s in segs if s["length"]}
    instructions: dict[int, dict[int, dict]] = {}
    instruction_order: dict[int, list[int]] = {}
    for s in segs:
        if s["is_code"] and s["length"]:
            instructions[s["index"]], instruction_order[s["index"]] = disassemble_resource(segment_bytes[s["index"]], objdump)

    fixups_by_segment: dict[int, list[dict]] = {}
    for s in segs:
        entries = []
        for j in range(s["fixup_count"]):
            p = s["fixup_offset"] + j*4
            entries.append({"type": u16(a, p), "offset": u16(a, p+2)})
        fixups_by_segment[s["index"]] = entries

    candidate_rows = []
    candidates_by_segment: dict[int, list[tuple[int,int,int]]] = defaultdict(list)
    for handle in TARGET_HANDLES:
        needle = b"\xBE" + handle.to_bytes(2, "little")
        hits_a = find_all(a, needle)
        hits_b = find_all(b, needle)
        if hits_a != hits_b:
            raise ValueError(f"Candidate offsets for handle {handle:#x} differ between variants")
        for file_off in hits_a:
            containing = [s for s in segs if s["length"] and s["file_offset"] <= file_off < s["file_offset"] + s["length"]]
            if len(containing) != 1:
                seg_index = None
                rel = None
                inst = None
                decode_ok = False
                seg_flags = ""
                seq = []
                flow = None
                flow_fixups = []
            else:
                s = containing[0]
                seg_index = s["index"]
                rel = file_off - s["file_offset"]
                inst_map = instructions.get(seg_index, {})
                order = instruction_order.get(seg_index, [])
                inst = inst_map.get(rel)
                decode_ok = bool(inst and inst["mnemonic"] == "mov" and re.search(
                    r"\bsi\s*,\s*0x0*%x\b" % handle, inst["operands"], re.I))
                seg_flags = f"0x{s['flags']:04X}"
                seq = []
                if rel in inst_map:
                    idx = order.index(rel)
                    seq = [inst_map[x] for x in order[idx:idx+7]]
                flow = next((x for x in seq[1:5] if x["mnemonic"] in ("call", "jmp", "lcall", "ljmp")), None)
                flow_fixups = []
                if flow and flow["bytes"] and flow["bytes"][0] in (0x9A, 0xEA):
                    f_by_offset = {x["offset"]: x["type"] for x in fixups_by_segment.get(seg_index, [])}
                    for operand_off in (flow["offset"]+1, flow["offset"]+3):
                        if operand_off in f_by_offset:
                            flow_fixups.append({"offset": operand_off, "type": f_by_offset[operand_off]})
            candidates_by_segment[seg_index].append((rel if rel is not None else -1, handle, file_off))
            seq_text = " | ".join(
                f"{x['offset']:04X}: {x['bytes'].hex(' ').upper()} {x['mnemonic']} {x['operands']}".strip()
                for x in seq
            )
            flow_kind = ""
            if flow:
                op = flow["bytes"][0] if flow["bytes"] else -1
                flow_kind = ("far_" if op in (0x9A, 0xEA) else "near_") + flow["mnemonic"]
            candidate_rows.append({
                "file_offset": f"0x{file_off:05X}",
                "segment": seg_index,
                "segment_file_base": f"0x{containing[0]['file_offset']:05X}" if len(containing)==1 else "",
                "segment_relative_offset": f"0x{rel:04X}" if rel is not None else "",
                "segment_flags": seg_flags,
                "chunk_handle": f"0x{handle:04X}",
                "instruction_start_in_resource_sweep": bool(inst),
                "decodes_mov_si_expected_handle": decode_ok,
                "instruction_bytes": inst["bytes"].hex(" ").upper() if inst else "",
                "mnemonic": inst["mnemonic"] if inst else "",
                "operands": inst["operands"] if inst else "",
                "first_control_flow_within_next_4_instructions": flow_kind,
                "control_flow_operands": flow["operands"] if flow else "",
                "control_flow_bytes": flow["bytes"].hex(" ").upper() if flow else "",
                "control_flow_fixups_raw": ";".join(f"{x['offset']:04X}:type={x['type']:04X}" for x in flow_fixups),
                "next_7_resource_local_instructions": seq_text,
            })

    candidate_rows.sort(key=lambda x: int(x["file_offset"], 16))

    pointer_rows = []
    seg1 = segs[1]
    seg1_data = segment_bytes.get(1, b"")
    for fx in fixups_by_segment[1]:
        if fx["type"] != 0x22:
            continue
        seg_word_off = fx["offset"]
        if seg_word_off < 2 or seg_word_off + 2 > len(seg1_data):
            raise ValueError(f"Segment 1 program-segment fixup outside resource at {seg_word_off:#x}")
        target_segment = u16(seg1_data, seg_word_off)
        target_offset = u16(seg1_data, seg_word_off-2)
        target = segs[target_segment] if target_segment < len(segs) else None
        target_in_bounds = bool(target and target["length"] and target_offset < target["length"])
        target_is_code = bool(target and target["is_code"])
        target_instruction = bool(target_is_code and target_offset in instructions.get(target_segment, {}))
        pointer_rows.append({
            "source_segment": 1,
            "source_segment_relative_fixup_offset": f"0x{seg_word_off:04X}",
            "fixup_type_raw": "0x0022",
            "target_offset_word_location": f"0x{seg_word_off-2:04X}",
            "target_offset": f"0x{target_offset:04X}",
            "target_segment": target_segment,
            "target_segment_file_base": f"0x{target['file_offset']:05X}" if target else "",
            "target_segment_length": f"0x{target['length']:04X}" if target else "",
            "target_within_segment_bounds": target_in_bounds,
            "target_segment_has_code_flag": target_is_code,
            "target_is_instruction_start_in_resource_sweep": target_instruction,
            "target_instruction_bytes": instructions[target_segment][target_offset]["bytes"].hex(" ").upper() if target_instruction else "",
            "target_instruction": (instructions[target_segment][target_offset]["mnemonic"] + " " + instructions[target_segment][target_offset]["operands"]).strip() if target_instruction else "",
        })

    r11 = segs[R11_SEGMENT]
    r11_data = segment_bytes[R11_SEGMENT]
    if not r11["is_lmem"]:
        raise ValueError("R11 target segment does not carry the LMem flag")
    lmem = {
        "segment_number": u16(r11_data, 0),
        "handle_list_offset": u16(r11_data, 2),
        "flags": u16(r11_data, 4),
        "type": u16(r11_data, 6),
        "block_size_field": u16(r11_data, 8),
        "handle_count": u16(r11_data, 10),
        "free_offset": u16(r11_data, 12),
        "free_size": u16(r11_data, 14),
    }
    handle_values = [u16(r11_data, lmem["handle_list_offset"] + 2*i) for i in range(lmem["handle_count"])]
    if lmem["segment_number"] != R11_SEGMENT or lmem["handle_list_offset"] != 0x10 or lmem["handle_count"] != 20:
        raise ValueError("R11 LMem header does not match the previously established 20-handle structure")
    if [handle_values[i] for i in range(11, 20)] != [0x03E2 + 0x44*i for i in range(9)]:
        raise ValueError("R11 handle entries 0x26..0x36 no longer match Alpha42 resource offsets")

    candidate_by_seg = Counter(str(r["segment"]) for r in candidate_rows)
    candidate_flow = Counter(r["first_control_flow_within_next_4_instructions"] or "none_in_next_4" for r in candidate_rows)
    pointer_by_target = Counter(str(r["target_segment"]) for r in pointer_rows)
    pointer_boundary = Counter((str(r["target_segment"]), bool(r["target_is_instruction_start_in_resource_sweep"])) for r in pointer_rows)
    near_targets = Counter()
    near_targets_resolved = 0
    for row in candidate_rows:
        if row["first_control_flow_within_next_4_instructions"] in ("near_call", "near_jmp"):
            m = re.search(r"0x([0-9a-fA-F]+)", row["control_flow_operands"])
            if m:
                target_off = int(m.group(1), 16)
                seg_index = row["segment"]
                near_targets[f"SEG{seg_index}:0x{target_off:04X}"] += 1
                if target_off in instructions.get(seg_index, {}):
                    near_targets_resolved += 1

    segment_rows = []
    for s in segs:
        segment_rows.append({
            "segment": s["index"],
            "file_offset": f"0x{s['file_offset']:05X}",
            "length": f"0x{s['length']:04X}",
            "fixup_offset": f"0x{s['fixup_offset']:05X}",
            "fixup_length": f"0x{s['fixup_length']:04X}",
            "fixup_count": s["fixup_count"],
            "flags": f"0x{s['flags']:04X}",
            "HAF_flags": ",".join(s["haf_names"]),
            "HF_flags": ",".join(s["hf_names"]),
            "is_code": s["is_code"],
            "is_lmem": s["is_lmem"],
            "candidate_count": candidate_by_seg.get(str(s["index"]), 0),
        })

    def write_csv(name: str, rows: list[dict]):
        if not rows:
            return
        with (out/name).open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)

    write_csv("GEO_alpha46_segment_inventory.csv", segment_rows)
    write_csv("GEO_alpha46_candidate_resource_contexts.csv", candidate_rows)
    write_csv("GEO_alpha46_program_segment_references.csv", pointer_rows)
    write_csv("GEO_alpha46_library_table.csv", parsed_a["libraries"])
    write_csv("GEO_alpha46_export_table.csv", parsed_a["exports"])
    fixup_type_rows = []
    for seg_index, entries in fixups_by_segment.items():
        counts = Counter(f"0x{x['type']:04X}" for x in entries)
        for raw_type, count in sorted(counts.items()):
            fixup_type_rows.append({"segment": seg_index, "fixup_type_raw": raw_type, "count": count})
    write_csv("GEO_alpha46_fixup_type_counts.csv", fixup_type_rows)

    export_distribution = Counter(str(x["segment"]) for x in parsed_a["exports"])
    summary = {
        "archive": archive.name,
        "archive_members": len(names),
        "zip_crc_ok": True,
        "source_files": list(SOURCE_FILES),
        "write_geo_size": len(a),
        "write_geo_sha256": {SOURCE_FILES[0]: sha256(a), SOURCE_FILES[1]: sha256(b)},
        "kernel_exe_present": bool(kernel),
        "kernel_exe_size": len(kernel),
        "kernel_exe_magic": kernel[:2].decode("latin1") if kernel else "",
        "kernel_exe_sha256": sha256(kernel) if kernel else "",
        "geos_file_magic": f"0x{GEOS_ID:08X}",
        "geode_header_offset_version1": f"0x{APP_HEADER_OFFSET:04X}",
        "application_type": parsed_a["app"]["type"],
        "application_attributes": f"0x{parsed_a['app']['attributes']:04X}",
        "permanent_name": parsed_a["app"]["permanent_name"],
        "permanent_extension": parsed_a["app"]["permanent_extension"],
        "num_segments": parsed_a["app"]["numseg"],
        "num_libraries": parsed_a["app"]["numlib"],
        "num_exports": parsed_a["app"]["numexp"],
        "libraries": parsed_a["libraries"],
        "exports_by_segment": dict(export_distribution),
        "application_process_pointer_raw": {
            "segment": parsed_a["app"]["x2_segment"],
            "offset": f"0x{parsed_a['app']['x2_offset']:04X}",
        },
        "application_token_resource_pointer_raw": {
            "segment": parsed_a["app"]["token_resource_segment"],
            "item": f"0x{parsed_a['app']['token_resource_item']:04X}",
        },
        "segment_table": {k: f"0x{v:04X}" for k,v in parsed_a["segment_table"].items()},
        "segment_table_identical_between_variants": True,
        "segment_descriptors_identical_between_variants": True,
        "code_segments": [s["index"] for s in segs if s["is_code"]],
        "code_segment_count": sum(1 for s in segs if s["is_code"]),
        "candidate_count_first_variant": len(candidate_rows),
        "candidate_offsets_identical_between_variants": True,
        "candidate_instruction_start_count_resource_local_sweep": sum(1 for r in candidate_rows if r["instruction_start_in_resource_sweep"]),
        "candidate_mov_si_expected_count_resource_local_sweep": sum(1 for r in candidate_rows if r["decodes_mov_si_expected_handle"]),
        "candidate_counts_by_segment": dict(candidate_by_seg),
        "candidate_flow_categories_first_control_flow_within_next_4": dict(candidate_flow),
        "near_control_flow_targets_resolved_to_instruction_starts": near_targets_resolved,
        "near_control_flow_targets": dict(near_targets),
        "program_segment_fixup_count_in_segment_1": len(pointer_rows),
        "program_segment_references_by_target_segment": dict(pointer_by_target),
        "program_segment_references_in_target_bounds": sum(1 for r in pointer_rows if r["target_within_segment_bounds"]),
        "program_segment_references_to_code_segments": sum(1 for r in pointer_rows if r["target_segment_has_code_flag"]),
        "program_segment_targets_at_instruction_starts_resource_local_sweep": sum(1 for r in pointer_rows if r["target_is_instruction_start_in_resource_sweep"]),
        "program_segment_target_boundary_counts": {f"SEG{seg}_instruction_start_{str(ok).lower()}": count for (seg,ok),count in pointer_boundary.items()},
        "r11_segment_index": R11_SEGMENT,
        "r11_file_offset": f"0x{r11['file_offset']:05X}",
        "r11_segment_length": f"0x{r11['length']:04X}",
        "r11_segment_flags": f"0x{r11['flags']:04X}",
        "r11_lmem_header": lmem,
        "r11_handle_table_values": [f"0x{x:04X}" for x in handle_values],
        "r11_candidate_handles": [f"0x{x:04X}" for x in TARGET_HANDLES],
        "candidate_context_method_limit": "GNU objdump performs a linear sweep from offset zero inside each resource flagged HAF_CODE. This is resource-local rather than whole-file disassembly, but it is not yet recursive control-flow tracing from validated entry points.",
        "pointer_method_limit": "Segment-1 fixups with raw type 0x0022 are interpreted as program-segment words. The preceding WORD is treated as the offset component, consistent with GeoDump's documented offset-first/segment-last far-pointer representation. Target instruction-boundary checks are against resource-local linear-sweep maps, not a complete control-flow graph.",
        "next_step": "Use the 351 segment-1 program-segment pointer pairs as entry-point candidates, trace control flow recursively, and resolve kernel ordinals 0x00A9 and 0x01E6 with a matching GeoWorks 1.x kernel symbol/export source.",
        "disassembler": subprocess.run([objdump, "--version"], capture_output=True, text=True).stdout.splitlines()[0],
    }
    (out/"GEO_alpha46_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n", encoding="utf-8")
    return summary

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive", type=Path)
    p.add_argument("--out", type=Path, default=Path("alpha46_output"))
    p.add_argument("--objdump", default="objdump")
    args = p.parse_args()
    print(json.dumps(analyze(args.archive, args.out, args.objdump), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
