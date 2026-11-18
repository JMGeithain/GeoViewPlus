"""Read-only PC/GEOS 2.x token DB and moniker-reference resolver.

The parser intentionally reports raw numeric fields where semantics have not
been independently established. It never modifies the VM file.
"""
from __future__ import annotations
from collections import Counter
from dataclasses import dataclass
import struct
from geoviewplus_token_db_v2 import TokenDBFormatError, VMDirectoryInfo, vm_block_data

DB_MAP_BLOCK_WORDS = 6
DB_ITEM_INFO_SIZE = 4
DB_ITEM_BLOCK_INFO_SIZE = 6
TOKEN_ENTRY_SIZE = 24
MONIKER_LIST_ENTRY_SIZE = 6
VIS_MONIKER_HEADER_SIZE = 5


@dataclass(frozen=True)
class DBMapBlockInfo:
    vm_handle: int
    memory_handle: int
    map_group: int
    map_item: int
    ungrouped_group: int
    new_ungrouped_group: int
    trailing_bytes: bytes


@dataclass(frozen=True)
class ResolvedDBItem:
    group_handle: int
    item_handle: int
    item_block_info_offset: int
    item_block_vm_handle: int
    item_block_ref_count: int
    lmem_chunk_handle: int
    lmem_chunk_offset: int
    chunk_size_word: int
    payload: bytes


@dataclass(frozen=True)
class TokenEntry:
    index: int
    token_chars: bytes
    manufacturer_id: int
    moniker_group: int
    moniker_item: int
    flags: int
    release_words: tuple[int, int, int, int]
    protocol_words: tuple[int, int]

    @property
    def token_text(self) -> str:
        return self.token_chars.decode("latin-1", errors="replace")


@dataclass(frozen=True)
class MonikerListEntry:
    index: int
    type_word: int
    group_handle: int
    item_handle: int

    @property
    def display_size_code(self) -> int:
        return (self.type_word & 0x3000) >> 12

    @property
    def style_code(self) -> int:
        return (self.type_word & 0x0F00) >> 8

    @property
    def is_gstring(self) -> bool:
        return bool(self.type_word & 0x0040)

    @property
    def is_moniker_list(self) -> bool:
        return bool(self.type_word & 0x0080)

    @property
    def aspect_ratio_code(self) -> int:
        return (self.type_word & 0x0030) >> 4

    @property
    def color_code(self) -> int:
        return self.type_word & 0x000F


@dataclass(frozen=True)
class VisMonikerHeader:
    type_byte: int
    width: int
    height: int
    payload_size: int

    @property
    def is_gstring(self) -> bool:
        return bool(self.type_byte & 0x40)

    @property
    def is_moniker_list(self) -> bool:
        return bool(self.type_byte & 0x80)

    @property
    def color_code(self) -> int:
        return self.type_byte & 0x0F

    @property
    def aspect_ratio_code(self) -> int:
        return (self.type_byte & 0x30) >> 4


@dataclass(frozen=True)
class ResolvedMoniker:
    token_index: int
    token_chars: bytes
    manufacturer_id: int
    list_entry: MonikerListEntry
    db_item: ResolvedDBItem
    header: VisMonikerHeader | None


@dataclass(frozen=True)
class TokenDatabaseAnalysis:
    file_sha256: str
    db_map: DBMapBlockInfo
    token_map_item: ResolvedDBItem
    token_entries: tuple[TokenEntry, ...]
    moniker_lists: dict[tuple[int, int], tuple[MonikerListEntry, ...]]
    resolved_monikers: tuple[ResolvedMoniker, ...]
    skipped_dummy_entry: bool
    warnings: tuple[str, ...]

    @property
    def moniker_list_count_distribution(self) -> dict[int, int]:
        return dict(Counter(len(v) for v in self.moniker_lists.values()))

    @property
    def manufacturer_id_counts(self) -> dict[int, int]:
        return dict(Counter(t.manufacturer_id for t in self.token_entries))


def parse_db_map_block(block: bytes, expected_vm_handle: int | None = None) -> DBMapBlockInfo:
    if len(block) < DB_MAP_BLOCK_WORDS * 2:
        raise TokenDBFormatError("DB-Map-Block ist kürzer als sechs WORD-Felder")
    words = struct.unpack_from("<6H", block, 0)
    if expected_vm_handle is not None and words[0] != expected_vm_handle:
        raise TokenDBFormatError(
            f"DB-Map-Block meldet Handle 0x{words[0]:04X}, erwartet 0x{expected_vm_handle:04X}"
        )
    return DBMapBlockInfo(*words, trailing_bytes=bytes(block[12:]))


