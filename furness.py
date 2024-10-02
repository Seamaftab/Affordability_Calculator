import json
import requests
from bs4 import BeautifulSoup

url = "https://www.furnessbs.co.uk/intermediaries/residential-affordability-budget-breakdown"

def get_mortgage_data(data):
    mortgage_data = {}
    term = data["Mortgage Requirement"].get("Loan Term")
    Amount = data["Mortgage Requirement"].get("Loan Amount",0)
    Purchase = data["Mortgage Requirement"].get("Purchase Price",0)
    rate = 1
    monthly_rate = rate / 100 / 12
    num_payments = term

    PMT = (Amount * monthly_rate) / (1 - (1 + monthly_rate) ** -num_payments)

    mortgage_data["mortgage-repayment"] = round(PMT, 2)
    mortgage_data["AffordabilityMortgageLoanAmount"]= Amount
    mortgage_data["AffordabilityMortgagePurchasePrice"]= Purchase
    mortgage_data["affordability-loan-to-value"]= int((Amount/Purchase)*100)
    mortgage_data["affordability-interest-rate"]=rate
    mortgage_data["affordability-length"]=int(term/12)
    mortgage_data["product-type"]=4072
    mortgage_data["affordability-type"]="capital-and-interest" if data["Mortgage Requirement"].get("Payment Method") == "Repayment" else "interest-only"

    return mortgage_data

def get_income(data):
    money = {}
    total_net_income = 0
    clients = data.get("Client Details", [])

    for i, client in enumerate(clients):
        applicant = "" if i == 0 else "2"

        employment_details = client.get("Employment Details", {})
        basic_annual_income = employment_details.get("Basic Annual Income", 0)
        net_monthly_income = employment_details.get("Net Monthly Income", 0)

        money[f"AffordabilityBasicSalaryAnnum{applicant}"] = basic_annual_income
        money[f"AffordabilityNonGuaranteedIncome{applicant}"] = 0
        money[f"AffordabilityGuaranteedIncome{applicant}"] = 0
        money[f"assessable-income-per-annum{f'-{i + 1}' if i != 0 else ''}"] = basic_annual_income
        money[f"AffordabilityNetMonthlyIncome{'' if i == 0 else '2'}"] = net_monthly_income
        money["second-applicant"] = len(clients) > 1

        if net_monthly_income not in ["null", None]:
            total_net_income += net_monthly_income

    money["total-net-incomings"] = total_net_income
    return money

def get_expenses(data):
    expense = {}
    cost = data["Client Details"][0].get("Outgoings", [])

    expense["AffordabilityOtherCosts"]=0
    expense["AffordabilitySecuredDebtsCosts"]=0
    expense["AffordabilityCurrentRentCosts"]=cost["Household"].get("Mortgage / Rent", 0)
    expense["AffordabilityRepaymentStrategyCosts"]=0
    expense["AffordabilityUnsecuredDebtsCosts"]=0
    expense["AffordabilityMaintenanceChildSupportCosts"]=0
    expense["AffordabilityPersonalPensionCosts"]=0
    expense["AffordabilityInsuranceCosts"]=cost["Household"].get("Insurance", 0)
    expense["AffordabilityUtilitiesCosts"]=0
    expense["AffordabilityCouncilTaxCosts"]=0
    expense["AffordabilityFoodPersonalGoodsCosts"]=0
    expense["AffordabilityGroundRentServicesCosts"]=cost["Household"].get("Ground Rent", 0)
    expense["AffordabilityCommunicationsCosts"]=0
    expense["AffordabilityTravelCosts"]=cost["Living Costs"].get("Travel", 0)
    expense["AffordabilityFuelCommutingEssentialCosts"]=0
    expense["AffordabilityOtherTravelCosts"]=0
    expense["AffordabilityChildcareCosts"]=0
    expense["AffordabilityClothesEntertainmentHobbiesCosts"]=cost["Household"].get("Other", 0)
    expense["unsecured-expenses"]=2465.97

    return expense

def get_params(data):
    mortgages = get_mortgage_data(data)
    incomes = get_income(data)
    expenses = get_expenses(data)

    params = mortgages
    params.update(incomes)
    params.update(expenses)

    return params

def main():
    with open(config) as file:
        data = json.load(file)
    params = get_params(data)

    response = requests.get(url, params=params)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        amount_remaining = soup.select_one("#total-remainings")
        print(f"Total Remainings : ",amount_remaining.text)
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
    main()