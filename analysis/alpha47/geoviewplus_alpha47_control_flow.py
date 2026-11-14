#!/usr/bin/env python3
"""GeoViewPlus 0.5 Alpha47: recursive control-flow reachability audit.

Seeds are derived from GeoWorks 1.x program-segment fixups (0x22), program
far-pointer fixups (0x24), and the exported routine table. GNU objdump decodes
basic blocks from those addresses in 8086 mode. Results remain provisional:
indirect dispatch, unresolved fixup forms, and overlapping decodes are reported.
"""
from __future__ import annotations
import argparse, csv, json, re, shutil, subprocess, tempfile, zipfile, hashlib, os, sys
from collections import Counter
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "alpha46"))
from geoviewplus_alpha46_geode_resource_map import parse_geode, u16, sha256, SOURCE_FILES, disassemble_resource

TARGET_HANDLES = tuple(range(0x26, 0x38, 2))
INSN_RE = re.compile(r"^\s*([0-9a-fA-F]+):\s*((?:[0-9a-fA-F]{2}\s+)+)\s*([a-zA-Z][\w.]*)\s*(.*?)\s*$")

def find_all(data: bytes, needle: bytes) -> list[int]:
    out, pos = [], 0
    while True:
        pos = data.find(needle, pos)
        if pos < 0:
            return out
        out.append(pos)
        pos += 1

def decode_block(segment_file: str, segment_length: int, start: int, objdump: str, max_bytes: int = 0x80) -> list[dict]:
    if not 0 <= start < segment_length:
        return []
    end = min(start + max_bytes, segment_length)
    cmd = [objdump, "-D", "-b", "binary", "-m", "i8086", "-Mintel",
           f"--start-address={start}", f"--stop-address={end}", segment_file]
    proc = subprocess.run(cmd, check=True, capture_output=True, text=True, errors="replace")
    rows = []
    for line in proc.stdout.splitlines():
        m = INSN_RE.match(line)
        if m:
            rows.append({
                "offset": int(m.group(1), 16),
                "bytes": bytes.fromhex(m.group(2)),
                "mnemonic": m.group(3).lower(),
                "operands": m.group(4).strip(),
            })
    return rows

def parse_near_target(operands: str) -> int | None:
    if ":" in operands:
        return None
    m = re.search(r"0x([0-9a-fA-F]+)", operands)
    return int(m.group(1), 16) if m else None

