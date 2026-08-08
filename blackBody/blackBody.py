# =============================================================================
# Code Author / Maintainer: 
#   Pau Fonseca i Casas, Ph.D. <pau@fib.upc.edu>
#   Universitat Politècnica de Catalunya
#   Dept. Statistics and Operations Research
# 
# This code is part of Theory-5, developed by:
#   Jorge Luis Silva de Barcellos
#   Pau Fonseca i Casas, Ph.D.
# =============================================================================

import math

# =============================================================================
# Input estimates  — adjust to match your measurements
# =============================================================================
a_est   = 1 / 137.035999084   # fine-structure constant α
cmb_est = 2.725962684               # CMB temperature estimate [K]  (theory: ≈ e ≈ 2.71828)

# =============================================================================
# Derived parameters
# =============================================================================
p_d    = 1 / math.log(cmb_est)   # math.log = natural logarithm (ln)
p_d_bb = 1 / 125

# =============================================================================
# Temperature error: T_err = e^( e^((1 - x) + 1) - e + 1 ) - e
# Evaluated for x = p_d, 1/p_d, p_d_bb, 1/p_d_bb
# =============================================================================
e = math.e

T_err_pd      = e ** ((e ** ((1 - p_d)     + 1) - e**1) + e**0) - e
T_err_bb      = e ** ((e ** ((1 - p_d_bb)   + 1) - e**1) + e**0) - e

# =============================================================================
# Results
# =============================================================================
print(f"p_d               = {p_d}")
print(f"p_d_bb            = {p_d_bb}")
print()
print(f"T_err(p_d)        = {T_err_pd}")
print(f"T_err(p_d_bb)     = {T_err_bb}")
