# ELF Format — Executable and Linkable Format

## What is ELF?

ELF (Executable and Linkable Format) is the standard binary format for executables, object files, and shared libraries on Linux and many other Unix-like systems.

## ELF Structure

```
┌─────────────────────────────────────┐
│     ELF Header (64 bytes)           │
├─────────────────────────────────────┤
│     Program Header Table            │
│     (segments for runtime loading)  │
├─────────────────────────────────────┤
│     Section Data (text, data...)    │
├─────────────────────────────────────┤
│     Section Header Table            │
│     (metadata for linking)          │
└─────────────────────────────────────┘
```

## ELF Header (bytes 0-63)

| Offset | Size | Field | Meaning |
|--------|------|-------|---------|
| 0-3   | 4    | `e_ident` | Magic: `0x7F 'E' 'L' 'F'` |
| 4     | 1    | `ei_class` | 1=32-bit, 2=64-bit |
| 5     | 1    | `ei_data` | 1=little, 2=big endian |
| 6     | 1    | `ei_version` | ELF version (usually 1) |
| 7     | 1    | `ei_osabi` | OS ABI (0=System V) |
| 16-17 | 2    | `e_type` | 1=relocatable, 2=executable, 3=shared |
| 18-19 | 2    | `e_machine` | 0x3E = x86-64 |
| 20-23 | 4    | `e_version` | Version (1) |
| 24-31 | 8    | `e_entry` | Entry point address |
| 32-39 | 8    | `e_phoff` | Program header offset |
| 40-47 | 8    | `e_shoff` | Section header offset |
| 48-49 | 2    | `e_flags` | Flags (0 for x86-64) |
| 50-51 | 2    | `e_ehsize` | ELF header size (64) |
| 52-53 | 2    | `e_phentsize` | Program header entry size (56) |
| 54-55 | 2    | `e_phnum` | Number of program headers |
| 56-57 | 2    | `e_shentsize` | Section header entry size (64) |
| 58-59 | 2    | `e_shnum` | Number of section headers |
| 60-61 | 2    | `e_shstrndx` | Section header string table index |

## Program Headers (Segments)

These tell the OS **how to load** the binary:

| Offset | Size | Field | Meaning |
|--------|------|-------|---------|
| 0-3   | 4    | `p_type` | 1=PT_LOAD (loadable segment) |
| 4-7   | 4    | `p_flags` | PF_R=4, PF_W=2, PF_X=1 |
| 8-15  | 8    | `p_offset` | Offset in file |
| 16-23 | 8    | `p_vaddr` | Virtual address in memory |
| 24-31 | 8    | `p_paddr` | Physical address (usually same) |
| 32-39 | 8    | `p_filesz` | Size in file |
| 40-47 | 8    | `p_memsz` | Size in memory (bss adds extra) |
| 48-55 | 8    | `p_align` | Alignment (0x200000 typical) |

### Common Segment Setup

For a simple executable:
- **Text segment:** Read+Exec, contains `.text` section
- **Data segment:** Read+Write, contains `.data` and `.bss`

## Sections (for linking/debugging)

| Section | Contents |
|---------|----------|
| `.text` | Executable code |
| `.data` | Initialized global variables |
| `.bss` | Uninitialized data (zero-filled) |
| `.rodata` | Read-only data (strings) |
| `.symtab` | Symbol table (functions, globals) |
| `.strtab` | String table (names) |
| `.shstrtab` | Section header string table |

## Building an ELF from Scratch

The `ELFBuilder` class creates minimal ELF64 binaries:

```python
builder = ELFBuilder()
builder.add_section('.text', b'\x90\xc3')  # nop; ret
builder.add_section('.data', b'ZETA\x00')
elf = builder.build(entry_point=0x1000)
Path('output/myprog').write_bytes(elf)
```

The resulting binary:
1. Valid ELF header with correct magic
2. PT_LOAD program header telling OS to map at 0x400000
3. Section data aligned to 16 bytes
4. Optional section headers (for debuggers, linkers)

## Parsing ELF Files

Use `readelf` or `objdump`:

```bash
$ readelf -h myprog
$ objdump -d myprog  # disassemble
$ file myprog        # identify format
```

Or Python:

```python
import struct
with open('myprog', 'rb') as f:
 magic = f.read(4)  # b'\x7fELF'
```

## Why ELF is Powerful

- **Portable:** Same format on any architecture
- **Extensible:** Can add custom sections
- **Efficient:** Memory-mapped loading, lazy binding
- **Secure:** Supports PIE (position-independent executables), RELRO

## References

- System V Application Binary Interface — AMD64 Architecture
- `man elf`
- https://refspecs.linuxfoundation.org/elf/elf.pdf

---

**Note:** This kit creates **minimal** ELFs. Production compilers (gcc/clang) add many more sections, proper symbol tables, and debug info.
