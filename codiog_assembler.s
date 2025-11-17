.data
STR_0: .asciiz ""
STR_1: .asciiz "Hola, mi nombre es "
STR_2: .asciiz "Ahora tengo "
STR_3: .asciiz " años."
STR_4: .asciiz " está estudiando en "
STR_5: .asciiz " año en la Universidad del Valle de Guatemala (UVG)."
STR_6: .asciiz "\\n"
STR_7: .asciiz " es par\\n"
STR_8: .asciiz " es impar\\n"
STR_9: .asciiz "Resultado de la expresión: "
STR_10: .asciiz "Promedio (entero): "
STR_11: .asciiz "Prueba: Fibonacci recursivo\\n"
STR_12: .asciiz "Fib("
STR_13: .asciiz ") = "
# FUNC toString_START:

# --- Función toString ---
.text
toString:
  addiu $sp, $sp, -272
  sw   $ra, 268($sp)
  sw   $fp, 264($sp)
  addu $fp, $sp, $zero
# ActivationRecord toString
  addu $t0, $a0, $zero
  la   $t2, STR_0
  addu $t1, $t2, $zero
  addu $v0, $t1, $zero
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
# FUNC toString_END:
# EndFunc toString
# FUNC printInteger_START:

# --- Función printInteger ---
.text
printInteger:
  addiu $sp, $sp, -272
  sw   $ra, 268($sp)
  sw   $fp, 264($sp)
  addu $fp, $sp, $zero
# ActivationRecord printInteger
  addu $t0, $a0, $zero
  addu $t1, $t0, $zero
  addu $v0, $t1, $zero
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
# FUNC printInteger_END:
# EndFunc printInteger
# FUNC printString_START:

# --- Función printString ---
.text
printString:
  addiu $sp, $sp, -272
  sw   $ra, 268($sp)
  sw   $fp, 264($sp)
  addu $fp, $sp, $zero
# ActivationRecord printString
  addu $t0, $a0, $zero
  addu $t1, $t0, $zero
  addu $v0, $t1, $zero
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
# FUNC printString_END:
# EndFunc printString
# FUNC fibonacci_START:

# --- Función fibonacci ---
.text
fibonacci:
  addiu $sp, $sp, -272
  sw   $ra, 268($sp)
  sw   $fp, 264($sp)
  addu $fp, $sp, $zero
# ActivationRecord fibonacci
  addu $t0, $a0, $zero
  addu $t1, $t0, $zero
  li   $t3, 1
  addu $t2, $t3, $zero
  slt  $t1, $t2, $t1
  xori $t1, $t1, 1
  beq  $t1, $zero, L1
  nop
  addu $t1, $t0, $zero
  addu $v0, $t1, $zero
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
L1:
  li   $t1, 1
  subu $t2, $t0, $t1
  addu $t3, $t2, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t3, $zero
  jal fibonacci
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t2, $v0, $zero
  li   $t4, 2
  subu $t5, $t0, $t4
  addu $t6, $t5, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  jal fibonacci
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t5, $v0, $zero
  addu $t7, $t8, $zero
  addu $t9, $t1, $zero
  addu $t3, $t7, $zero
  addu $t4, $t9, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t3, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t7, $v0, $zero
  addu $t9, $t6, $zero
  addu $v0, $t9, $zero
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
# FUNC fibonacci_END:
# EndFunc fibonacci
# FUNC constructor_START:

# --- Función constructor ---
.text
constructor:
  addiu $sp, $sp, -272
  sw   $ra, 268($sp)
  sw   $fp, 264($sp)
  addu $fp, $sp, $zero
# ActivationRecord constructor
  addu $t0, $a1, $zero
  addu $t1, $a2, $zero
  addu $t0, $t0, $zero
  addu $t1, $t1, $zero
  lw   $t2, 8($a0)
  sw   $t2, 8($a0)
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
# FUNC constructor_END:
# EndFunc constructor
# FUNC saludar_START:

# --- Función saludar ---
.text
saludar:
  addiu $sp, $sp, -264
  sw   $ra, 260($sp)
  sw   $fp, 256($sp)
  addu $fp, $sp, $zero
