import pandas as pd
import numpy as np

def calculate_robotaxi_profitability(
    vehicle_cost,
    annual_miles,
    paid_miles_percentage,
    price_per_mile,
    maintenance_cost_per_mile,
    insurance_cost_per_year,
    operational_life_years,
    energy_cost_per_mile,
    discount_rate,
):
    """
    Calculates the net present value (NPV) and internal rate of return (IRR) 
    of a Robotaxi investment.

    Args:
        vehicle_cost (float): The initial cost of the robotaxi vehicle.
        annual_miles (float): The total number of miles driven per year.
        paid_miles_percentage (float): The percentage of annual miles that are paid miles.
        price_per_mile (float): The price charged per paid mile.
        maintenance_cost_per_mile (float): The cost of maintenance per mile driven.
        insurance_cost_per_year (float): The annual cost of insurance.
        operational_life_years (int): The number of years the vehicle is expected to operate.
        energy_cost_per_mile (float): The cost of energy per mile driven.
        discount_rate (float): The discount rate used to calculate NPV.

    Returns:
        dict: A dictionary containing the NPV and IRR of the investment.
    """

    paid_miles_per_year = annual_miles * paid_miles_percentage
    annual_revenue = paid_miles_per_year * price_per_mile
    annual_operating_cost = (
        annual_miles * (maintenance_cost_per_mile + energy_cost_per_mile)
        + insurance_cost_per_year
    )
    annual_cash_flow = annual_revenue - annual_operating_cost

    cash_flows = [-vehicle_cost] + [annual_cash_flow] * operational_life_years
    npv = np.npv(discount_rate, cash_flows)
    irr = np.irr(cash_flows)

    return {"NPV": npv, "IRR": irr}

# --- Example Usage ---
vehicle_cost = 50000
annual_miles = 100000
paid_miles_percentage = 0.8
price_per_mile = 1.5
maintenance_cost_per_mile = 0.1
insurance_cost_per_year = 3000
operational_life_years = 5
energy_cost_per_mile = 0.05
discount_rate = 0.1

results = calculate_robotaxi_profitability(
    vehicle_cost,
    annual_miles,
    paid_miles_percentage,
    price_per_mile,
    maintenance_cost_per_mile,
    insurance_cost_per_year,
    operational_life_years,
    energy_cost_per_mile,
    discount_rate,
)

print(f"Net Present Value (NPV): ${results['NPV']:.2f}")
print(f"Internal Rate of Return (IRR): {results['IRR']:.2%}")