def analyze(archive: Path, out: Path, objdump: str = "objdump", max_blocks: int = 20000) -> dict:
    archive, out = Path(archive), Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if shutil.which(objdump) is None:
        raise RuntimeError(f"GNU objdump not found: {objdump}")
    with zipfile.ZipFile(archive) as zf:
        bad = zf.testzip()
        if bad is not None:
            raise ValueError(f"ZIP CRC failure: {bad}")
        names = set(zf.namelist())
        a, b = (zf.read(p) for p in SOURCE_FILES)
    parsed, parsed_b = parse_geode(a), parse_geode(b)
    if parsed["segments"] != parsed_b["segments"] or parsed["segment_table"] != parsed_b["segment_table"]:
        raise ValueError("WRITE.GEO resource tables differ between variants")
    segs = parsed["segments"]
    data = {s["index"]: a[s["file_offset"]:s["file_offset"]+s["length"]]
            for s in segs if s["length"]}
    resource_instruction_maps = {}
    for s in segs:
        if s["is_code"] and s["length"]:
            resource_instruction_maps[s["index"]] = disassemble_resource(data[s["index"]], objdump)[0]

    temp_paths = {}
    try:
        for seg, blob in data.items():
            f = tempfile.NamedTemporaryFile(prefix=f"gvp_a47_seg{seg}_", suffix=".bin", delete=False)
            f.write(blob); f.close(); temp_paths[seg] = f.name

        fixups = {}
        for s in segs:
            entries = []
            for j in range(s["fixup_count"]):
                p = s["fixup_offset"] + 4*j
                entries.append({"type": u16(a, p), "offset": u16(a, p+2)})
            fixups[s["index"]] = entries
        fixup_maps = {seg: {x["offset"]: x["type"] for x in rows} for seg, rows in fixups.items()}

        candidates = {}
        for handle in TARGET_HANDLES:
            needle = b"\xBE" + handle.to_bytes(2, "little")
            ha, hb = find_all(a, needle), find_all(b, needle)
            if ha != hb:
                raise ValueError(f"Alpha45 candidate positions differ for handle {handle:#x}")
            for file_off in ha:
                owner = next((s for s in segs if s["is_code"] and s["file_offset"] <= file_off < s["file_offset"]+s["length"]), None)
                if owner:
                    key = (owner["index"], file_off-owner["file_offset"])
                    candidates[key] = handle

        pointer_rows = []
        pointer_seeds = set()
        seg1 = segs[1]
        d1 = data[1]
        for fx in fixups[1]:
            if fx["type"] != 0x22:
                continue
            off = fx["offset"]
            if off < 2 or off+2 > len(d1):
                raise ValueError(f"Invalid type-0x22 fixup in segment 1 at {off:#x}")
            target_seg, target_off = u16(d1, off), u16(d1, off-2)
            target = segs[target_seg] if target_seg < len(segs) else None
            in_bounds = bool(target and target["length"] and target_off < target["length"])
            is_code = bool(target and target["is_code"])
            target_instruction = bool(is_code and target_off in resource_instruction_maps.get(target_seg, {}))
            pointer_rows.append({"source_segment":1,"fixup_offset":off,"target_segment":target_seg,
                                 "target_offset":target_off,"target_in_bounds":in_bounds,"target_is_code":is_code,
                                 "target_instruction_start_resource_sweep":target_instruction})
            if in_bounds and is_code:
                pointer_seeds.add((target_seg,target_off))

        far_pointer_rows = []
        far_pointer_seeds = set()
        for s in segs:
            blob = data.get(s["index"], b"")
            for fx in fixups[s["index"]]:
                if fx["type"] != 0x24:
                    continue
                off = fx["offset"]
                if off+4 > len(blob):
                    raise ValueError(f"Invalid type-0x24 pointer in segment {s['index']} at {off:#x}")
                target_seg, target_off = u16(blob, off), u16(blob, off+2)
                target = segs[target_seg] if target_seg < len(segs) else None
                in_bounds = bool(target and target["length"] and target_off < target["length"])
                is_code = bool(target and target["is_code"])
                target_instruction = bool(is_code and target_off in resource_instruction_maps.get(target_seg, {}))
                far_pointer_rows.append({"source_segment":s["index"],"fixup_offset":off,
                                         "target_segment":target_seg,"target_offset":target_off,
                                         "target_in_bounds":in_bounds,"target_is_code":is_code,
                                         "target_instruction_start_resource_sweep":target_instruction})
                if in_bounds and is_code:
                    far_pointer_seeds.add((target_seg,target_off))

        export_seeds = {(x["segment"],x["offset"]) for x in parsed["exports"]}
        seeds = pointer_seeds | far_pointer_seeds | export_seeds

        queue = list(seeds)
        queued = set(seeds)
        processed_blocks = set()
        visited = set()
        decoded = {}
        edges = []
        candidate_hits = {}
        unresolved = []
        external = Counter()
        stops = Counter()
        conflicts = []
        block_rows = []
        block_count = 0

        while queue and block_count < max_blocks:
            seg, start = queue.pop()
            if (seg,start) in processed_blocks:
                continue
            processed_blocks.add((seg,start)); block_count += 1
            if seg not in data:
                unresolved.append({"segment":seg,"offset":start,"reason":"segment has no data"})
                continue
            block = decode_block(temp_paths[seg], len(data[seg]), start, objdump)
            if not block or block[0]["offset"] != start:
                unresolved.append({"segment":seg,"offset":start,"reason":"objdump could not decode entry"})
                continue
            block_instruction_count = 0
            block_exit = "window_end"
            for idx, ins in enumerate(block):
                off, raw, mn, op = ins["offset"], ins["bytes"], ins["mnemonic"], ins["operands"]
                if idx and off != block[idx-1]["offset"] + len(block[idx-1]["bytes"]):
                    block_exit = "decode_gap"
                    break
                old = decoded.get((seg,off))
                if old and (old["bytes"] != raw or old["mnemonic"] != mn):
                    conflicts.append({"segment":seg,"offset":off,"existing_bytes":old["bytes"].hex(" ").upper(),
                                      "alternate_bytes":raw.hex(" ").upper(),"existing_mnemonic":old["mnemonic"],
                                      "alternate_mnemonic":mn})
                    block_exit = "overlap_conflict"
                    break
                decoded[(seg,off)] = ins
                visited.add((seg,off)); block_instruction_count += 1
                if (seg,off) in candidates:
                    candidate_hits[(seg,off)] = candidates[(seg,off)]
                nxt = off + len(raw)

                if mn == "call":
                    if raw[0] == 0x9A:
                        if fixup_maps.get(seg,{}).get(off+3) == 0x22 and off+5 <= len(data[seg]):
                            ts, to = u16(data[seg],off+3), u16(data[seg],off+1)
                            if ts < len(segs) and segs[ts]["is_code"] and to < len(data.get(ts,b"")):
                                edges.append({"source_segment":seg,"source_offset":off,"target_segment":ts,"target_offset":to,"kind":"far_call_program"})
                                if (ts,to) not in queued: queue.append((ts,to)); queued.add((ts,to))
                            else: external["far_call_program_outside_code"] += 1
                        else:
                            external["far_call_external"] += 1
                    else:
                        target = parse_near_target(op)
                        if target is not None and target < len(data[seg]):
                            edges.append({"source_segment":seg,"source_offset":off,"target_segment":seg,"target_offset":target,"kind":"near_call"})
                            if (seg,target) not in queued: queue.append((seg,target)); queued.add((seg,target))
                        else: external["indirect_or_unparsed_near_call"] += 1
                    if idx == len(block)-1:
                        if nxt < len(data[seg]) and (seg,nxt) not in queued: queue.append((seg,nxt)); queued.add((seg,nxt))
                        block_exit = "call_fallthrough"
                    continue

                if mn == "jmp":
                    if raw[0] == 0xEA:
                        if fixup_maps.get(seg,{}).get(off+3) == 0x22 and off+5 <= len(data[seg]):
                            ts, to = u16(data[seg],off+3), u16(data[seg],off+1)
                            if ts < len(segs) and segs[ts]["is_code"] and to < len(data.get(ts,b"")):
                                edges.append({"source_segment":seg,"source_offset":off,"target_segment":ts,"target_offset":to,"kind":"far_jmp_program"})
                                if (ts,to) not in queued: queue.append((ts,to)); queued.add((ts,to))
                            else: external["far_jmp_program_outside_code"] += 1
                        else: external["far_jmp_external"] += 1
                        stops["far_jmp"] += 1; block_exit = "far_jmp"; break
                    target = parse_near_target(op)
                    if target is not None and target < len(data[seg]):
                        edges.append({"source_segment":seg,"source_offset":off,"target_segment":seg,"target_offset":target,"kind":"near_jmp"})
                        if (seg,target) not in queued: queue.append((seg,target)); queued.add((seg,target))
                    else: stops["indirect_jmp"] += 1
                    block_exit = "near_or_indirect_jmp"; break

                if mn.startswith("ret") or mn in ("iret","hlt"):
                    stops[mn] += 1; block_exit = mn; break

                if (mn.startswith("j") and mn != "jmp") or mn.startswith("loop"):
                    target = parse_near_target(op)
                    if target is not None and target < len(data[seg]):
                        edges.append({"source_segment":seg,"source_offset":off,"target_segment":seg,"target_offset":target,"kind":mn})
                        if (seg,target) not in queued: queue.append((seg,target)); queued.add((seg,target))
                    if idx == len(block)-1:
                        if nxt < len(data[seg]) and (seg,nxt) not in queued: queue.append((seg,nxt)); queued.add((seg,nxt))
                        block_exit = "conditional_fallthrough"
                    continue

                if mn in ("int","into"):
                    stops[mn] += 1

                if idx == len(block)-1:
                    if nxt < len(data[seg]) and (seg,nxt) not in queued: queue.append((seg,nxt)); queued.add((seg,nxt))
                    block_exit = "window_end"
            block_rows.append({"segment":seg,"start_offset":f"0x{start:04X}",
                               "instructions_decoded":block_instruction_count,"exit_kind":block_exit})

        if queue:
            stops["queue_limit_remaining"] += len(queue)

        candidate_rows = []
        for (seg,off),handle in sorted(candidates.items()):
            candidate_rows.append({"segment":seg,"segment_relative_offset":f"0x{off:04X}",
                                   "file_offset":f"0x{segs[seg]['file_offset']+off:05X}",
                                   "chunk_handle":f"0x{handle:04X}",
                                   "reached_by_recursive_seeded_graph":(seg,off) in candidate_hits,
                                   "decoded_as_instruction_in_graph":(seg,off) in decoded,
                                   "graph_instruction":(decoded[(seg,off)]["mnemonic"]+" "+decoded[(seg,off)]["operands"]).strip() if (seg,off) in decoded else ""})

        def write_csv(name, rows):
            if rows:
                with (out/name).open("w",newline="",encoding="utf-8-sig") as f:
                    w=csv.DictWriter(f,fieldnames=list(rows[0].keys()));w.writeheader();w.writerows(rows)
        write_csv("GEO_alpha47_candidate_reachability.csv",candidate_rows)
        write_csv("GEO_alpha47_segment1_program_pointer_seeds.csv",pointer_rows)
        write_csv("GEO_alpha47_program_far_pointer_seeds.csv",far_pointer_rows)
        write_csv("GEO_alpha47_reachable_basic_blocks.csv",block_rows)
        write_csv("GEO_alpha47_control_flow_edges.csv",edges)
        write_csv("GEO_alpha47_decode_conflicts.csv",conflicts)
        write_csv("GEO_alpha47_unresolved_entries.csv",unresolved)

        by_seg = Counter(str(r["segment"]) for r in candidate_rows if r["reached_by_recursive_seeded_graph"])
        summary = {
            "archive":archive.name,"zip_crc_ok":True,"archive_members":len(names),
            "write_geo_sha256":{SOURCE_FILES[0]:sha256(a),SOURCE_FILES[1]:sha256(b)},
            "segment1_program_segment_fixup_rows":len(pointer_rows),
            "segment1_unique_code_pointer_seeds":len(pointer_seeds),
            "segment1_code_pointer_targets_at_instruction_starts_resource_sweep":sum(1 for r in pointer_rows if r["target_instruction_start_resource_sweep"]),
            "program_far_pointer_fixup_rows_type_0x24":len(far_pointer_rows),
            "program_far_pointer_unique_code_targets":len(far_pointer_seeds),
            "program_far_pointer_targets_at_instruction_starts_resource_local_sweep":sum(1 for r in far_pointer_rows if r["target_instruction_start_resource_sweep"]),
            "export_entry_count":len(export_seeds),
            "unique_recursive_seeds":len(seeds),
            "processed_basic_blocks":block_count,
            "decoded_instruction_addresses":len(decoded),
            "control_flow_edges":len(edges),
            "overlapping_decode_conflicts":len(conflicts),
            "unresolved_seed_or_branch_entries":len(unresolved),
            "candidate_count":len(candidate_rows),
            "candidate_reached_count":sum(1 for r in candidate_rows if r["reached_by_recursive_seeded_graph"]),
            "candidate_not_reached_count":sum(1 for r in candidate_rows if not r["reached_by_recursive_seeded_graph"]),
            "candidate_reached_by_segment":dict(by_seg),
            "candidate_not_reached":[{"segment":int(r["segment"]),"offset":r["segment_relative_offset"],"file_offset":r["file_offset"],"handle":r["chunk_handle"]} for r in candidate_rows if not r["reached_by_recursive_seeded_graph"]],
            "stop_reasons":dict(stops),"external_calls_and_jumps":dict(external),
            "method_limit":"Recursive traversal begins from 0x22 program-segment references, 0x24 program far pointers, and 16 exported routine addresses. Basic blocks are decoded from each seed with GNU objdump. Indirect dispatch and unresolved fixup forms are not followed. Overlapping decodes are reported; candidates not reached are not proven dead.",
            "next_step":"Investigate indirect dispatch/object-resource references for the 18 candidates not reached, and resolve kernel ordinals with a matching GeoWorks 1.x kernel source.",
            "disassembler":subprocess.run([objdump,"--version"],capture_output=True,text=True).stdout.splitlines()[0],
        }
        (out/"GEO_alpha47_summary.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        return summary
    finally:
        for path in temp_paths.values():
            try: os.unlink(path)
            except OSError: pass

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("archive",type=Path)
    p.add_argument("--out",type=Path,default=Path("alpha47_output"))
    p.add_argument("--objdump",default="objdump")
    p.add_argument("--max-blocks",type=int,default=20000)
    args=p.parse_args()
    print(json.dumps(analyze(args.archive,args.out,args.objdump,args.max_blocks),indent=2,ensure_ascii=False))

if __name__=="__main__":main()
