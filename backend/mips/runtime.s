# =========================================================
# runtime.s  —  Rutinas de apoyo para MARS/SPIM
# Convención:
#   - Entrada por $a0..$a3 según corresponda
#   - Retorno en $v0 cuando aplique
#   - No preserva $t0..$t9 (temporales)
#   - Cada rutina hace prolog/epilog mínimo
# =========================================================

    .data
RT_NEWLINE:     .asciiz "\n"
RT_TRUE:        .asciiz "true"
RT_FALSE:       .asciiz "false"
RT_SPACE:       .asciiz " "

    .text

    .globl _print_int
_print_int:
    # $a0 = entero
    li   $v0, 1          # print_int
    syscall
    jr   $ra
    nop

    .globl _print_char
_print_char:
    # $a0 = código ASCII (0..255)
    li   $v0, 11         # print_char
    syscall
    jr   $ra
    nop

    .globl _print_string
_print_string:
    # $a0 = dirección a string ASCIIZ
    li   $v0, 4          # print_string
    syscall
    jr   $ra
    nop

    .globl _print_bool
_print_bool:
    # $a0 = 0 ó 1
    beq  $a0, $zero, _pb_false
    nop
    la   $a0, RT_TRUE
    li   $v0, 4
    syscall
    jr   $ra
    nop
_pb_false:
    la   $a0, RT_FALSE
    li   $v0, 4
    syscall
    jr   $ra
    nop

    .globl _println
_println:
    # Imprime salto de línea
    la   $a0, RT_NEWLINE
    li   $v0, 4
    syscall
    jr   $ra
    nop

    .globl _print_space
_print_space:
    la   $a0, RT_SPACE
    li   $v0, 4
    syscall
    jr   $ra
    nop

    .globl _read_int
_read_int:
    # Lee entero desde stdin -> $v0
    li   $v0, 5          # read_int
    syscall
    jr   $ra
    nop

    .globl _malloc
_malloc:
    # $a0 = cantidad de bytes -> $v0 = ptr
    li   $v0, 9          # sbrk
    syscall
    jr   $ra
    nop

    .globl _exit
_exit:
    li   $v0, 10         # exit
    syscall