def resolve_db_item(data: bytes, directory: VMDirectoryInfo,
                    group_handle: int, item_handle: int) -> ResolvedDBItem:
    """Resolve DB group/item -> DBItemInfo -> DBItemBlockInfo -> LMem chunk."""
    try:
        group = vm_block_data(data, directory, group_handle)
    except KeyError as exc:
        raise TokenDBFormatError(f"DB-Gruppe 0x{group_handle:04X} fehlt") from exc
    if item_handle < 0 or item_handle + DB_ITEM_INFO_SIZE > len(group):
        raise TokenDBFormatError(
            f"DB-Item-Offset 0x{item_handle:04X} liegt außerhalb der Gruppe 0x{group_handle:04X}"
        )
    info_offset, chunk_handle = struct.unpack_from("<HH", group, item_handle)
    if info_offset + DB_ITEM_BLOCK_INFO_SIZE > len(group):
        raise TokenDBFormatError(
            f"DBItemBlockInfo 0x{info_offset:04X} liegt außerhalb der Gruppe 0x{group_handle:04X}"
        )
    _next_info, item_block_handle, ref_count = struct.unpack_from("<3H", group, info_offset)
    try:
        item_block = vm_block_data(data, directory, item_block_handle)
    except KeyError as exc:
        raise TokenDBFormatError(
            f"Item-Block 0x{item_block_handle:04X} aus Gruppe 0x{group_handle:04X} fehlt"
        ) from exc
    if len(item_block) < 16:
        raise TokenDBFormatError(f"LMem-Item-Block 0x{item_block_handle:04X} ist zu kurz")
    handle_table_offset = struct.unpack_from("<H", item_block, 2)[0]
    handle_count = struct.unpack_from("<H", item_block, 10)[0]
    if chunk_handle < handle_table_offset or (chunk_handle - handle_table_offset) % 2:
        raise TokenDBFormatError(
            f"LMem-Chunkhandle 0x{chunk_handle:04X} ist kein gültiger Handle-Tabellenoffset"
        )
    handle_index = (chunk_handle - handle_table_offset) // 2
    if handle_index >= handle_count or chunk_handle + 2 > len(item_block):
        raise TokenDBFormatError(
            f"LMem-Chunkhandle 0x{chunk_handle:04X} liegt außerhalb der Handle-Tabelle"
        )
    chunk_offset = struct.unpack_from("<H", item_block, chunk_handle)[0]
    if chunk_offset < 2 or chunk_offset > len(item_block):
        raise TokenDBFormatError("LMem-Chunkposition liegt außerhalb des Item-Blocks")
    size_word = struct.unpack_from("<H", item_block, chunk_offset - 2)[0]
    if size_word < 2 or size_word - 2 > len(item_block) - chunk_offset:
        raise TokenDBFormatError("LMem-Chunkgröße reicht über das Ende des Item-Blocks")
    payload = bytes(item_block[chunk_offset:chunk_offset + size_word - 2])
    return ResolvedDBItem(group_handle, item_handle, info_offset, item_block_handle,
                          ref_count, chunk_handle, chunk_offset, size_word, payload)


def parse_token_entries(payload: bytes) -> tuple[tuple[TokenEntry, ...], bool, tuple[str, ...]]:
    if len(payload) % TOKEN_ENTRY_SIZE:
        raise TokenDBFormatError(
            f"Token-Map-Größe {len(payload)} ist kein Vielfaches von {TOKEN_ENTRY_SIZE}"
        )
    count = len(payload) // TOKEN_ENTRY_SIZE
    if not count:
        raise TokenDBFormatError("Token-Map enthält keinen Datensatz")
    skipped_dummy = payload[:TOKEN_ENTRY_SIZE] == bytes(TOKEN_ENTRY_SIZE)
    start = 1 if skipped_dummy else 0
    warnings = [] if skipped_dummy else [
        "Erster TokenEntry ist nicht vollständig null; er wurde nicht als Dummy übersprungen."
    ]
    result = []
    for index in range(start, count):
        rec = payload[index * TOKEN_ENTRY_SIZE:(index + 1) * TOKEN_ENTRY_SIZE]
        chars = rec[0:4]
        manufacturer = struct.unpack_from("<H", rec, 4)[0]
        moniker_group, moniker_item = struct.unpack_from("<HH", rec, 6)
        flags = struct.unpack_from("<H", rec, 10)[0]
        release = struct.unpack_from("<4H", rec, 12)
        protocol = struct.unpack_from("<2H", rec, 20)
        if chars == bytes(4) and manufacturer == 0 and moniker_group == 0 and moniker_item == 0:
            warnings.append(f"Leerer TokenEntry an Index {index} wird als Rohdatensatz beibehalten.")
        result.append(TokenEntry(index, chars, manufacturer, moniker_group, moniker_item,
                                 flags, tuple(release), tuple(protocol)))
    return tuple(result), skipped_dummy, tuple(warnings)


