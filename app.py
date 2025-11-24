import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Cybercab Unit Economics", layout="wide", page_icon="🚕")

# Custom CSS for a "Beautiful" Dark Theme look
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: #fafafa; }
    .metric-card { background-color: #262730; padding: 20px; border-radius: 10px; border: 1px solid #41444e; }
    h1, h2, h3 { color: #00D4FF; }
</style>
""", unsafe_allow_html=True)

st.title("🤖 Cybercab Ownership: Financial Reality Check")
st.markdown("Model the cash flow, tax shields, and profitability of a Tesla Robotaxi fleet.")

# --- SIDEBAR: ASSUMPTIONS ---
with st.sidebar:
    st.header("⚙️ Operating Assumptions")
    
    # Revenue Drivers
    price_per_mile = st.slider("Price per Paid Mile ($)", 0.50, 3.00, 1.25, 0.05)
    hours_per_week = st.slider("Active Hours / Week", 20, 168, 60)
    avg_speed = st.slider("Avg Speed (mph)", 10, 40, 20)
    utilization = st.slider("Utilization % (Paid Time)", 30, 90, 55, help="Time spent with a passenger vs empty")
    
    # Platform Costs
    platform_take = st.slider("Tesla Network Fee (%)", 15, 50, 30) / 100
    
    st.header("💸 Cost Assumptions")
    car_cost = st.number_input("Vehicle Purchase Price ($)", value=29000)
    insurance_mo = st.number_input("Commercial Insurance / Mo ($)", value=300)
    cleaning_mo = st.number_input("Cleaning & Data / Mo ($)", value=150)
    energy_cost = st.number_input("Energy Cost ($/mile)", value=0.07)
    tire_maint_cost = st.number_input("Tires & Maint ($/mile)", value=0.05)
    
    st.header("🏦 Loan & Tax")
    down_payment = st.number_input("Down Payment ($)", value=5000)
    loan_rate = st.slider("Loan Interest Rate (%)", 4.0, 15.0, 7.5) / 100
    loan_term = st.selectbox("Loan Term (Months)", [36, 48, 60, 72], index=2)
    tax_rate = st.slider("Your Marginal Tax Rate (%)", 0, 50, 24) / 100

# --- CALCULATIONS ---

# 1. Operational Physics
total_hours_mo = hours_per_week * 4.33
paid_hours_mo = total_hours_mo * (utilization / 100)
paid_miles_mo = paid_hours_mo * avg_speed
# Crucial: Total miles includes "Deadhead" miles (driving empty)
total_miles_mo = paid_miles_mo / (utilization / 100) 

# 2. Revenue
gross_revenue_mo = paid_miles_mo * price_per_mile
network_fee_mo = gross_revenue_mo * platform_take
net_revenue_mo = gross_revenue_mo - network_fee_mo

# 3. Variable Costs (Based on TOTAL miles)
variable_costs_mo = total_miles_mo * (energy_cost + tire_maint_cost)

# 4. Fixed Costs
fixed_costs_mo = insurance_mo + cleaning_mo

# 5. Loan Calculation (Amortization)
loan_amount = car_cost - down_payment
monthly_rate = loan_rate / 12
if loan_rate > 0:
    monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate) ** loan_term) / ((1 + monthly_rate) ** loan_term - 1)
else:
    monthly_payment = loan_amount / loan_term

# Interest portion (approx for first year avg)
interest_payment_mo = loan_amount * monthly_rate 

# 6. Profitability Waterfall
opex_mo = variable_costs_mo + fixed_costs_mo
ebitda_mo = net_revenue_mo - opex_mo
taxable_income_mo = ebitda_mo - interest_payment_mo - (car_cost / 60) # Simple 5yr straight line dep for book
taxes_mo = taxable_income_mo * tax_rate if taxable_income_mo > 0 else 0
net_income_mo = taxable_income_mo - taxes_mo

# 7. Cash Flow
cash_flow_mo = ebitda_mo - monthly_payment - taxes_mo

# --- DISPLAY ---

# Top Line Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Net Monthly Revenue", f"${net_revenue_mo:,.0f}", help="After Tesla takes their cut")
c2.metric("Monthly OpEx", f"${opex_mo:,.0f}", delta_color="inverse", help="Energy, Tires, Insurance, Cleaning")
c3.metric("EBITDA", f"${ebitda_mo:,.0f}", help="Operational Profit before Debt & Taxes")
c4.metric("Free Cash Flow", f"${cash_flow_mo:,.0f}", delta_color="normal" if cash_flow_mo > 0 else "inverse")

st.divider()

# Charts
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📊 Where does the money go?")
    # Sankey-style waterfall data
    cost_breakdown = pd.DataFrame({
        'Category': ['Tesla Fee', 'Energy/Tires', 'Insurance/Clean', 'Loan Payment', 'Taxes', 'YOUR PROFIT'],
        'Amount': [network_fee_mo, variable_costs_mo, fixed_costs_mo, monthly_payment, taxes_mo, max(cash_flow_mo, 0)]
    })
    fig_donut = px.pie(cost_breakdown, values='Amount', names='Category', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_donut, use_container_width=True)

with col_chart2:
    st.subheader("📈 Sensitivity: Utilization vs. Profit")
    # Generate scenario data
    util_range = list(range(10, 100, 5))
    profits = []
    for u in util_range:
        # Re-calc for plotting
        pm = (total_hours_mo * (u/100)) * avg_speed
        tm = pm / (u/100)
        gr = pm * price_per_mile
        nf = gr * platform_take
        vc = tm * (energy_cost + tire_maint_cost)
        opx = vc + fixed_costs_mo
        ebi = (gr - nf) - opx
        cf = ebi - monthly_payment - (ebi * tax_rate if ebi > 0 else 0)
        profits.append(cf)
    
    df_sens = pd.DataFrame({'Utilization %': util_range, 'Monthly Cash Flow ($)': profits})
    fig_line = px.line(df_sens, x='Utilization %', y='Monthly Cash Flow ($)', markers=True)
    fig_line.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Break Even")
    fig_line.add_vline(x=utilization, line_dash="dot", line_color="green", annotation_text="Current Assumption")
    st.plotly_chart(fig_line, use_container_width=True)

# Comparison Table
st.subheader("📝 Bear vs. Bull Scenarios (Monthly)")
scenarios = pd.DataFrame({
    "Metric": ["Paid Miles", "Gross Revenue", "Tesla Fee", "OpEx", "Loan Pmt", "Cash Flow"],
    "Your Scenario": [
        f"{paid_miles_mo:,.0f}", 
        f"${gross_revenue_mo:,.0f}", 
        f"-${network_fee_mo:,.0f}", 
        f"-${opex_mo:,.0f}", 
        f"-${monthly_payment:,.0f}", 
        f"${cash_flow_mo:,.0f}"
    ]
})
st.dataframe(scenarios, hide_index=True, use_container_width=True)

if cash_flow_mo < 0:
    st.error(f"⚠️ DANGER: This car costs you ${abs(cash_flow_mo):,.0f} per month to operate. Increase utilization or price.")
else:
    st.success(f"✅ PROFIT: This car generates ${cash_flow_mo * 12:,.0f} in annual passive income.")
