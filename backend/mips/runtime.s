# backend/mips/runtime.s
# ============================================================
# runtime.s — Rutinas de soporte (Tarea 4)
# Convenciones:
#   - $a0..$a3: args
#   - $v0: retorno
#   - Cada función usa prólogo/epílogo simples con $fp/$ra
#   - Strings: ASCII C-like (terminados en '\0')
# ============================================================

        .text

# ------------------------------------------------------------
# __alloc(nbytes) -> ptr
#   Reserva nbytes con sbrk (syscall 9)
#   a0=nbytes, v0=puntero
# ------------------------------------------------------------
        .globl __alloc
__alloc:
        addiu $sp, $sp, -16
        sw    $ra, 12($sp)
        sw    $fp,  8($sp)
        addu  $fp, $sp, $zero

        li    $v0, 9          # sbrk
        syscall               # v0 <- ptr

        lw    $ra, 12($sp)
        lw    $fp,  8($sp)
        addiu $sp, $sp, 16
        jr    $ra
        nop

# ------------------------------------------------------------
# __strlen(s) -> len
#   a0=char*; v0=length (sin contar '\0')
# ------------------------------------------------------------
        .globl __strlen
__strlen:
        move  $t0, $a0
        li    $v0, 0
__strlen_loop:
        lb    $t1, 0($t0)
        beq   $t1, $zero, __strlen_end
        nop
        addiu $t0, $t0, 1
        addiu $v0, $v0, 1
        b     __strlen_loop
        nop
__strlen_end:
        jr    $ra
        nop

# ------------------------------------------------------------
# __strcpy(dst, src) -> dst
#   Copia incluyendo '\0'
#   a0=dst, a1=src
# ------------------------------------------------------------
        .globl __strcpy
__strcpy:
        move  $t0, $a0      # dst
        move  $t1, $a1      # src
__strcpy_loop:
        lb    $t2, 0($t1)
        sb    $t2, 0($t0)
        beq   $t2, $zero, __strcpy_end
        nop
        addiu $t1, $t1, 1
        addiu $t0, $t0, 1
        b     __strcpy_loop
        nop
__strcpy_end:
        move  $v0, $a0      # retorna dst
        jr    $ra
        nop

# ------------------------------------------------------------
# __strcat_new(a, b) -> nuevo string "a"+"b"
#   a0=ptr a, a1=ptr b ; v0=ptr nuevo
# ------------------------------------------------------------
        .globl __strcat_new
__strcat_new:
        addiu $sp, $sp, -24
        sw    $ra, 20($sp)
        sw    $fp, 16($sp)
        addu  $fp, $sp, $zero

        # lenA = strlen(a0)
        move  $t0, $a0
        jal   __strlen
        nop
        move  $t1, $v0            # lenA

        # lenB = strlen(a1)
        move  $a0, $a1
        jal   __strlen
        nop
        move  $t2, $v0            # lenB

        addu  $t3, $t1, $t2       # lenA+lenB
        addiu $t3, $t3, 1         # + '\0'

        move  $a0, $t3
        jal   __alloc
        nop
        move  $t4, $v0            # dst

        # strcpy(dst, a)
        move  $a0, $t4
        move  $a1, $t0
        jal   __strcpy
        nop

        # dst+lenA
        addu  $t5, $t4, $t1
        # strcpy(dst+lenA, b)
        move  $a0, $t5
        move  $a1, $a1            # b ya está en a1
        jal   __strcpy
        nop

        move  $v0, $t4
        lw    $ra, 20($sp)
        lw    $fp, 16($sp)
        addiu $sp, $sp, 24
        jr    $ra
        nop

# ------------------------------------------------------------
# __int_to_str(i) -> ptr
#   Convierte entero con signo a string nuevo (buffer 32 bytes).
# ------------------------------------------------------------
        .globl __int_to_str
__int_to_str:
        addiu $sp, $sp, -32
        sw    $ra, 28($sp)
        sw    $fp, 24($sp)
        addu  $fp, $sp, $zero

        move  $t0, $a0        # n
        li    $t1, 0          # neg=0
        bltz  $t0, __i2s_neg
        nop
        b     __i2s_after_sign
        nop
__i2s_neg:
        li    $t1, 1
        subu  $t0, $zero, $t0
__i2s_after_sign:
        li    $a0, 32
        jal   __alloc
        nop
        move  $t2, $v0
        addiu $t3, $t2, 31
        sb    $zero, 0($t3)
        addiu $t3, $t3, -1

        beq   $t0, $zero, __i2s_zero
        nop
__i2s_digits:
        li    $t4, 10
        div   $t0, $t4
        mfhi  $t5
        mflo  $t0
        addiu $t5, $t5, 48
        sb    $t5, 0($t3)
        addiu $t3, $t3, -1
        bne   $t0, $zero, __i2s_digits
        nop
        b     __i2s_maybe_sign
        nop
__i2s_zero:
        li    $t5, 48
        sb    $t5, 0($t3)
        addiu $t3, $t3, -1
__i2s_maybe_sign:
        beq   $t1, $zero, __i2s_done
        nop
        li    $t5, 45
        sb    $t5, 0($t3)
        addiu $t3, $t3, -1
__i2s_done:
        addiu $t3, $t3, 1
        move  $v0, $t3

        lw    $ra, 28($sp)
        lw    $fp, 24($sp)
        addiu $sp, $sp, 32
        jr    $ra
        nop

# ------------------------------------------------------------
# print_str(s) y println_str(s)
# ------------------------------------------------------------
        .globl print_str
print_str:
        li    $v0, 4
        syscall
        jr    $ra
        nop

        .globl println_str
println_str:
        addiu $sp, $sp, -16
        sw    $ra, 12($sp)
        sw    $fp,  8($sp)
        addu  $fp, $sp, $zero

        li    $v0, 4
        syscall

        la    $a0, __rt_nl
        li    $v0, 4
        syscall

        lw    $ra, 12($sp)
        lw    $fp,  8($sp)
        addiu $sp, $sp, 16
        jr    $ra
        nop

# ------------------------------------------------------------
# newEstudiante(arg0, arg1, arg2) -> this
#   Reserva 16 bytes y llama a constructor$1(this, arg0, arg1, arg2)
#   Campos: nombre(ptr), edad(int), color(ptr), grado(int)
# ------------------------------------------------------------
        .globl newEstudiante
newEstudiante:
        addiu $sp, $sp, -24
        sw    $ra, 20($sp)
        sw    $fp, 16($sp)
        addu  $fp, $sp, $zero

        move  $t0, $a0     # arg0
        move  $t1, $a1     # arg1
        move  $t2, $a2     # arg2

        li    $a0, 16
        jal   __alloc
        nop
        move  $t3, $v0     # this

        sw    $zero, 0($t3)
        sw    $zero, 4($t3)
        sw    $zero, 8($t3)
        sw    $zero, 12($t3)

        move  $a0, $t3
        move  $a1, $t0
        move  $a2, $t1
        move  $a3, $t2
        jal   constructor$1
        nop

        move  $v0, $t3

        lw    $ra, 20($sp)
        lw    $fp, 16($sp)
        addiu $sp, $sp, 24
        jr    $ra
        nop

# ------------------------------------------------------------
# __exit(): syscall 10
# ------------------------------------------------------------
        .globl __exit
__exit:
        li    $v0, 10
        syscall

# -------------------- DATA del runtime ----------------------
        .data
__rt_nl:
        .asciiz "\n"