def parse_moniker_list(payload: bytes) -> tuple[MonikerListEntry, ...]:
    if len(payload) % MONIKER_LIST_ENTRY_SIZE:
        raise TokenDBFormatError(
            f"Moniker-Liste mit {len(payload)} Bytes ist kein Vielfaches von 6"
        )
    result = []
    for index, off in enumerate(range(0, len(payload), MONIKER_LIST_ENTRY_SIZE)):
        typ, group, item = struct.unpack_from("<3H", payload, off)
        result.append(MonikerListEntry(index, typ, group, item))
    return tuple(result)


def parse_vis_moniker_header(payload: bytes) -> VisMonikerHeader | None:
    if len(payload) < VIS_MONIKER_HEADER_SIZE:
        return None
    type_byte = payload[0]
    width, height = struct.unpack_from("<HH", payload, 1)
    return VisMonikerHeader(type_byte, width, height, len(payload) - VIS_MONIKER_HEADER_SIZE)


def analyze_token_database(data: bytes, directory: VMDirectoryInfo) -> TokenDatabaseAnalysis:
    if directory.file_size != len(data):
        raise TokenDBFormatError("VM-Verzeichnis gehört nicht zu den übergebenen Dateibytes")
    try:
        db_map_raw = vm_block_data(data, directory, directory.db_map_block_handle)
    except KeyError as exc:
        raise TokenDBFormatError("DB-Map-Block fehlt") from exc
    db_map = parse_db_map_block(db_map_raw, directory.db_map_block_handle)
    token_map_item = resolve_db_item(data, directory, db_map.map_group, db_map.map_item)
    tokens, skipped_dummy, warnings = parse_token_entries(token_map_item.payload)
    moniker_lists: dict[tuple[int, int], tuple[MonikerListEntry, ...]] = {}
    resolved = []
    for token in tokens:
        key = (token.moniker_group, token.moniker_item)
        if key not in moniker_lists:
            list_item = resolve_db_item(data, directory, *key)
            moniker_lists[key] = parse_moniker_list(list_item.payload)
        for entry in moniker_lists[key]:
            moniker_item = resolve_db_item(data, directory, entry.group_handle, entry.item_handle)
            header = parse_vis_moniker_header(moniker_item.payload)
            resolved.append(ResolvedMoniker(token.index, token.token_chars, token.manufacturer_id,
                                            entry, moniker_item, header))
    return TokenDatabaseAnalysis(directory.sha256, db_map, token_map_item, tokens,
                                 moniker_lists, tuple(resolved), skipped_dummy, tuple(warnings))


def summarize_token_database(analysis: TokenDatabaseAnalysis) -> str:
    lines = [
        "PC/GEOS-2.x Token-Datenbank – DB-/Moniker-Auflösung (read-only)",
        f"SHA-256: {analysis.file_sha256}",
        f"DB-Map-Block: 0x{analysis.db_map.vm_handle:04X}",
        f"Token-Map: Gruppe 0x{analysis.db_map.map_group:04X}, Item 0x{analysis.db_map.map_item:04X}",
        f"Token-Einträge: {len(analysis.token_entries)}",
        f"Dummy-Eintrag übersprungen: {'ja' if analysis.skipped_dummy_entry else 'nein'}",
        f"Unterschiedliche Monikerlisten: {len(analysis.moniker_lists)}",
        f"Moniker-Referenzen erfolgreich aufgelöst: {len(analysis.resolved_monikers)}",
        "Monikerlisten-Längen (Einträge je Liste):",
    ]
    lines.extend(f"  {count}: {n} Listen" for count, n in sorted(analysis.moniker_list_count_distribution.items()))
    lines.append("Hersteller-IDs (numerisch):")
    lines.extend(f"  0x{mid:04X}: {n}" for mid, n in sorted(analysis.manufacturer_id_counts.items()))
    lines.append("Release-/Protocol-Werte bleiben Rohdaten und werden nicht semantisch bewertet.")
    if analysis.warnings:
        lines.append("Warnungen:")
        lines.extend(f"  - {w}" for w in analysis.warnings)
    return "\n".join(lines)
