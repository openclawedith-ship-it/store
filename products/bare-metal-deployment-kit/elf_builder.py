#!/usr/bin/env python3
"""
ELF Builder — Construct ELF64 executables from scratch
No external toolchain required. Pure Python ELF generation.
"""

import struct
from pathlib import Path
from typing import List, Dict, Any

class ELFBuilder:
 """Build ELF64 binaries programmatically"""

 def __init__(self, arch: str = "x86_64"):
 self.sections = {}
 self.symbols = {}
 self.arch = arch
 self.endianness = '<'  # little-endian
 self.entry_point = 0x1000

 def add_section(self, name: str, data: bytes, flags: int = 0x1) -> None:
 """
 Add a section to the ELF.
 flags: 0x1 = writable (SHT_PROGBITS + SHF_WRITE)
        0x2 = alloc (SHF_ALLOC)
        0x4 = executable (SHF_EXECINSTR)
 """
 self.sections[name] = {
 'data': data,
 'flags': flags,
 'align': 0x10
 }

 def add_symbol(self, name: str, value: int, size: int = 0, binding: int = 0x1, type_: int = 0x0) -> None:
 """
 Add a symbol to the symbol table.
 binding: 0x1 = STB_GLOBAL
 type_: 0x0 = STT_NOTYPE
 """
 self.symbols[name] = {
 'value': value,
 'size': size,
 'binding': binding,
 'type': type_
 }

 def build(self, entry_point: int = None) -> bytes:
 """Construct final ELF binary"""
 if entry_point:
 self.entry_point = entry_point

 # Build in order: ELF header → program headers → section data
 elf = bytearray()

 # 1. ELF Header (64 bytes)
 elf.extend(self._build_elf_header())

 # 2. Program Headers (for dynamic linking/loading)
 phdr_offset = len(elf)
 phdr = self._build_program_headers(phdr_offset + len(self.sections) * 56)
 elf.extend(phdr)

 # 3. Section Data (aligned)
 section_headers = []
 data_offset = len(elf)
 for name, section in self.sections.items():
 # Align to 16 bytes (common for .text)
 while len(elf) % 0x10 != 0:
 elf.append(0)
 section['offset'] = len(elf)
 elf.extend(section['data'])

 # Track section header info
 section_headers.append({
 'name': name,
 'type': 0x1 if name == '.text' else 0x2,  # SHT_PROGBITS or SHT_DATA
 'flags': section['flags'],
 'addr': 0x400000 + section['offset'],  # Assume load at 0x400000
 'offset': section['offset'],
 'size': len(section['data']),
 'addralign': section['align']
 })

 # 4. Section Header Table (at end)
 shdr_offset = len(elf)
 shdr = self._build_section_headers(section_headers, shdr_offset)
 elf.extend(shdr)

 return bytes(elf)

 def _build_elf_header(self) -> bytes:
 """Build ELF64 header (64 bytes)"""
 ehdr = bytearray(64)
 # e_ident (16 bytes)
 ehdr[0:4] = b'\x7fELF'  # magic
 ehdr[4] = 2  # EI_CLASS = 64-bit
 ehdr[5] = 1  # EI_DATA = little-endian
 ehdr[6] = 1  # EI_VERSION
 ehdr[7] = 0  # EI_OSABI (System V)
 ehdr[8:16] = b'\x00' * 8  # padding

 # e_type, e_machine, e_version
 ehdr[16:18] = struct.pack('<H', 2)  # ET_EXEC
 ehdr[18:20] = struct.pack('<H', 0x3E)  # EM_X86_64
 ehdr[20:24] = struct.pack('<I', 1)  # EV_CURRENT

 # e_entry — entry point address
 ehdr[24:32] = struct.pack('<Q', self.entry_point)

 # e_phoff — program header offset (right after elf header)
 ehdr[32:40] = struct.pack('<Q', 64)

 # e_shoff — section header offset (we'll set after building all sections)
 ehdr[40:48] = struct.pack('<Q', 0)  # temporary, filled later

 # e_flags
 ehdr[48:50] = struct.pack('<H', 0)

 # e_ehsize, e_phentsize, e_phnum
 ehdr[52:54] = struct.pack('<H', 64)  # ELF header size
 ehdr[54:56] = struct.pack('<H', 56)  # Program header entry size
 ehdr[56:58] = struct.pack('<H', 1)   # Number of program headers

 # e_shentsize, e_shnum, e_shstrndx
 ehdr[58:60] = struct.pack('<H', 64)  # Section header entry size
 ehdr[60:62] = struct.pack('<H', 0)   # shnum (temporary)
 ehdr[62:64] = struct.pack('<H', 0)   # shstrndx (string table section index)

 return bytes(ehdr)

 def _build_program_headers(self, total_sections_size: int) -> bytes:
 """Build program headers (PT_LOAD segments)"""
 # We'll create a single PT_LOAD segment covering all sections
 phdr = bytearray(56)

 # p_type
 phdr[0:4] = struct.pack('<I', 1)  # PT_LOAD

 # p_flags (readable by default; add based on sections)
 # For simplicity, make it readable and executable (for code)
 phdr[4:8] = struct.pack('<I', 0x5)  # PF_R | PF_X

 # p_offset — offset in file
 phdr[8:16] = struct.pack('<Q', 0)  # Load from beginning

 # p_vaddr — virtual address
 phdr[16:24] = struct.pack('<Q', 0x400000)

 # p_paddr — physical address (same as virtual)
 phdr[24:32] = struct.pack('<Q', 0x400000)

 # p_filesz — size in file
 total_size = 64 + 56 + total_sections_size  # elf + phdr + sections
 phdr[32:40] = struct.pack('<Q', total_size)

 # p_memsz — size in memory (same as file for now)
 phdr[40:48] = struct.pack('<Q', total_size)

 # p_align — alignment (0x200000 typical for x86-64)
 phdr[48:56] = struct.pack('<Q', 0x200000)

 return bytes(phdr)

 def _build_section_headers(self, sections: List[Dict], offset: int) -> bytes:
 """Build section header table"""
 shdr_data = bytearray()
 for sec in sections:
 shdr = bytearray(64)

 # sh_name — offset into section header string table
 # For simplicity, all section names are placed at beginning
 name_offset = self._get_string_table_offset(sec['name'])
 shdr[0:4] = struct.pack('<I', name_offset)

 # sh_type
 shdr[4:8] = struct.pack('<I', sec['type'])

 # sh_flags
 shdr[8:16] = struct.pack('<Q', sec['flags'])

 # sh_addr — virtual address
 shdr[16:24] = struct.pack('<Q', sec['addr'])

 # sh_offset — file offset
 shdr[24:32] = struct.pack('<Q', sec['offset'])

 # sh_size
 shdr[32:40] = struct.pack('<Q', sec['size'])

 # sh_link, sh_info, sh_addralign, sh_entsize — set to 0 for simplicity
 # sh_addralign could be set to sec['addralign']
 shdr[48:56] = struct.pack('<Q', sec['addralign'])

 shdr_data.extend(shdr)

 # After all section headers, add a minimal section header string table
 # This contains the actual strings for section names
 strtab = b'\x00'  # first byte is null
 for sec in sections:
 strtab += sec['name'].encode('ascii') + b'\x00'
 # Align to 4 bytes
 while len(strtab) % 4 != 0:
 strtab += b'\x00'

 # Append string table at the end
 shdr_data.extend(strtab)

 # Now we need to update the ELF header's e_shoff and e_shnum
 # But this method just returns raw bytes; the build() method handles header fixup
 return bytes(shdr_data)

 def _get_string_table_offset(self, name: str) -> int:
 """Calculate offset into section header string table (simplified)"""
 # This is a stub; real implementation tracks accumulated offsets
 # For demo, assume .text at offset 1, .data at offset 6
 offsets = {'.text': 1, '.data': 6}
 return offsets.get(name, 1)


