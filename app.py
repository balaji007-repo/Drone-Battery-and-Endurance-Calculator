import streamlit as st
import pandas as pd

st.set_page_config(page_title="UAV Endurance Calculator", layout="wide")

st.title("Drone Endurance & Battery Calculator")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Hardware & Weight")
    cells = st.slider("No. of Cells (S)", 2, 14, 6)
    motors = st.slider("No. of Motors", 4, 8, 4)
    target_auw = st.number_input("Target All Up Weight (grams)", value=5000)
    
    st.markdown("**Motor Thrust Data**")
    w1 = st.number_input("Test Weight 1 (grams/motor)", value=500)
    i1 = st.number_input("Current at Test Weight 1 (A)", value=3.0)
    w2 = st.number_input("Test Weight 2 (grams/motor)", value=1000)
    i2 = st.number_input("Current at Test Weight 2 (A)", value=8.0)

with col2:
    st.subheader("Avionics Power Ratings")
    p_fc = st.slider("Flight Controller (W)", 0.0, 10.0, 2.0)
    p_comp = st.slider("Flight Computer (W)", 0.0, 50.0, 15.0)
    p_gps = st.slider("GPS (W)", 0.0, 5.0, 1.0)
    p_cam = st.slider("Camera (W)", 0.0, 20.0, 5.0)
    
    margin_pct = st.slider("Battery Safety Margin (%)", 0, 40, 20)
    margin = margin_pct / 100.0

st.subheader("Mission Profiles")
c1, c2, c3 = st.columns(3)
t1 = c1.number_input("Target Flight Time 1 (mins)", value=15)
t2 = c2.number_input("Target Flight Time 2 (mins)", value=30)
t3 = c3.number_input("Target Flight Time 3 (mins)", value=45)

b1, b2, b3 = st.columns(3)
bat1 = b1.number_input("Test Battery 1 (mAh)", value=8000)
bat2 = b2.number_input("Test Battery 2 (mAh)", value=16000)
bat3 = b3.number_input("Test Battery 3 (mAh)", value=22000)

# Base Calculations
nom_voltage = cells * 3.7
weight_per_motor = target_auw / motors

slope = (i2 - i1) / (w2 - w1) if w2 != w1 else 0
motor_current = i1 + slope * (weight_per_motor - w1)
total_motor_current = motor_current * motors

total_avionics_power = p_fc + p_comp + p_gps + p_cam
avionics_current = total_avionics_power / nom_voltage
total_hover_current = total_motor_current + avionics_current
hover_power_w = total_hover_current * nom_voltage

st.markdown("---")
st.subheader("Results")

# 1. Required Battery Capacity for Target Times
req_cap_1 = (t1 * total_hover_current) / (60 * (1 - margin)) * 1000
req_cap_2 = (t2 * total_hover_current) / (60 * (1 - margin)) * 1000
req_cap_3 = (t3 * total_hover_current) / (60 * (1 - margin)) * 1000

st.write("**1. Required Battery Capacity (mAh) for Target Flight Times**")
req_df = pd.DataFrame({
    "Flight Time (mins)": [t1, t2, t3],
    "Required Capacity (mAh)": [round(req_cap_1, 2), round(req_cap_2, 2), round(req_cap_3, 2)]
})
st.table(req_df)

# Advanced Simulation Logic
def get_cell_voltage(soc):
    if soc > 0.90:
        return 4.0 + (soc - 0.90) * 2.0 
    elif soc > 0.15:
        return 3.7 + (soc - 0.15) * 0.4
    else:
        return 3.2 + (soc / 0.15) * 0.5

def sim_flight(capacity_mah):
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
        i_draw = hover_power_w / v_total
        
        current_cap -= i_draw * (1.0 / 3600.0)
        t_sec += 1
        
    return round(t_sec / 60.0, 2)

# 2. Compare Standard vs Advanced Endurance
st.write("**2. Endurance Comparison: Standard vs Advanced Simulation**")

results = []
for bat in [bat1, bat2, bat3]:
    cap_ah = bat / 1000.0
    std_time = (cap_ah * (1 - margin) / total_hover_current) * 60
    sim_time = sim_flight(bat)
    
    results.append({
        "Battery (mAh)": bat,
        "Standard Method (mins)": round(std_time, 2),
        "Simulated Method (mins)": sim_time,
        "Difference (mins)": round(sim_time - std_time, 2)
    })

st.table(pd.DataFrame(results))