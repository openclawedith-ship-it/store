.section .data
input_str: .asciz "Hello from ZETA Bare Metal"
.section .text
.global _start
_start:
 push %rbp
 mov %rsp, %rbp
 lea input_str(%rip), %rdi
 mov $1, %rax
 mov $1, %rdi
 mov %rdi, %rsi
 mov $30, %rdx
 syscall
 mov $60, %rax
 xor %rdi, %rdi
 syscall
 pop %rbp
 ret