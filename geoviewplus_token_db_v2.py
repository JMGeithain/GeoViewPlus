"""Read-only PC/GEOS 2.x VM-directory parser."""
from __future__ import annotations
from dataclasses import dataclass
from collections import Counter
from pathlib import Path
import hashlib
import struct

SIG_V2 = bytes.fromhex("C7 45 C1 53")
VM_HEADER = 0x100
VM_MAGIC = 0xADEB
DIR_MAGIC = 0x00FB
DIR_HEADER_SIZE = 0x20
DIR_ENTRY_SIZE = 12


class TokenDBFormatError(ValueError):
    pass


def u16(data: bytes, off: int) -> int:
    if off < 0 or off + 2 > len(data):
        raise TokenDBFormatError(f"WORD außerhalb der Datei: 0x{off:X}")
    return struct.unpack_from("<H", data, off)[0]


def u32(data: bytes, off: int) -> int:
    if off < 0 or off + 4 > len(data):
        raise TokenDBFormatError(f"DWORD außerhalb der Datei: 0x{off:X}")
    return struct.unpack_from("<I", data, off)[0]


@dataclass(frozen=True)
class VMBlockEntry:
    index: int
    vm_handle: int
    memory_handle: int
    flags: int
    user_id: int
    size: int
    file_position_relative: int
    file_offset: int

    @property
    def allocated(self) -> bool:
        return bool(self.file_position_relative and self.size)


@dataclass(frozen=True)
class VMDirectoryInfo:
    file_size: int
    sha256: str
    directory_file_offset: int
    directory_pointer_relative: int
    vm_header_directory_size: int
    directory_size: int
    first_free_handle: int
    last_free_handle: int
    first_unused_handle: int
    free_block_count: int
    free_handle_count: int
    used_block_count: int
    loaded_block_count: int
    map_block_handle: int
    compaction_threshold: int
    total_allocated_size: int
    vm_flags: int
    db_map_block_handle: int
    entries: tuple[VMBlockEntry, ...]

    @property
    def allocated_entries(self):
        return tuple(e for e in self.entries if e.allocated)

    @property
    def user_id_counts(self):
        return dict(Counter(e.user_id for e in self.allocated_entries))


def parse_pcgeos2_vm_directory(data: bytes, label: str = "<bytes>") -> VMDirectoryInfo:
    if len(data) < 0x118 or data[:4] != SIG_V2:
        raise TokenDBFormatError(f"{label}: keine vollständige PC/GEOS-2.x-Datei")
    if u16(data, 0x28) != 2:
        raise TokenDBFormatError(f"{label}: GEOS-Dateityp ist nicht VM (type != 2)")
    if u16(data, VM_HEADER) != VM_MAGIC:
        raise TokenDBFormatError(f"{label}: VM-Kennung 0xADEB fehlt")
    vm_dir_size = u16(data, VM_HEADER + 2)
    dirptr = u32(data, VM_HEADER + 4)
    directory = 0x100 + dirptr  # dirptr is relative to the byte after the 256-byte GEOS header
    if directory < 0x100 or directory + DIR_HEADER_SIZE > len(data):
        raise TokenDBFormatError(f"{label}: Directory-Zeiger außerhalb der Datei")
    if u16(data, directory) != DIR_MAGIC:
        raise TokenDBFormatError(f"{label}: Directory-Kennung 0x00FB fehlt")

    first_free, last_free, first_unused, dir_size = struct.unpack_from("<4H", data, directory + 2)
    free_blocks, free_handles, used_blocks, loaded_blocks = struct.unpack_from("<4H", data, directory + 10)
    map_handle = u16(data, directory + 20)
    compaction = u16(data, directory + 22)
    total_size = u32(data, directory + 24)
    vm_flags = data[directory + 28]
    db_map_handle = u16(data, directory + 30)

    payload = dir_size - DIR_HEADER_SIZE
    if payload < 0 or payload % DIR_ENTRY_SIZE:
        raise TokenDBFormatError(f"{label}: Directory-Größe passt nicht zu 12-Byte-Einträgen")
    if directory + dir_size > len(data):
        raise TokenDBFormatError(f"{label}: Directory reicht über Dateiende")
    count = payload // DIR_ENTRY_SIZE
    entries = []
    for i in range(count):
        off = directory + DIR_HEADER_SIZE + i * DIR_ENTRY_SIZE
        mem, flags, uid, size, pos = struct.unpack_from("<HHHHI", data, off)
        absolute = 0x100 + pos if pos else 0
        if pos and (absolute > len(data) or size > len(data) - absolute):
            raise TokenDBFormatError(f"{label}: Block {i} liegt außerhalb der Datei")
        entries.append(VMBlockEntry(i, DIR_HEADER_SIZE + i * DIR_ENTRY_SIZE,
                                    mem, flags, uid, size, pos, absolute))
    allocated = sum(e.allocated for e in entries)
    if allocated not in (used_blocks, used_blocks + 1):
        raise TokenDBFormatError(
            f"{label}: {allocated} belegte Einträge passen nicht zu nblocks_used={used_blocks}"
        )
    return VMDirectoryInfo(
        len(data), hashlib.sha256(data).hexdigest(), directory, dirptr, vm_dir_size,
        dir_size, first_free, last_free, first_unused, free_blocks, free_handles,
        used_blocks, loaded_blocks, map_handle, compaction, total_size, vm_flags,
        db_map_handle, tuple(entries)
    )


def vm_block_data(data: bytes, info: VMDirectoryInfo, vm_handle: int) -> bytes:
    if vm_handle < DIR_HEADER_SIZE:
        raise KeyError(f"Ungültiger VM-Handle 0x{vm_handle:04X}")
    index, rem = divmod(vm_handle - DIR_HEADER_SIZE, DIR_ENTRY_SIZE)
    if rem or index >= len(info.entries):
        raise KeyError(f"VM-Handle 0x{vm_handle:04X} ist kein Directory-Eintrag")
    entry = info.entries[index]
    if entry.vm_handle != vm_handle or not entry.allocated:
        raise KeyError(f"VM-Handle 0x{vm_handle:04X} ist nicht belegt")
    return bytes(data[entry.file_offset:entry.file_offset + entry.size])


def summarize_vm_directory(info: VMDirectoryInfo) -> str:
    lines = [
        "PC/GEOS-2.x-VM-Verzeichnis (read-only)",
        f"Dateigröße: {info.file_size:,} Bytes",
        f"SHA-256: {info.sha256}",
        f"Directory-Dateioffset: 0x{info.directory_file_offset:X}",
        f"Directory-Größe: 0x{info.directory_size:X}",
        f"Directory-Einträge: {len(info.entries)}",
        f"Belegte Blöcke: {len(info.allocated_entries)}",
        f"Frei: {info.free_block_count}; freie Handles: {info.free_handle_count}; "
        f"belegt laut Header: {info.used_block_count}; geladen: {info.loaded_block_count}",
        f"Map-Block-Handle: 0x{info.map_block_handle:04X}",
        f"DB-Map-Block-Handle: 0x{info.db_map_block_handle:04X}",
        "User-ID-Verteilung (nur numerisch):",
    ]
    lines.extend(f"  0x{k:04X}: {v}" for k, v in sorted(info.user_id_counts.items()))
    lines.append("Token-/Moniker-/Icon-Bedeutungen sind noch nicht semantisch zugeordnet.")
    return "\n".join(lines)


def parse_file(path: str | Path) -> VMDirectoryInfo:
    path = Path(path)
    return parse_pcgeos2_vm_directory(path.read_bytes(), str(path))
