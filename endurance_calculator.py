import streamlit as st
import pandas as pd

st.set_page_config(page_title="UAV Endurance Calculator", layout="wide")

st.title("Drone Endurance & Battery Calculator")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hardware Configuration")
    cells = st.slider("No. of Cells (S)", 2, 14, 12)
    motors = st.slider("No. of Motors", 4, 8, 4)
    
    st.markdown("**Weight Option 1 (Lightweight / Base)**")
    w1 = st.number_input("AUW 1 - Motor Thrust (g/motor)", value=500)
    i1 = st.number_input("Current per Motor at AUW 1 (A)", value=5.0)
    
    st.markdown("**Weight Option 2 (Heavy / Max Payload)**")
    w2 = st.number_input("AUW 2 - Motor Thrust (g/motor)", value=1000)
    i2 = st.number_input("Current per Motor at AUW 2 (A)", value=12.0)

with col2:
    st.subheader("Avionics Power Ratings")
    p_fc = st.slider("Flight Controller (W)", 0.0, 10.0, 5.0)
    p_comp = st.slider("Flight Computer (W)", 0.0, 50.0, 25.0)
    p_gps = st.slider("GPS (W)", 0.0, 5.0, 2.0)
    p_cam = st.slider("Camera (W)", 0.0, 20.0, 10.0)
    
    margin_pct = st.slider("Battery Safety Margin (%)", 0, 40, 20)
    margin = margin_pct / 100.0

st.subheader("Mission Profiles & Battery Inputs")
c1, c2, c3 = st.columns(3)
t1 = c1.number_input("Target Time 1 (mins)", value=35)
t2 = c2.number_input("Target Time 2 (mins)", value=40)
t3 = c3.number_input("Target Time 3 (mins)", value=45)

b1, b2, b3 = st.columns(3)
bat1 = b1.number_input("Test Battery 1 (mAh)", value=22000)
bat2 = b2.number_input("Test Battery 2 (mAh)", value=27000)
bat3 = b3.number_input("Test Battery 3 (mAh)", value=30000)

# System Math
nom_voltage = cells * 3.7
total_auw1 = w1 * motors
total_auw2 = w2 * motors

total_avionics_power = p_fc + p_comp + p_gps + p_cam
avionics_current = total_avionics_power / nom_voltage

# Hover states for both weights
i_hover1 = (i1 * motors) + avionics_current
i_hover2 = (i2 * motors) + avionics_current

p_hover1 = i_hover1 * nom_voltage
p_hover2 = i_hover2 * nom_voltage

st.markdown("---")
st.subheader("Analysis & Summary Metrics")

# Section 1: Required Capacities
st.write("### 1. Required Battery Capacity (mAh) for Target Flight Times")

req_cap_auw1_t1 = (t1 * i_hover1) / (60 * (1 - margin)) * 1000
req_cap_auw1_t2 = (t2 * i_hover1) / (60 * (1 - margin)) * 1000
req_cap_auw1_t3 = (t3 * i_hover1) / (60 * (1 - margin)) * 1000

req_cap_auw2_t1 = (t1 * i_hover2) / (60 * (1 - margin)) * 1000
req_cap_auw2_t2 = (t2 * i_hover2) / (60 * (1 - margin)) * 1000
req_cap_auw2_t3 = (t3 * i_hover2) / (60 * (1 - margin)) * 1000

req_df = pd.DataFrame({
    "Target Flight Time (mins)": [t1, t2, t3],
    f"Req. Capacity at AUW 1 ({total_auw1}g)": [round(req_cap_auw1_t1, 1), round(req_cap_auw1_t2, 1), round(req_cap_auw1_t3, 1)],
    f"Req. Capacity at AUW 2 ({total_auw2}g)": [round(req_cap_auw2_t1, 1), round(req_cap_auw2_t2, 1), round(req_cap_auw2_t3, 1)]
})
st.table(req_df)

# Advanced Simulation Engine
def get_cell_voltage(soc):
    if soc > 0.90:
        return 4.0 + (soc - 0.90) * 2.0 
    elif soc > 0.15:
        return 3.7 + (soc - 0.15) * 0.4
    else:
        return 3.2 + (soc / 0.15) * 0.5

def sim_flight(capacity_mah, total_power):
    cap_ah = capacity_mah / 1000.0
    usable_ah = cap_ah * (1 - margin)
    current_cap = cap_ah
    t_sec = 0
    
    while current_cap > (cap_ah - usable_ah):
        soc = current_cap / cap_ah
        v_cell = get_cell_voltage(soc)
        if v_cell <= 3.5:
            break
        v_total = v_cell * cells
        i_draw = total_power / v_total
        current_cap -= i_draw * (1.0 / 3600.0)
        t_sec += 1
    return round(t_sec / 60.0, 2)

# Section 2: Method Comparison Across Weights
st.write("### 2. Flight Endurance Comparison Matrix")
res_auw1 = []
res_auw2 = []

for bat in [bat1, bat2, bat3]:
    cap_ah = bat / 1000.0
    
    # AUW 1 Calculations
    std_t1 = (cap_ah * (1 - margin) / i_hover1) * 60
    sim_t1 = sim_flight(bat, p_hover1)
    res_auw1.append({
        "Battery (mAh)": bat,
        "Standard (mins)": round(std_t1, 2),
        "Simulated (mins)": sim_t1,
        "Diff (mins)": round(sim_t1 - std_t1, 2)
    })
    
    # AUW 2 Calculations
    std_t2 = (cap_ah * (1 - margin) / i_hover2) * 60
    sim_t2 = sim_flight(bat, p_hover2)
    res_auw2.append({
        "Battery (mAh)": bat,
        "Standard (mins)": round(std_t2, 2),
        "Simulated (mins)": sim_t2,
        "Diff (mins)": round(sim_t2 - std_t2, 2)
    })

out_col1, out_col2 = st.columns(2)

with out_col1:
    st.markdown(f"**Endurance Metrics for AUW 1 ({total_auw1} grams)**")
    st.table(pd.DataFrame(res_auw1))

with out_col2:
    st.markdown(f"**Endurance Metrics for AUW 2 ({total_auw2} grams)**")
    st.table(pd.DataFrame(res_auw2))