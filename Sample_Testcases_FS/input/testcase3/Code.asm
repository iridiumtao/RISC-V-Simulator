# Custom testcase
# Load an immediate value into x1
lw      x1, #0              # x1 = 10

# Write data to x2
addi    x2, x1, 5           # x2 = x1 + 5 -> x2 = 10 + 5 = 15

# Read from x2, which is written by the previous instruction
add     x3, x1, x2           # x3 = x1 + x2 -> x3 = 10 + 15 = 25

# Write to x3
addi    x3, x3, 1            # x3 = x3 + 1 -> x3 = 25 + 1 = 26

# Read from x3 (write-after-read hazard)
sub     x4, x3, x2           # x4 = x3 - x2 -> x4 = 26 - 15 = 11

# Write to x1 (write-after-write hazard)
addi    x1, x1, 5            # x1 = x1 + 5 -> x1 = 10 + 5 = 15

# Read from x1 (read-after-write hazard)
xor     x5, x1, x3           # x5 = x1 * x3 -> x5 = 15 xor 26 = 21


/* In Binary
00000000000000000000000010000011
00000000010100001000000100010011
00000000001000001000000110110011
00000000000100011000000110010011
01000000001000011000001000110011
00000000010100001000000010010011
00000000001100001100001010110011
*/