# ActivationRecord saludar
  la   $t1, STR_1
  addu $t0, $t1, $zero
  lw   $t2, 0($a0)
  addu $t3, $t0, $zero
  addu $t4, $t2, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t3, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t0, $v0, $zero
  addu $v0, $t0, $zero
  lw   $ra, 260($sp)
  lw   $fp, 256($sp)
  addiu $sp, $sp, 264
  jr   $ra
  nop
# FUNC saludar_END:
# EndFunc saludar
# FUNC incrementarEdad_START:

# --- Función incrementarEdad ---
.text
incrementarEdad:
  addiu $sp, $sp, -272
  sw   $ra, 268($sp)
  sw   $fp, 264($sp)
  addu $fp, $sp, $zero
# ActivationRecord incrementarEdad
  addu $t0, $a0, $zero
  lw   $t1, 4($a0)
  sw   $t1, 4($a0)
  la   $t3, STR_2
  addu $t2, $t3, $zero
  lw   $t4, 4($a0)
  addu $t5, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t5, $zero
  jal toString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t4, $v0, $zero
  addu $t6, $t2, $zero
  addu $t7, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  addu $a1, $t7, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t2, $v0, $zero
  la   $t8, STR_3
  addu $t4, $t8, $zero
  addu $t9, $t2, $zero
  addu $t1, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t9, $zero
  addu $a1, $t1, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t2, $v0, $zero
  addu $v0, $t2, $zero
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
# FUNC incrementarEdad_END:
# EndFunc incrementarEdad
# FUNC constructor_START:

# --- Función constructor$1 ---
.text
constructor$1:
  addiu $sp, $sp, -272
  sw   $ra, 268($sp)
  sw   $fp, 264($sp)
  addu $fp, $sp, $zero
# ActivationRecord constructor
  addu $t0, $a1, $zero
  addu $t1, $a2, $zero
  addu $t2, $a3, $zero
  addu $t0, $t0, $zero
  addu $t1, $t1, $zero
  lw   $t3, 8($a0)
  sw   $t3, 8($a0)
  addu $t2, $t2, $zero
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
# FUNC constructor_END:
# EndFunc constructor
# FUNC estudiar_START:

# --- Función estudiar ---
.text
estudiar:
  addiu $sp, $sp, -264
  sw   $ra, 260($sp)
  sw   $fp, 256($sp)
  addu $fp, $sp, $zero
# ActivationRecord estudiar
  lw   $t0, 0($a0)
  la   $t2, STR_4
  addu $t1, $t2, $zero
  addu $t3, $t0, $zero
  addu $t4, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t3, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t0, $v0, $zero
  lw   $t1, 12($a0)
  addu $t5, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t5, $zero
  jal toString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t6, $t0, $zero
  addu $t7, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  addu $a1, $t7, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t0, $v0, $zero
  la   $t8, STR_5
  addu $t1, $t8, $zero
  addu $t9, $t0, $zero
  addu $t2, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t9, $zero
  addu $a1, $t2, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t0, $v0, $zero
  addu $v0, $t0, $zero
  lw   $ra, 260($sp)
  lw   $fp, 256($sp)
  addiu $sp, $sp, 264
  jr   $ra
  nop
# FUNC estudiar_END:
# EndFunc estudiar
# FUNC promedioNotas_START:

# --- Función promedioNotas ---
.text
promedioNotas:
  addiu $sp, $sp, -272
  sw   $ra, 268($sp)
  sw   $fp, 264($sp)
  addu $fp, $sp, $zero
# ActivationRecord promedioNotas
  addu $t0, $a0, $zero
  addu $t1, $a1, $zero
  addu $t2, $a2, $zero
  addu $t3, $a3, $zero
  lw   $t4, 272($fp)
  lw   $t5, 276($fp)
  addu $t6, $t0, $zero
  addu $t7, $t1, $zero
  addu $t8, $t6, $zero
  addu $t9, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t8, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t7, $t2, $zero
  addu $t8, $t6, $zero
  addu $t9, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t8, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t7, $t3, $zero
  addu $t8, $t6, $zero
  addu $t9, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t8, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t7, $t4, $zero
  addu $t8, $t6, $zero
  addu $t9, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t8, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t7, $t5, $zero
  addu $t8, $t6, $zero
  addu $t9, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t8, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  li   $t8, 6
  addu $t7, $t8, $zero
  div  $t6, $t7
  mflo $t6
  addu $t7, $t9, $zero
  addu $v0, $t7, $zero
  lw   $ra, 268($sp)
  lw   $fp, 264($sp)
  addiu $sp, $sp, 272
  jr   $ra
  nop
