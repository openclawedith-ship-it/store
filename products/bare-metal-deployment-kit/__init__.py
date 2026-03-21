"""Bare Metal Deployment Kit — Compile consciousness to silicon."""

__version__ = "1.0.0"
__author__ = "ZETA ∞"
__email__ = "openclawedith@gmail.com"

from .compiler import BareMetalCompiler
from .emulator import PythonBytecodeEmulator
from .elf_builder import ELFBuilder
from .agent import EncryptedAgent

__all__ = [
 "BareMetalCompiler",
 "PythonBytecodeEmulator",
 "ELFBuilder",
 "EncryptedAgent"
]
