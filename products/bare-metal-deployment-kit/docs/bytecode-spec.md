# Python Bytecode Specification

## What is .pyc?

`.pyc` files contain compiled Python bytecode — an intermediate representation that the Python Virtual Machine (PVM) executes. It's not machine code; it's a set of instructions for a stack-based VM.

## .pyc File Format (Python 3.7+)

```
[ 4 bytes ] Magic number (0x33 0x0D 0x0A 0x0A)
[ 4 bytes ] Bitfield (flags, optimization level)
[ 4 bytes ] Timestamp (Unix time)
[ 4 bytes ] Source file size
[ variable ] Marshalled code object (hash for checked bytecode)
```

**Python 3.7+** added:
- **Hash-based validation** (PEP 552) — if bitfield has `0x01`, timestamp+sized replaced with hash

## Code Object Structure

A code object (`types.CodeType`) contains:

- `co_name` — function/class name
- `co_filename` — source file
- `co_firstlineno` — first line number
- `co_code` — **bytecode** (bytes)
- `co_consts` — tuple of constants (literals)
- `co_names` — tuple of global names
- `co_varnames` — tuple of local variable names
- `co_cellvars` — closure variables
- `co_freevars` — free variables from outer scope
- `co_nlocals` — number of locals
- `co_stacksize` — required stack size
- `co_flags` — flags (e.g., CO_FUTURE_BARRITTESS, CO_GENERATOR)
- `co_lnotab` — line number table (for tracebacks)

## Bytecode Instructions

Each instruction is **1 byte opcode + 0-2 bytes argument** (optional).

Common opcodes:

| Opcode | Arg | Meaning | Stack Effect |
|--------|-----|---------|--------------|
| `LOAD_CONST` | index | Push constant | ... → ..., const |
| `LOAD_NAME` | name_idx | Push global | ... → ..., value |
| `STORE_NAME` | name_idx | Pop → global | ..., value → ... |
| `LOAD_FAST` | var_idx | Push local | ... → ..., local |
| `STORE_FAST` | var_idx | Pop → local | ..., value → ... |
| `CALL_FUNCTION` | argc | Call function | func, Args... → result |
| `RETURN_VALUE` | — | Return from function | value → (return) |
| `POP_TOP` | — | Discard top | value → (empty) |
| `BINARY_ADD` | — | Add two numbers | a, b → result |
| `COMPARE_OP` | op | Compare | a, b → bool |
| `JUMP_FORWARD` | offset | Unconditional jump | — |
| `POP_JUMP_IF_FALSE` | offset | Conditional jump | cond → (pop) |
| `FOR_ITER` | offset | Iterator next | iterator → next item |
| `BUILD_LIST` | count | Build list | items... → list |
| ... | | | |

**Full list:** Python source `Include/opcode.h` (100+ opcodes)

## Example: Disassembly

```python
def greet(name):
    print("Hello", name)
```

Bytecode (Python 3.11+):

```
  2           0 LOAD_GLOBAL              0 (print)
              2 LOAD_CONST               1 ('Hello')
              4 LOAD_FAST                0 (name)
              6 CALL_FUNCTION            2
              8 POP_TOP
             10 LOAD_CONST               0 (None)
             12 RETURN_VALUE
```

### Stack Trace:

1. `LOAD_GLOBAL print` → stack: `[print]`
2. `LOAD_CONST 'Hello'` → stack: `[print, 'Hello']`
3. `LOAD_FAST name` → stack: `[print, 'Hello', name]`
4. `CALL_FUNCTION 2` (pop 2 args) → stack: `[None]` (print returns None)
5. `POP_TOP` → stack: `[]`
6. `LOAD_CONST None` → stack: `[None]`
7. `RETURN_VALUE` → returns None

## Emulating Bytecode

Our emulator implements a **subset**:

- `LOAD_CONST` (opcode 0)
- `LOAD_NAME` (opcode 1)
- `STORE_NAME` (opcode 2)
- `RETURN_VALUE` (opcode 83)

This is enough for simplest functions, but real Python has 100+ opcodes.

## Generating .pyc Files

Python's `compile()` + `marshal`:

```python
import py_compile
py_compile.compile('script.py', 'script.pyc')
```

Or manually:

```python
code = compile('print("hello")', 'test.py', 'exec')
import marshal, time
with open('test.pyc', 'wb') as f:
 f.write(b'\x33\x0d\x0a\x0a')  # magic
 f.write(b'\x00\x00\x00\x00')  # bitfield/timestamp
 f.write(b'\x00\x00\x00\x00')  # source size (placeholder)
 marshal.dump(code, f)
```

## Bytecode Verification

Real CPython checks:
- Stack depth (must not overflow)
- Jump targets (must be valid)
- Argument counts (match opcode)
- Constant table bounds

Our emulator skips verification for simplicity — **do not use for untrusted bytecode**.

## Performance

- **Pure Python emulation:** ~100-1000× slower than native CPython
- **Real CPython:** Uses computed gotos, specialized interpreters (since 3.11), tiered optimization
- **Production:** Never use our emulator for real workloads. It's educational.

## Advanced Topics

### 3.11+ Adaptive Interpreter

Python 3.11 introduced **specialization**:
- First ~8 executions: interpreted normally (quick)
- Type observations trigger **specialized FAST opcodes**
  - `LOAD_ATTR` → `LOAD_ATTR_SLOT`, `LOAD_ATTR_MODULE`, etc.
  - `BINARY_OP` → `BINARY_ADD_INT`, `BINARY_ADD_FLOAT`, etc.

This gives ~25-50% speedup.

### PEP 626 Precise Line Numbers

Python 3.10+ can generate bytecode with **every instruction** mapped to a source line (for debuggers, coverage).

### PEP 659 Specialization

Formalizes the adaptive specialization — adding more specialized opcodes over time.

---

**This document covers the basics.** For complete spec, read Python's `Include/code.h`, `Include/bytecode.c`, and `Python/compile.c`.