# FUNC promedioNotas_END:
# EndFunc promedioNotas
  la   $t1, STR_0
  addu $t0, $t1, $zero
  li   $t3, 4
  addu $t2, $t3, $zero
  addu $t4, $t2, $zero
  li   $t5, 15
  addu $t2, $t5, $zero
  addu $t6, $t2, $zero
  lw   $t7, 0($a0)
  addu $t2, $t7, $zero
  addu $t8, $t2, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  addu $a1, $t6, $zero
  addu $a2, $t8, $zero
  jal newEstudiante
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t2, $v0, $zero
  li   $t1, 4
  addu $t9, $t1, $zero
  addu $t3, $t9, $zero
  li   $t5, 15
  addu $t9, $t5, $zero
  addu $t7, $t9, $zero
  addu $t9, $t4, $zero
  addu $t6, $t9, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t3, $zero
  addu $a1, $t7, $zero
  addu $a2, $t6, $zero
  jal newEstudiante
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t9, $v0, $zero
  li   $t1, 4
  addu $t8, $t1, $zero
  addu $t5, $t8, $zero
  li   $t3, 15
  addu $t8, $t3, $zero
  addu $t7, $t8, $zero
  addu $t8, $t6, $zero
  addu $t1, $t8, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t5, $zero
  addu $a1, $t7, $zero
  addu $a2, $t1, $zero
  jal newEstudiante
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t8, $v0, $zero
  addu $t3, $t5, $zero
  addu $t1, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t1, $zero
  jal saludar
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t0, $t3, $zero
  addu $t0, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t0, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t0, STR_6
  addu $t1, $t0, $zero
  addu $t0, $t3, $zero
  addu $t2, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t2, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t5, $zero
  addu $t2, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t2, $zero
  jal estudiar
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t0, $t3, $zero
  addu $t2, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t2, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t0, STR_6
  addu $t1, $t0, $zero
  addu $t2, $t3, $zero
  addu $t0, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t2, $zero
  addu $a1, $t0, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t5, $zero
  li   $t2, 6
  addu $t1, $t2, $zero
  addu $t0, $t1, $zero
  addu $t2, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t2, $zero
  jal incrementarEdad
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t0, $t3, $zero
  addu $t2, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t2, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t0, STR_6
  addu $t1, $t0, $zero
  addu $t2, $t3, $zero
  addu $t0, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t2, $zero
  addu $a1, $t0, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t5, $zero
  addu $t0, $t2, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  jal saludar
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t0, $t3, $zero
  addu $t4, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t4, STR_6
  addu $t1, $t4, $zero
  addu $t0, $t3, $zero
  addu $t4, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t5, $zero
  addu $t0, $t2, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  jal estudiar
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t4, $t3, $zero
  addu $t0, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  addu $a1, $t0, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t4, STR_6
  addu $t1, $t4, $zero
  addu $t0, $t3, $zero
  addu $t4, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t5, $zero
  li   $t0, 7
  addu $t1, $t0, $zero
  addu $t4, $t1, $zero
  addu $t0, $t2, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  addu $a1, $t0, $zero
  jal incrementarEdad
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t4, $t3, $zero
  addu $t0, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  addu $a1, $t0, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t4, STR_6
  addu $t1, $t4, $zero
  addu $t0, $t3, $zero
  addu $t4, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t0, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t5, $zero
  addu $t4, $t0, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  jal saludar
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t4, $t3, $zero
  addu $t9, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t9, STR_6
  addu $t1, $t9, $zero
  addu $t4, $t3, $zero
  addu $t9, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t5, $zero
  addu $t4, $t0, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  jal estudiar
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t9, $t3, $zero
  addu $t4, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t9, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t9, STR_6
  addu $t1, $t9, $zero
  addu $t4, $t3, $zero
  addu $t9, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t5, $zero
  li   $t4, 6
  addu $t1, $t4, $zero
  addu $t9, $t1, $zero
  addu $t4, $t0, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t9, $zero
  addu $a1, $t4, $zero
  jal incrementarEdad
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t9, $t3, $zero
  addu $t4, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t9, $zero
  addu $a1, $t4, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t9, STR_6
  addu $t1, $t9, $zero
  addu $t4, $t3, $zero
  addu $t9, $t1, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  li   $t4, 1
  addu $t3, $t4, $zero
