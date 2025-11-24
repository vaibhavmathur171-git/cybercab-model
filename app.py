import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Cybercab Fleet Commander", layout="wide", page_icon="🚔")

# --- CUSTOM CSS FOR "DELIGHTFUL" UI ---
st.markdown("""
<style>
    /* Modern Dark Theme */
    .stApp { background-color: #0a0a0a; color: #e0e0e0; font-family: 'Inter', sans-serif; }
    
    /* KPI Cards */
    div[data-testid="metric-container"] {
        background-color: #1a1a1a;
        border: 1px solid #333;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.5);
        transition: all 0.3s ease;
    }
    div[data-testid="metric-container"]:hover {
        border-color: #E31937;
        transform: translateY(-2px);
    }
    
    /* Sliders & Inputs */
    .stSlider > div > div > div > div { background-color: #E31937; }
    .stNumberInput input { background-color: #1a1a1a; color: #fff; border: 1px solid #333; border-radius: 8px; }
    
    /* Headers & Text */
    h1, h2, h3 { font-weight: 700; letter-spacing: -0.5px; }
    h1 { color: #E31937; }
    h2 { border-bottom: 2px solid #333; padding-bottom: 15px; margin-top: 30px; }
    .highlight { color: #E31937; font-weight: bold; }
    
    /* Expanders */
    .streamlit-expanderHeader { background-color: #1a1a1a; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🚔 Cybercab Fleet Commander")
    st.markdown("### The Business of Autonomous Mobility")
with c2:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_logo.png", width=80)

st.divider()

# --- SIDEBAR: CONTROL CENTER ---
with st.sidebar:
    st.header("🎛️ Fleet Controls")
    
    # 1. Fleet Scale
    with st.expander("📈 Fleet Scale", expanded=True):
        num_cars = st.number_input("Number of Cybercabs", value=1, min_value=1, step=1, 
            help="Multiplies all CapEx, OpEx, and Revenue.")

    # 2. Revenue Drivers
    with st.expander("💰 Revenue Assumptions", expanded=True):
        price_per_mile = st.slider("Price Charged ($/mi)", 0.50, 3.50, 1.60, step=0.10,
            help="Uber is ~$2.50. Robotaxi target is $1.00-$2.00.")
        paid_utilization = st.slider("Paid Utilization (%)", 20, 80, 55, step=5,
            help="% of time car has a paying passenger. Uber avg is 50-60%.")
        hours_active = st.slider("Hours Online / Day", 8, 24, 16, step=2,
            help="Total time car is available for jobs (includes deadhead).")

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
    with st.expander("🏦 Loan & CapEx (Per Car)", expanded=False):
        car_price = st.number_input("Vehicle Price ($)", value=29000, step=1000)
        down_payment = st.number_input("Down Payment ($)", value=5000, step=500)
        loan_rate = st.number_input("Interest Rate (%)", value=7.5, step=0.5) / 100
        loan_months = st.selectbox("Loan Term (Months)", [36, 48, 60, 72], index=2)

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

loan_principal = car_price - down_payment
monthly_rate = loan_rate / 12
if loan_rate > 0:
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
kpi1.metric("Fleet Net Revenue", f"${fleet_net_revenue:,.0f}", f"{num_cars} Cars")
kpi2.metric("Total Fleet Costs", f"${fleet_total_costs:,.0f}", "OpEx + Debt")
kpi3.metric("Total Miles Driven", f"{fleet_total_miles:,.0f}", f"{(deadhead_miles_mo_per_car*num_cars):,.0f} Empty")
kpi4.metric("Net Fleet Cash Flow", f"${fleet_cash_flow:,.0f}", delta_color="normal" if fleet_cash_flow > 0 else "inverse")

if fleet_cash_flow > 0:
    st.success(f"✅ **Generating Cash:** Your fleet is producing **${fleet_cash_flow*12:,.0f}** in annual profit.")
else:
    st.error(f"⚠️ **Burning Cash:** Your fleet is losing **${abs(fleet_cash_flow):,.0f}** per month. Adjust pricing or utilization.")

# 2. Visual Breakdown & Sensitivity
c_viz, c_sens = st.columns([1, 1])

with c_viz:
    st.subheader("💸 Per-Car Unit Economics")
    # Sankey Waterfall
    fig_waterfall = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Gross Fares", "Tesla Fee", "Deadhead/Fuel/Tires", "Ins/Clean/Rescue", "Car Loan", "NET PROFIT"],
        textposition = "outside",
        text = [f"${gross_rev_car:,.0f}", f"-${platform_cut_car:,.0f}", f"-${var_opex_car:,.0f}", f"-${fixed_opex_car:,.0f}", f"-${monthly_debt_car:,.0f}", f"${cash_flow_car:,.0f}"],
        y = [gross_rev_car, -platform_cut_car, -var_opex_car, -fixed_opex_car, -monthly_debt_car, cash_flow_car],
        connector = {"line":{"color":"#555"}},
        decreasing = {"marker":{"color":"#E31937"}},
        increasing = {"marker":{"color":"#00C853"}},
        totals = {"marker":{"color":"#2196F3"}}
    ))
    fig_waterfall.update_layout(title="Where does the money go? (Single Car)", template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_waterfall, use_container_width=True)

with c_sens:
    st.subheader("🧠 Deep Think: Profit Sensitivity")
    st.markdown("How **Price** and **Utilization** affect Per-Car Monthly Profit.")
    
    # Real-time Heatmap Calc
    x_util = list(range(30, 85, 5))
    y_price = [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
    z_data = []
    for p in y_price:
        row = []
        for u in x_util:
            # Re-run core logic for matrix
            pm = (hours_mo * (u/100) * avg_speed)
            tm = pm / (u/100)
            gr = pm * p
            nr = gr * (1 - (platform_fee/100))
            vc = tm * (tire_cost + energy_cost)
            tc = vc + fixed_opex_car + monthly_debt_car
            row.append(nr - tc)
        z_data.append(row)

    fig_heat = go.Figure(data=go.Heatmap(
        z=z_data, x=[f"{x}%" for x in x_util], y=[f"${y:.2f}" for y in y_price],
        colorscale='RdBu', zmid=0, texttemplate="$%{z:.0f}", textfont={"size":10}
    ))
    fig_heat.update_layout(
        xaxis_title="Paid Utilization %", yaxis_title="Price per Mile",
        template="plotly_dark", height=400, margin=dict(l=0, r=0, t=30, b=0),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)'
    )
    st.plotly_chart(fig_heat, use_container_width=True)

# --- DEEP THINK CONTEXT SECTION ---
st.markdown("---")
st.header("📚 Deep Think: The Research Behind the Numbers")
st.markdown("Why are the default costs set where they are? Based on industry analysis of rideshare and fleet operations.")

with st.expander("1. The 'Vomit Tax' (Cleaning & Maintenance) - Why $400/mo?", expanded=True):
    st.markdown("""
    * **Reality:** A robotaxi cannot clean itself. Riders will leave trash, spill drinks, or worse.
    * **Benchmark:** Professional fleet detailing costs ~$100-$150 for a deep clean. A robotaxi will likely need a weekly deep clean plus daily wipe-downs.
    * **The Cost:** 4x weekly cleans ($400) + daily sanitization labor is a realistic, perhaps even conservative, estimate for maintaining a premium service.
    """)

with st.expander("2. Commercial Insurance - Why $250/mo?", expanded=True):
    st.markdown("""
    * **Reality:** Your personal auto policy **will not cover** a vehicle used for commercial rideshare, especially one without a driver.
    * **Benchmark:** Commercial fleet insurance for taxis or limos typically runs $3,000 - $6,000 per year per vehicle ($250 - $500/mo) depending on location and coverage limits.
    * **The Risk:** While autonomous cars may crash less, the *liability* for the few crashes they do have will be enormous, keeping premiums high initially.
    """)

with st.expander("3. Tires & Energy - Why $0.14/mile?", expanded=True):
    st.markdown("""
    * **Tires ($0.06/mi):** EVs are heavier and have higher torque, leading to faster tire wear. A set of 4 tires for a Tesla can cost $1,000+ and may only last 25,000 miles in high-duty city driving.
    * **Energy ($0.08/mi):** While home charging is cheap (~$0.15/kWh), a 24/7 robotaxi will rely heavily on Superchargers (~$0.35/kWh) to stay on the road. The blended cost per mile will be higher than a personal user's.
    """)

with st.expander("4. Utilization & Deadhead - The Silent Killer", expanded=True):
    st.markdown("""
    * **Reality:** A car only makes money when a passenger is inside. Driving to pick someone up (deadhead) costs money but earns zero.
    * **Benchmark:** Human Uber/Lyft drivers average a **50-60% paid utilization rate**. The rest of the time they are waiting or driving empty.
    * **The Math:** At 50% utilization, for every 1 paid mile, the car drives 2 total miles. Your variable costs (tires, energy) double relative to your revenue.
    """)
