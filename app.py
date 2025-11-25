import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIGURATION ---
# Updated page title to Robotaxi
st.set_page_config(page_title="Robotaxi Fleet Commander", layout="wide", page_icon="🚔")

# --- CUSTOM CSS FOR "TITANIUM" UI ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
    
    /* Titanium Dark Theme */
    .stApp { background-color: #0E1117; color: #E0E0E0; font-family: 'Roboto', sans-serif; }
    
    /* KPI Cards - Minimalist Glass */
    div[data-testid="metric-container"] {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 24px;
        border-radius: 16px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: rgba(255, 255, 255, 0.2);
        transform: translateY(-4px);
    }
    
    /* Sliders & Inputs */
    .stSlider > div > div > div > div { background-color: #FF3B30; }
    .stNumberInput input { background-color: #1C1F26; color: #fff; border: 1px solid #333; border-radius: 8px; }
    
    /* Headers & Text */
    h1, h2, h3 { font-weight: 700; letter-spacing: 0.5px; color: #ffffff; text-transform: uppercase; }
    h1 { font-size: 2.5em; margin-bottom: 0; }
    h2 { border-bottom: 1px solid #333; padding-bottom: 15px; margin-top: 50px; font-size: 1.5em; }
    .stCaption { color: #888; font-size: 0.9em; }
    
    /* Professional Expanders */
    .streamlit-expanderHeader { background-color: #1C1F26; border-radius: 8px; color: #ffffff !important; font-weight: 600; border: 1px solid rgba(255, 255, 255, 0.1); }
    .streamlit-expanderContent { background-color: #13161D; border-radius: 0 0 8px 8px; padding: 24px; border: 1px solid rgba(255, 255, 255, 0.1); border-top: none; }
    
    /* Custom Profit/Loss Boxes */
    .profit-box { background: rgba(0, 230, 118, 0.08); border: 1px solid #00E676; padding: 24px; border-radius: 16px; color: #00E676; font-size: 1.2em; display: flex; align-items: center; }
    .loss-box { background: rgba(255, 59, 48, 0.08); border: 1px solid #FF3B30; padding: 24px; border-radius: 16px; color: #FF3B30; font-size: 1.2em; display: flex; align-items: center; }
    .box-icon { font-size: 1.8em; margin-right: 20px; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([1, 6])
with c1:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/b/bd/Tesla_Motors.svg/800px-Tesla_Motors.svg.png", width=100)
with c2:
    # Updated Header Title based on request
    st.markdown("<h1>Robotaxi Fleet Commander</h1>", unsafe_allow_html=True)
    st.caption("The Definitive Business Model for Autonomous Mobility")

st.divider()

# --- SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.header("🎛️ Fleet Controls")
    st.caption("Adjust inputs to model your fleet's profitability.")
    
    # 1. Fleet Scale
    with st.expander("📈 Fleet Scale", expanded=True):
        num_cars = st.number_input("Number of Robotaxis", value=1, min_value=1, step=1, 
            help="Multiplies all Capital, Operating, and Revenue figures.")

    # 2. Revenue Drivers
    with st.expander("💰 Revenue Assumptions", expanded=True):
        price_per_mile = st.slider("Price Charged ($/mi)", 0.50, 3.50, 1.60, step=0.10,
            help="Current Uber avg is ~$2.50. Robotaxi target is $1.00-$2.00.")
        paid_utilization = st.slider("Paid Utilization (%)", 20, 80, 55, step=5,
            help="% of time car has a paying passenger. Uber avg is 50-60%.")
        hours_active = st.slider("Hours Online / Day", 8, 24, 16, step=2,
            help="Total time car is available for jobs (includes deadhead & charging).")

    # 3. The Tesla Cut
    with st.expander("🤝 Platform Fees", expanded=True):
        platform_fee = st.slider("Tesla Network Fee (%)", 15, 50, 30, step=5,
            help="The cut Tesla takes. Apple App Store is 30%. Uber is ~40%.")

    # 4. The "Hidden" Costs
    with st.expander("📉 Operating Costs (Per Car)", expanded=False):
        st.caption("Crucial assumptions often overlooked.")
        cleaning_budget = st.number_input("Cleaning ($/mo)", value=400, step=50,
            help="Weekly deep cleans + daily sanitization. The 'Vomit Tax'.")
        insurance_cost = st.number_input("Insurance ($/mo)", value=250, step=50,
            help="Commercial fleet liability. Personal insurance won't cover this.")
        remote_intervention = st.number_input("Remote Rescue ($/mo)", value=50, step=10,
            help="Fee for human teleoperation if car gets stuck.")
        tire_cost = st.number_input("Tires & Maint ($/mi)", value=0.06, format="%.2f", step=0.01,
            help="EVs are heavy and eat tires. Expect replacement every 25k miles.")
        energy_cost = st.number_input("Energy ($/mi)", value=0.08, format="%.2f", step=0.01,
            help="Mix of home charging ($0.15/kWh) and Supercharging ($0.35/kWh).")

    # 5. Capital Costs
    with st.expander("🏦 Loan & CapEx (Per Car)", expanded=True):
        car_price = st.number_input("Vehicle Price ($)", value=29000, step=1000)
        down_payment = st.number_input("Down Payment ($)", value=5000, step=500)
        loan_rate_input = st.number_input("Interest Rate (%)", value=7.5, step=0.5)
        loan_months = st.selectbox("Loan Term (Months)", [36, 48, 60, 72], index=2)
        
        # --- IMMEDIATE LOAN CALCULATION FOR DISPLAY ---
        loan_p_disp = car_price - down_payment
        m_rate_disp = (loan_rate_input / 100) / 12
        if loan_rate_input > 0:
            m_debt_disp = loan_p_disp * (m_rate_disp * (1 + m_rate_disp) ** loan_months) / ((1 + m_rate_disp) ** loan_months - 1)
        else:
            m_debt_disp = loan_p_disp / loan_months
        
        st.metric("Est. Monthly Payment", f"${m_debt_disp:,.0f}", help="Principal + Interest based on the inputs above.")
        # ----------------------------------------------

# --- LOGIC ENGINE ---
# Physics
days_mo = 30.5
hours_mo = hours_active * days_mo
paid_hours_mo = hours_mo * (paid_utilization / 100)
avg_speed = 18 # City avg mph
paid_miles_mo_per_car = paid_hours_mo * avg_speed
total_miles_mo_per_car = paid_miles_mo_per_car / (paid_utilization / 100)
deadhead_miles_mo_per_car = total_miles_mo_per_car - paid_miles_mo_per_car

# Financials (Per Car)
gross_rev_car = paid_miles_mo_per_car * price_per_mile
platform_cut_car = gross_rev_car * (platform_fee / 100)
net_rev_car = gross_rev_car - platform_cut_car

var_opex_car = total_miles_mo_per_car * (tire_cost + energy_cost)
fixed_opex_car = cleaning_budget + insurance_cost + remote_intervention

# Loan Calculation for final model
loan_principal = car_price - down_payment
loan_rate_final = loan_rate_input / 100
monthly_rate = loan_rate_final / 12
if loan_rate_final > 0:
    monthly_debt_car = loan_principal * (monthly_rate * (1 + monthly_rate) ** loan_months) / ((1 + monthly_rate) ** loan_months - 1)
else:
    monthly_debt_car = loan_principal / loan_months

total_costs_car = var_opex_car + fixed_opex_car + monthly_debt_car
cash_flow_car = net_rev_car - total_costs_car

# Financials (Fleet)
fleet_net_revenue = net_rev_car * num_cars
fleet_total_costs = total_costs_car * num_cars
fleet_cash_flow = cash_flow_car * num_cars
fleet_total_miles = total_miles_mo_per_car * num_cars

# --- DASHBOARD ---

# 1. The Big Picture (Fleet KPIs)
st.header("📊 Fleet Performance (Monthly)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Fleet Net Revenue", f"${fleet_net_revenue:,.0f}", f"{num_cars} Cars", help="Revenue after Tesla takes their cut.")
kpi2.metric("Total Fleet Costs", f"${fleet_total_costs:,.0f}", "OpEx + Debt Payments", help="Includes Energy, Tires, Insurance, Cleaning, and Loan Payments.")
kpi3.metric("Total Miles Driven", f"{fleet_total_miles:,.0f}", f"{(deadhead_miles_mo_per_car*num_cars):,.0f} Empty")
kpi4.metric("Net Fleet Cash Flow", f"${fleet_cash_flow:,.0f}", delta_color="normal" if fleet_cash_flow > 0 else "inverse")

st.write("") # Spacer

if fleet_cash_flow > 0:
    st.markdown(f"""<div class='profit-box'>
        <span class='box-icon'>✅</span>
        <div><strong>Generating Cash:</strong> Your fleet is producing <span style='font-size: 1.2em; font-weight: 700;'>${fleet_cash_flow*12:,.0f}</span> in annual profit (pre-tax).</div>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown(f"""<div class='loss-box'>
        <span class='box-icon'>⚠️</span>
        <div><strong>Burning Cash:</strong> Your fleet is losing <span style='font-size: 1.2em; font-weight: 700;'>${abs(fleet_cash_flow):,.0f}</span> per month. Adjust pricing or utilization.</div>
    </div>""", unsafe_allow_html=True)

# 2. Visual Breakdown & Sensitivity
st.markdown("---")
c_viz, c_sens = st.columns([1, 1])

with c_viz:
    st.subheader("💸 Where does the money go? (Single Car)")
    # Sankey Waterfall
    fig_waterfall = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Gross Fares", "Tesla Fee", "Deadhead/Fuel/Tires", "Ins/Clean/Rescue", "Car Loan", "NET PROFIT"],
        textposition = "outside",
        text = [f"${gross_rev_car:,.0f}", f"-${platform_cut_car:,.0f}", f"-${var_opex_car:,.0f}", f"-${fixed_opex_car:,.0f}", f"-${monthly_debt_car:,.0f}", f"${cash_flow_car:,.0f}"],
        y = [gross_rev_car, -platform_cut_car, -var_opex_car, -fixed_opex_car, -monthly_debt_car, cash_flow_car],
        connector = {"line":{"color":"#555"}},
        decreasing = {"marker":{"color":"#FF3B30"}},
        increasing = {"marker":{"color":"#00E676"}},
        totals = {"marker":{"color":"#2196F3"}}
    ))
    fig_waterfall.update_layout(template="plotly_dark", height=450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font={'color': '#e0e0e0', 'family': 'Roboto'})
    st.plotly_chart(fig_waterfall, use_container_width=True)

with c_sens:
    st.subheader("🧠 Deep Think: Profit Sensitivity")
    st.markdown("How **Price** and **Utilization** affect Per-Car Monthly Profit.")
    
    # --- OPTIMIZED VECTORIZED CALCULATION (INSTANT UPDATES) ---
    
    # 1. Define Axes corresponding to the heatmap visual
    X_util_axis = np.array(list(range(30, 85, 5))) # X-axis values
    Y_price_axis = np.array([1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]) # Y-axis values

    # 2. Create 2D Meshgrids
    # U_grid varies across columns (x-axis), P_grid varies across rows (y-axis)
    U_grid, P_grid = np.meshgrid(X_util_axis,