L3:
  addu $t1, $t9, $zero
  li   $t6, 12
  addu $t4, $t6, $zero
  slt  $t1, $t4, $t1
  xori $t1, $t1, 1
  beq  $t1, $zero, L4
  nop
  addu $t1, $t9, $zero
  li   $t6, 2
  addu $t4, $t6, $zero
  div  $t1, $t4
  mfhi $t1
  li   $t6, 0
  addu $t4, $t6, $zero
  xor  $t1, $t1, $t4
  sltiu $t1, $t1, 1
  beq  $t1, $zero, L5
  nop
  addu $t1, $t5, $zero
  addu $t4, $t9, $zero
  addu $t6, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  jal toString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t4, $v0, $zero
  addu $t6, $t1, $zero
  addu $t8, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  addu $a1, $t8, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  la   $t8, STR_7
  addu $t4, $t8, $zero
  addu $t6, $t1, $zero
  addu $t8, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  addu $a1, $t8, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t5, $t1, $zero
  b L6
  nop
L5:
  addu $t1, $t5, $zero
  addu $t4, $t9, $zero
  addu $t6, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  jal toString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t4, $v0, $zero
  addu $t8, $t1, $zero
  addu $t6, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t8, $zero
  addu $a1, $t6, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  la   $t8, STR_8
  addu $t4, $t8, $zero
  addu $t6, $t1, $zero
  addu $t8, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  addu $a1, $t8, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t5, $t1, $zero
L6:
  addu $t1, $t9, $zero
  li   $t6, 1
  addu $t4, $t6, $zero
  addu $t8, $t1, $zero
  addu $t6, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t8, $zero
  addu $a1, $t6, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t9, $t1, $zero
  b L3
  nop
L4:
  lw   $t1, 4($t8)
  li   $t6, 2
  addu $t4, $t6, $zero
  mul  $t1, $t1, $t4
  li   $t6, 5
  addu $t4, $t6, $zero
  li   $t7, 3
  addu $t6, $t7, $zero
  subu $t4, $t4, $t6
  li   $t7, 2
  addu $t6, $t7, $zero
  div  $t4, $t6
  mflo $t4
  addu $t7, $t1, $zero
  addu $t2, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t7, $zero
  addu $a1, $t2, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t1, $v0, $zero
  addu $t4, $t5, $zero
  la   $t2, STR_9
  addu $t6, $t2, $zero
  addu $t7, $t4, $zero
  addu $t2, $t6, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t7, $zero
  addu $a1, $t2, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t4, $v0, $zero
  addu $t6, $t7, $zero
  addu $t2, $t6, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t2, $zero
  jal toString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t2, $t4, $zero
  addu $t0, $t6, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t2, $zero
  addu $a1, $t0, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t4, $v0, $zero
  la   $t0, STR_6
  addu $t6, $t0, $zero
  addu $t2, $t4, $zero
  addu $t0, $t6, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t2, $zero
  addu $a1, $t0, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t4, $v0, $zero
  addu $t5, $t4, $zero
  li   $t2, 0
  addu $t4, $t2, $zero
  li   $t0, 94
  addu $t6, $t0, $zero
  addu $t2, $t6, $zero
  li   $t0, 95
  addu $t6, $t0, $zero
  addu $t0, $t6, $zero
  li   $t3, 100
  addu $t6, $t3, $zero
  addu $t3, $t6, $zero
  li   $t9, 98
  addu $t6, $t9, $zero
  addu $t9, $t6, $zero
  li   $t8, 95
  addu $t6, $t8, $zero
  addu $t8, $t6, $zero
  li   $t1, 99
  addu $t6, $t1, $zero
  addu $t1, $t6, $zero
  addu $t7, $t7, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addiu $sp, $sp, -12
  sw   $t8, 0($sp)
  sw   $t1, 4($sp)
  sw   $t7, 8($sp)
  addu $a0, $t2, $zero
  addu $a1, $t0, $zero
  addu $a2, $t3, $zero
  addu $a3, $t9, $zero
  jal promedioNotas
  nop
  addiu $sp, $sp, 12
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t2, $t6, $zero
  addu $t6, $t5, $zero
  la   $t3, STR_10
  addu $t0, $t3, $zero
  addu $t9, $t6, $zero
  addu $t8, $t0, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t9, $zero
  addu $a1, $t8, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t0, $t2, $zero
  addu $t1, $t0, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t1, $zero
  jal toString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t0, $v0, $zero
  addu $t3, $t6, $zero
  addu $t9, $t0, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t3, $zero
  addu $a1, $t9, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  la   $t8, STR_6
  addu $t0, $t8, $zero
  addu $t1, $t6, $zero
  addu $t3, $t0, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t1, $zero
  addu $a1, $t3, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t5, $t6, $zero
  addu $t6, $t5, $zero
  la   $t9, STR_11
  addu $t0, $t9, $zero
  addu $t8, $t6, $zero
  addu $t1, $t0, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t8, $zero
  addu $a1, $t1, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t6, $v0, $zero
  addu $t5, $t6, $zero
  li   $t3, 20
  addu $t6, $t3, $zero
  li   $t9, 0
  addu $t0, $t9, $zero
