# ============================================================
# A2 COST SCALING MODEL — COST AS FUNCTION OF EMPTY WEIGHT
# Result form:  Cost = (coefficient) * We
# ============================================================

import math

# ------------------------------------------------------------
# 1) Mach -> KTAS (Mach 1.6 @ 30,000 ft)
# ------------------------------------------------------------
def isa_temperature_K(alt_ft):
    T0 = 288.15      # K
    L  = 0.0065      # K/m
    h_m = alt_ft * 0.3048
    return T0 - L*h_m if h_m <= 11000 else 216.65

def mach_to_ktas(M, alt_ft):
    gamma = 1.4
    R = 287.05
    T = isa_temperature_K(alt_ft)
    a = math.sqrt(gamma * R * T)
    return M * a * 1.9438444924

Vmax_ktas = mach_to_ktas(1.6, 30000)

# ------------------------------------------------------------
# 2) Fixed program assumptions
# ------------------------------------------------------------
Q_total = 500
Q_5yr   = 500
Q_proto = 5

# Technology factors (from lecture table)
F_cert  = 1.00
F_comp  = 2.00
F_taper = 0.95
F_cf    = 1.03
F_press = 1.03
F_hye   = 1.00

# ------------------------------------------------------------
# 3) CPI escalation to ~2026 USD
# ------------------------------------------------------------
CPI_2012 = 229.594
CPI_2026 = 324.054      # Dec 2025 proxy
CPI = CPI_2026 / CPI_2012

# ------------------------------------------------------------
# 4) Labor rates for 2026
# ------------------------------------------------------------
year = 2026
R_ENG  = 2.576 * year - 5058
R_TOOL = 2.883 * year - 5666
R_MFG  = 2.316 * year - 4552

# ------------------------------------------------------------
# 5) Structural fraction: W_airframe = k * We
# ------------------------------------------------------------
k_struct = 0.45   # mid-range assumption

# ------------------------------------------------------------
# 6) COST COEFFICIENTS (symbolic in We)
# ------------------------------------------------------------

# Engineering cost coefficient
CENG_coeff = (
    0.083 *
    (k_struct ** 0.791) *
    (Vmax_ktas ** 1.521) *
    (Q_5yr ** 0.183) *
    F_cert * F_cf * F_comp * F_press * F_hye *
    R_ENG * CPI
)

# Development + flight test (also RDT&E)
CDEV_coeff = (
    0.06458 *
    (k_struct ** 0.873) *
    (Vmax_ktas ** 1.890) *
    (Q_proto ** 0.346) *
    F_cert * F_cf * F_comp * F_press * F_hye *
    CPI
)

CFT_coeff = (
    0.009646 *
    (k_struct ** 1.160) *
    (Vmax_ktas ** 1.3718) *
    (Q_proto ** 1.281) *
    F_cert * F_hye *
    CPI
)

# Tooling (distributed per aircraft)
CTOOL_coeff = (
    2.1036 *
    (k_struct ** 0.764) *
    (Vmax_ktas ** 0.899) *
    (Q_5yr ** 0.178) *
    (Q_total ** 0.066) *
    F_taper * F_cf * F_comp * F_press * F_hye *
    R_TOOL * CPI
) / Q_total

# Manufacturing per aircraft
CMFG_coeff = (
    20.2588 *
    (k_struct ** 0.740) *
    (Vmax_ktas ** 0.543) *
    (Q_total ** 0.524) *
    F_cert * F_cf * F_comp * F_hye *
    R_MFG * CPI
) / Q_total

# ------------------------------------------------------------
# 7) Final linearized results
# ------------------------------------------------------------
RDT_E_per_We = CENG_coeff + CDEV_coeff + CFT_coeff
UnitCost_per_We = CTOOL_coeff + CMFG_coeff

print("=== COST SCALING RESULTS ===")
print(f"Vmax = {Vmax_ktas:.1f} KTAS (Mach 1.6 @ 30,000 ft)")
print()
print(f"RDT&E cost ≈ ${RDT_E_per_We:,.0f} × We")
print(f"Unit cost  ≈ ${UnitCost_per_We:,.0f} × We")
print()
print("Example:")
print("If We = 30,000 lb:")
print(f"  RDT&E ≈ ${RDT_E_per_We*30000/1e9:.2f} B")
print(f"  Unit cost ≈ ${UnitCost_per_We*30000/1e6:.1f} M")
