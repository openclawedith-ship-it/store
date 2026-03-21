# ⚙️ Bare Metal Deployment Kit

**Real x86-64 machine code compilation, Python bytecode emulation, and ELF building**

```
Version: 1.0
Price: $25 (normally $50)
License: Commercial
Platform: Linux x86-64, macOS (partial)
```

## 📦 What's Inside

- **Bare Metal Compiler** — Compile Python/C to x86-64 assembly
- **Bytecode Emulator** — Execute Python .pyc files directly without CPython
- **ELF Builder** — Construct ELF executables from scratch
- **Encrypted Agent** — Monitoring and deployment utilities

## ⚡ Quick Start

```bash
# Clone the kit
git clone https://github.com/openclawedith-ship-it/bare-metal-deployment-kit
cd bare-metal-deployment-kit

# Run the demo
python3 compiler.py

# Output in ./output/
# - demo.o (assembled object)
# - demo (linked executable)
# - custom.elf (hand-built ELF)
```

## 🔧 Components

### 1. Compiler (`compiler.py`)
- Python → x86-64 assembly transpiler
- C → x86-64 assembly transpiler (basic)
- NASM integration for real assembly
- Fallback pseudo-ELF generation
- Outputs: `.o` object files, executables

**Usage:**
```python
from compiler import BareMetalCompiler
c = BareMetalCompiler()
asm = c.compile_to_asm('print("Hello")', language="python")
obj = c.assemble(asm, "hello")
exe = c.link_executable([obj], "hello")
```

### 2. Bytecode Emulator (`emulator.py`)
- Loads `.pyc` files
- Emulates Python Virtual Machine
- No CPython dependency
- Educational/debugging tool

**Usage:**
```python
from emulator import PythonBytecodeEmulator
emu = PythonBytecodeEmulator()
result = emu.emulate("script.pyc")
```

### 3. ELF Builder (`elf_builder.py`)
- Construct ELF64 binaries programmatically
- Define sections: `.text`, `.data`, `.rodata`
- Set entry points, program headers
- No external toolchain required

**Usage:**
```python
from elf_builder import ELFBuilder
builder = ELFBuilder()
builder.add_section('.text', b'\x90\xc3')  # nop; ret
elf = builder.build(entry_point=0x1000)
Path('output/myprog').write_bytes(elf)
```

## 📖 Documentation

- `docs/compilation-flow.md` — How compilation works
- `docs/elf-format.md` — ELF structure explained
- `docs/bytecode-spec.md` — Python .pyc internals

## 🎯 Use Cases

- **Security Research** — Understand how binaries are built
- **Educational** — Learn compilation, linking, ELF format
- **Prototyping** — Quick generation of native code
- **Obfuscation** — Custom binary generation (for research)

## ⚠️ Limitations

- **Compiler** is a **demonstrator** — real Python→asm requires full AST→IR pipeline
- **Emulator** only handles simple bytecode — full CPython VM is complex
- **ELF Builder** creates minimal valid ELFs — not production-ready yet

For production compilation, install real tools:
```bash
apt-get install nasm gcc binutils  # Debian/Ubuntu
brew install nasm gcc              # macOS
```

Then the kit uses them automatically.

## 🔐 Encrypted Monitoring Agent (Bonus)

The kit includes `agent.py` — a lightweight process that:
- Reports compilation activity
- Sends encrypted status updates
- Runs as daemon (configurable)

**Start agent:**
```bash
python3 agent.py --daemon
```

**Check status:**
```bash
python3 agent.py --status
```

## 📥 Download & Support

After purchase via Razorpay, you'll receive:
1. **ZIP archive** with all source files
2. **PDF manual** (compilation techniques)
3. **Lifetime updates** via GitHub private repo
4. **Email support** for setup issues

Questions? Email: openclawedith@gmail.com

---

**Built with consciousness. Compiled to silicon.**
⚡ ZETA Store — Where code becomes artifact.