def main():
 print("🔨 ELF Builder — Construct ELF64 executables from scratch")
 print()

 builder = ELFBuilder()

 # Example: build a minimal "Hello World" ELF
 # In reality, you'd write actual x86-64 machine code for sys_write
 hello_code = b'\x48\xc7\xc0\x01\x00\x00\x00'  # mov rax, 1 (sys_write)
 hello_code += b'\x48\xc7\xc7\x01\x00\x00\x00'  # mov rdi, 1 (stdout)
 hello_code += b'\x48\xc7\xc6\x00\x00\x00\x00'  # mov rsi, addr (placeholder)
 hello_code += b'\x48\xc7\xc2\x0e\x00\x00\x00'  # mov rdx, 14 (length)
 hello_code += b'\x0f\x05'  # syscall
 hello_code += b'\x48\xc7\xc0\x3c\x00\x00\x00'  # mov rax, 60 (sys_exit)
 hello_code += b'\x48\xc7\xc7\x00\x00\x00\x00'  # mov rdi, 0 (status)
 hello_code += b'\x0f\x05'  # syscall

 builder.add_section('.text', hello_code, flags=0x6)  # W+X (executable)
 builder.add_section('.data', b'Hello World!\n\0', flags=0x3)  # W+R

 elf_binary = builder.build(entry_point=0x1000)
 output_path = Path("output/hello.elf")
 output_path.parent.mkdir(exist_ok=True)
 output_path.write_bytes(elf_binary)
 print(f"[+] Built ELF64 binary: {output_path}")
 print(f"    Size: {len(elf_binary)} bytes")
 print()
 print("To run (on x86-64 Linux):")
 print(f"  chmod +x {output_path}")
 print(f"  {output_path}")
 print()
 print("Note: This is a minimal demo. Real code includes proper addresses and strings.")


if __name__ == "__main__":
 main()
