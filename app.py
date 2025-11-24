import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Cybercab Business Planner", layout="wide", page_icon="🚕")

# --- CUSTOM CSS FOR "BEAUTIFUL" UI ---
st.markdown("""
<style>
    /* Dark Mode Modern aesthetics */
    .stApp { background-color: #050505; color: #e0e0e0; }
    
    /* KPI Cards */
    .css-1r6slb0 { background-color: #1E1E1E; border: 1px solid #333; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
    
    /* Sliders - Tesla Red Accent */
    div.stSlider > div > div > div > div { background-color: #E31937; }
    
    /* Headers */
    h1, h2, h3 { font-family: 'SF Pro Display', sans-serif; letter-spacing: -0.5px; }
    h1 { color: #E31937; }
    h2 { color: #ffffff; border-bottom: 2px solid #333; padding-bottom: 10px; }
    
    /* Tooltips */
    .tooltip { position: relative; display: inline-block; border-bottom: 1px dotted white; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🚕 Cybercab Owner Logic")
    st.markdown("#### The 'Airbnb for Cars' Business Simulator")
with c2:
    st.image("https://upload.wikimedia.org/wikipedia/commons/e/e8/Tesla_logo.png", width=100)

st.divider()

# --- SIDEBAR: THE CONTROL CENTER ---
with st.sidebar:
    st.header("🎛️ Operational Controls")
    
    with st.expander("💰 Revenue Assumptions", expanded=True):
        price_per_mile = st.slider("Price Charged ($/mi)", 0.50, 3.50, 1.60, 
            help="Uber is ~$2.50. Robotaxi promises to be cheaper. $1.00 is the 'race to bottom' floor.")
        
        paid_utilization = st.slider("Paid Utilization (%)", 20, 80, 55, 
            help="Percent of time the car actually has a paying passenger. Uber drivers average ~50-60%.")
        
        hours_active = st.slider("Hours Online / Day", 8, 24, 16, 
            help="How long is the car available? 16 hours allows for charging + cleaning breaks.")

    with st.expander("🤝 The 'Tesla Tax' & Fees", expanded=True):
        platform_fee = st.slider("Tesla Platform Fee (%)", 15, 50, 30, 
            help="The cut Tesla takes for matching riders. Apple takes 30%, Uber takes ~40%.")
        
    with st.expander("📉 Hidden 'Killer' Costs", expanded=False):
        st.caption("Most models ignore these. We don't.")
        
        cleaning_budget = st.number_input("Cleaning Budget ($/mo)", value=400, step=50,
            help="The 'Vomit Tax'. Weekly deep cleans + daily sanitization. One bad ride can cost $150.")
        
        insurance_cost = st.number_input("Commercial Insurance ($/mo)", value=250, step=50,
            help="Personal insurance WON'T cover this. You need commercial fleet liability.")
        
        remote_intervention = st.number_input("Remote Rescue Fee ($/mo)", value=50,
            help="Cost for a human to remotely 'unstick' the car if it gets confused.")
        
        tire_cost = st.number_input("Tires & Maint. ($/mi)", value=0.06, format="%.2f",
            help="EVs are heavy and eat tires. Expect to replace tires every 25k miles.")
        
        energy_cost = st.number_input("Electricity ($/mi)", value=0.08, format="%.2f",
            help="Assumes mix of Home Charging ($0.15/kWh) and Supercharging ($0.35/kWh).")

    with st.expander("🏦 Loan & CapEx", expanded=False):
        car_price = st.number_input("Vehicle Price ($)", value=29000)
        down_payment = st.number_input("Down Payment ($)", value=5000)
        loan_rate = st.number_input("Interest Rate (%)", value=7.5) / 100
        loan_months = st.selectbox("Loan Term", [36, 48, 60, 72], index=2)

# --- LOGIC ENGINE ---

# 1. Time Physics
days_mo = 30.5
hours_mo = hours_active * days_mo
paid_hours_mo = hours_mo * (paid_utilization / 100)
avg_speed = 18 # City average mph

# 2. Mileage Physics (The Deadhead Calculation)
paid_miles_mo = paid_hours_mo * avg_speed
# If 50% utilization, you drive 2 miles to get paid for 1.
total_miles_mo = paid_miles_mo / (paid_utilization / 100) 
deadhead_miles_mo = total_miles_mo - paid_miles_mo

# 3. Revenue
gross_revenue = paid_miles_mo * price_per_mile
platform_cut = gross_revenue * (platform_fee / 100)
net_revenue = gross_revenue - platform_cut

# 4. Variable Costs (Tires, Fuel - based on TOTAL miles)
variable_opex = total_miles_mo * (tire_cost + energy_cost)

# 5. Fixed Costs (Insurance, Cleaning, Rescue)
fixed_opex = cleaning_budget + insurance_cost + remote_intervention

# 6. Debt Service
loan_principal = car_price - down_payment
monthly_rate = loan_rate / 12
monthly_debt = loan_principal * (monthly_rate * (1 + monthly_rate) ** loan_months) / ((1 + monthly_rate) ** loan_months - 1)

# 7. The Bottom Line
total_costs = variable_opex + fixed_opex + monthly_debt
cash_flow = net_revenue - total_costs

# --- DASHBOARD LAYOUT ---

# Row 1: The Big Numbers
c1, c2, c3, c4 = st.columns(4)
c1.metric("Monthly Revenue", f"${net_revenue:,.0f}", "After Tesla Fee")
c2.metric("Monthly Costs", f"${total_costs:,.0f}", "OpEx + Debt")
c3.metric("Miles Driven", f"{total_miles_mo:,.0f}", f"{deadhead_miles_mo:,.0f} Empty (Deadhead)")
c4.metric("Net Cash Flow", f"${cash_flow:,.0f}", delta_color="normal" if cash_flow > 0 else "inverse")

st.markdown("---")

# Row 2: Visuals
col_left, col_right = st.columns([2, 1])

with col_left:
    st.subheader("💸 Where is the money going?")
    
    # Sankey-like Waterfall
    fig = go.Figure(go.Waterfall(
        name = "20", orientation = "v",
        measure = ["relative", "relative", "relative", "relative", "relative", "total"],
        x = ["Gross Fares", "Tesla Fee", "Deadhead/Fuel/Tires", "Insurance/Clean/Rescue", "Car Loan", "YOUR PROFIT"],
        textposition = "outside",
        text = [f"${gross_revenue:,.0f}", f"-${platform_cut:,.0f}", f"-${variable_opex:,.0f}", f"-${fixed_opex:,.0f}", f"-${monthly_debt:,.0f}", f"${cash_flow:,.0f}"],
        y = [gross_revenue, -platform_cut, -variable_opex, -fixed_opex, -monthly_debt, cash_flow],
        connector = {"line":{"color":"rgb(63, 63, 63)"}},
    ))
    fig.update_layout(template="plotly_dark", height=400, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🎯 Breakeven Analysis")
    st.markdown(f"""
    To make **$1.00 of profit**, you need:
    
    * **Price:** ${price_per_mile:.2f} / mile
    * **Utilization:** {paid_utilization}%
    """)
    
    if cash_flow < 0:
        st.error(f"⚠️ **BURNING CASH**\nYou are losing ${abs(cash_flow):.0f} every month. You are effectively paying people to ride in your car.")
    elif cash_flow < 1000:
        st.warning(f"⚠️ **SIDE HUSTLE**\nMaking ${cash_flow:.0f}/mo. Nice extra cash, but not a livelihood yet. One major repair could wipe out a year of profit.")
    else:
        st.success(f"✅ **FREEDOM**\nMaking ${cash_flow:.0f}/mo (${cash_flow*12:,.0f}/yr). This beats most entry-level salaries.")

# Row 3: Sensitivity (The "What If" Machine)
st.subheader("🧠 Deep Think: Sensitivity Matrix")
st.markdown("How does **Price** and **Utilization** affect your bottom line?")

# Create Heatmap Data
x_util = list(range(20, 90, 10))
y_price = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
z_data = []

for p in y_price:
    row = []
    for u in x_util:
        # Quick calc logic
        pm = (hours_mo * (u/100) * avg_speed)
        tm = pm / (u/100)
        gr = pm * p
        nr = gr * (1 - (platform_fee/100))
        vc = tm * (tire_cost + energy_cost)
        tc = vc + fixed_opex + monthly_debt
        row.append(nr - tc)
    z_data.append(row)

fig_heat = go.Figure(data=go.Heatmap(
    z=z_data, x=[f"{x}%" for x in x_util], y=[f"${y:.2f}" for y in y_price],
    colorscale='RdBu', zmid=0, texttemplate="$%{z:.0f}", textfont={"size":12}
))
fig_heat.update_layout(
    title="Monthly Profit Heatmap (Green = Good, Red = Debt)",
    xaxis_title="Utilization %", yaxis_title="Price per Mile",
    template="plotly_dark", height=500
)
st.plotly_chart(fig_heat, use_container_width=True)

# --- FOOTER ---
st.caption("Disclaimer: This is a simulation based on estimated inputs. Actual cleaning costs, insurance premiums, and regulatory fees will vary by city.")
