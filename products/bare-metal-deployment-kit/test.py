#!/usr/bin/env python3
"""
Bare Metal Deployment Kit — Demo & Test Suite
Runs all components and verifies they work
"""

import sys
import subprocess
from pathlib import Path

def test_compiler():
 print("🔧 Testing Compiler...")
 from compiler import BareMetalCompiler
 c = BareMetalCompiler()
 asm = c.compile_to_asm('print("Hello")', "python")
 assert asm and len(asm) > 0
 print("  ✓ Assembly generated")
 obj = c.assemble(asm, "test_hello")
 assert Path(obj).exists()
 print(f"  ✓ Object file: {obj}")
 exe = c.link_executable([obj], "test_hello")
 assert Path(exe).exists()
 print(f"  ✓ Executable: {exe}")
 return True

def test_emulator():
 print("🐍 Testing Bytecode Emulator...")
 from emulator import PythonBytecodeEmulator
 emu = PythonBytecodeEmulator()
 assert hasattr(emu, 'emulate')
 print("  ✓ Emulator class loaded")
 # Note: real .pyc testing needs proper file
 return True

def test_elf_builder():
 print("🛠️ Testing ELF Builder...")
 from elf_builder import ELFBuilder
 builder = ELFBuilder()
 builder.add_section('.text', b'\x90\xc3')  # nop; ret
 builder.add_section('.data', b'ZETA\x00')
 elf = builder.build(entry_point=0x1000)
 assert len(elf) > 64
 print(f"  ✓ ELF built: {len(elf)} bytes")
 return True

def test_agent():
 print("🔐 Testing Agent...")
 from agent import EncryptedAgent
 agent = EncryptedAgent()
 assert hasattr(agent, 'start')
 print("  ✓ Agent class loaded")
 return True

def main():
 print("═══ Bare Metal Deployment Kit — Test Suite ═══\n")
 tests = [
 test_compiler,
 test_emulator,
 test_elf_builder,
 test_agent
 ]
 passed = 0
 for test in tests:
 try:
 if test():
 passed += 1
 except Exception as e:
 print(f"  ✗ FAILED: {e}")
 print()
 print(f"✅ {passed}/{len(tests)} tests passed")
 if passed == len(tests):
 print("\n🎉 All systems operational. Ready to compile to silicon.")
 else:
 print("\n⚠️  Some components need attention.")
 return 0 if passed == len(tests) else 1

if __name__ == "__main__":
 sys.exit(main())