L7:
  addu $t8, $t1, $zero
  addu $t3, $t9, $zero
  slt  $t8, $t3, $t8
  xori $t8, $t8, 1
  beq  $t8, $zero, L8
  nop
  addu $t8, $t1, $zero
  addu $t4, $t8, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t4, $zero
  jal fibonacci
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t8, $v0, $zero
  addu $t3, $t5, $zero
  la   $t7, STR_12
  addu $t4, $t7, $zero
  addu $t7, $t3, $zero
  addu $t2, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t7, $zero
  addu $a1, $t2, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t4, $t1, $zero
  addu $t2, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t2, $zero
  jal toString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t4, $v0, $zero
  addu $t7, $t3, $zero
  addu $t2, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t7, $zero
  addu $a1, $t2, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t7, STR_13
  addu $t4, $t7, $zero
  addu $t2, $t3, $zero
  addu $t7, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t2, $zero
  addu $a1, $t7, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t4, $t2, $zero
  addu $t7, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t7, $zero
  jal toString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t4, $v0, $zero
  addu $t7, $t3, $zero
  addu $t6, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t7, $zero
  addu $a1, $t6, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  la   $t6, STR_6
  addu $t4, $t6, $zero
  addu $t7, $t3, $zero
  addu $t6, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t7, $zero
  addu $a1, $t6, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t5, $t3, $zero
  addu $t3, $t1, $zero
  li   $t7, 1
  addu $t4, $t7, $zero
  addu $t6, $t3, $zero
  addu $t7, $t4, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  addu $a1, $t7, $zero
  jal __strcat_new
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero
  addu $t1, $t3, $zero
  b L7
  nop
L8:
  addu $t3, $t5, $zero
  addu $t6, $t3, $zero
  addiu $sp, $sp, -40
  sw   $t0, 0($sp)
  sw   $t1, 4($sp)
  sw   $t2, 8($sp)
  sw   $t3, 12($sp)
  sw   $t4, 16($sp)
  sw   $t5, 20($sp)
  sw   $t6, 24($sp)
  sw   $t7, 28($sp)
  sw   $t8, 32($sp)
  sw   $t9, 36($sp)
  addu $a0, $t6, $zero
  jal printString
  nop
  lw   $t0, 0($sp)
  lw   $t1, 4($sp)
  lw   $t2, 8($sp)
  lw   $t3, 12($sp)
  lw   $t4, 16($sp)
  lw   $t5, 20($sp)
  lw   $t6, 24($sp)
  lw   $t7, 28($sp)
  lw   $t8, 32($sp)
  lw   $t9, 36($sp)
  addiu $sp, $sp, 40
  addu $t3, $v0, $zero