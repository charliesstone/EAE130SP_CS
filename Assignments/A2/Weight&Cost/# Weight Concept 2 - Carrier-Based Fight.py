# Weight Concept 2 - Carrier-Based Fighter Sizing

import math
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# 1. CREW DEFINITION (Carrier-based fighter)
# ============================================================

n_crew = 1                      # single-seat fighter 
W_crew_per = 200                # lb / person (including gear)
W_crew = n_crew * W_crew_per
n_engines = 2


# ============================================================
# 2. PAYLOAD DEFINITIONS (RFP-based)
# ============================================================

# ---- Fixed internal avionics & sensors (RFP specified) ----
W_avionics = 2500               # lb (internal, always carried)

# ---- Air-to-Air ordnance ----
W_AIM120 = 350                    # lb 
W_AIM9X  = 186                    # lb 

W_A2A = 6 * W_AIM120 + 2 * W_AIM9X

# ---- Strike ordnance (fill in weights later) ----
W_MK83 = 1000                      # lb (placeholder)

W_strike = 4 * W_MK83 + 2 * W_AIM9X


# ============================================================
# 3. SELECT MISSION PAYLOAD
# ============================================================
# Choose ONE sizing mission at a time

mission_type = "BOTH"            # options: "A2A" or "STRIKE" or "BOTH"

if mission_type == "A2A":
    W_payload = W_A2A
elif mission_type == "STRIKE":
    W_payload = W_strike
elif mission_type == "BOTH":
    W_payload = W_A2A + W_strike
else:
    raise ValueError("Invalid mission type selected")


# ============================================================
# 4. MISSION PARAMETERS (to be filled per mission)
# ============================================================

R_nmi     = 700        # combat radius (nm) – 700 or 1000
E_hr      = 0.50        # loiter / combat time (hr) (30min to 1 hr)
c_tsfc    = 0.75        # thrust specific fuel consumption (1/hr) (assumed)
LD_cruise = 12        # lift-to-drag ratio - 12 to 14
V_kt      = 460        # cruise speed (knots) - 460 to 480

# Breguet fractions
Wf_Wi_cruise = math.exp(-R_nmi * c_tsfc / (V_kt * LD_cruise)) if V_kt > 0 else 1.0
Wf_Wi_loiter = math.exp(-E_hr * c_tsfc / LD_cruise) if LD_cruise > 0 else 1.0


# ============================================================
# 5. NON-BREGUET SEGMENT WEIGHT FRACTIONS
# ============================================================

segment_fracs = {
    "Warmup": 0.990,
    "Taxi":  0.990,
    "Takeoff": 0.990,
    "Climb":   0.960,
    "Descent": 0.990,
    "Landing": 0.995
}

W_end_W0 = 1.0
for frac in segment_fracs.values():
    W_end_W0 *= frac

W_end_W0 *= Wf_Wi_cruise
W_end_W0 *= Wf_Wi_loiter

fuel_frac_mission = 1.0 - W_end_W0

# Carrier reserve factor (loiter + traps + margin)
reserve_factor  = 1.25
fuel_frac_total = reserve_factor * fuel_frac_mission


# ============================================================
# 6. ITERATIVE TOGW SOLUTION
# ============================================================

# Empty-weight fraction model (Raymer-style)
A = 1.05
C = -0.05

error     = 1e-6
W0_history = []
W0        = 90000          # initial guess near carrier limit
delta     = 2 * error


while delta > error:
    W0_history.append(W0)
    We_W0 = A * (W0 ** C)
    W0_new = (W_payload + W_crew + W_avionics) / (1 - fuel_frac_total - We_W0)

    delta = abs(W0_new - W0) / abs(W0_new)
    W0 = W0_new

W0_history = np.array(W0_history)
We = We_W0 * W0

# Plot Convergence
plt.figure(figsize=(8,4))
plt.title('Weight Estimate Convergence')
plt.xlabel("Iteration")
plt.ylabel("W0 (kg)")
plt.plot(W0_history, label='W0', linestyle='-', linewidth=2, marker=None, markersize=8)
plt.grid(True)
plt.legend(loc='best')
plt.show()

# ============================================================
# 7. OUTPUT
# ============================================================

print(f"Mission type: {mission_type}")
print(f"W_crew      = {W_crew:,.0f} lb")
print(f"W_avionics  = {W_avionics:,.0f} lb")
print(f"W_payload   = {W_payload:,.0f} lb")
print(f"Fuel fraction (total) = {fuel_frac_total:.4f}")
print(f"Estimated TOGW W0     = {W0:,.0f} lb")
print(f"Estimated empty weight We = {We:,.0f} lb")
print(f"Empty-weight fraction We/W0 = {We/W0:.4f}")





