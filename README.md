# Drone Battery and Endurance Calculator

A professional, interactive web-based engineering tool built with **Streamlit** to analyze and simulate UAV (unmanned aerial vehicle) flight times. 

This calculator computes required battery configurations for specific targets and evaluates battery performance side-by-side across two different All Up Weight (AUW) configurations using both standard formulas and a dynamic voltage-drop simulation.

## Features
* **Dual AUW Metrics:** Compare performance profiles for a base/lightweight setup versus a fully loaded/max payload configuration simultaneously.
* **Avionics Overhead Accounting:** Factor in standalone power consumption from Flight Controllers, Companion Computers, GPS units, and Cameras.
* **Dual-Method Endurance Analysis:** * *Standard Method:* Pure linear capacity vs. current draw calculation.
  * *Advanced Simulation:* Real-time integration iterating over a multi-stage Lithium-Polymer discharge voltage curve to catch power drops as capacity fades.

---

## How to Run This Project Locally

### Prerequisites
Make sure you have Python installed on your system. 

### Step 1: Clone the Repository
Open your terminal or PowerShell and run:
```bash
git clone [https://github.com/balaji007-repo/Drone-Battery-and-Endurance-Calculator.git](https://github.com/balaji007-repo/Drone-Battery-and-Endurance-Calculator.git)
cd Drone-Battery-and-Endurance-Calculator