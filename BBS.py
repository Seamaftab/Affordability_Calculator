import json
import requests
from datetime import datetime

url = 'https://bathbs.asanto.com/engine/mortgage/bath_hosted_resi_live'

def get_mortgage_data(data):
    mortgage_data = {}
    
    property_location = data["Property Details"].get("Property Location")
    Loan_Amount = data["Mortgage Requirement"].get("Loan Amount")
    loan_term = data["Mortgage Requirement"].get("Loan Term")
    Mortgage_Type = data["Mortgage Requirement"].get("Mortgage Type")

    mortgage_data["search_id"] = "ddfdeaab-5460-445b-b5cc-32387cb0aff1"
    mortgage_data["num_applicants"] = data.get("No of Applicant", 0)
    mortgage_data["property_value"] = str(data["Mortgage Requirement"].get("Purchase Price"))
    
    if property_location == "Northern Ireland":
        mortgage_data["property_region"] = "North East"
    elif property_location == "England":
        mortgage_data["property_region"] = "East of England"
    elif property_location == "Wales":
        mortgage_data["property_region"] = "Wales"
    elif property_location == "Scotland":
        mortgage_data["property_region"] = "Scotland"
    else:
        mortgage_data["property_region"] = "Greater London"

    mortgage_data["loan_amount"] = str(Loan_Amount)
    mortgage_data["capital_raising"] = "Yes"
    mortgage_data["help_to_buy"] = "No"
    mortgage_data["help_to_buy_equity_loan"] = 0 
    mortgage_data["mortgage_type"] = data["Mortgage Requirement"].get("Loan Purpose", 0)

    if data["Client Details"][0]["Applicant Type"] == "First Time Buyer":
        mortgage_data["purchaser_type"] = "FirstTimeBuyer"
    else:
        mortgage_data["purchaser_type"] = "Home mover"

    mortgage_data["mortgage_term_years"] = int(loan_term / 12)
    mortgage_data["mortgage_term_months"] = int(loan_term % 12)
    mortgage_data["product_length"] = str(int(data["Mortgage Requirement"].get("Product term") / 12)) + " years +"

    repayment_type = data["Mortgage Requirement"].get("Payment Method")

    if repayment_type == "Repayment":
        mortgage_data["repayment_type"] = "Capital & Interest"
    elif repayment_type == "Interest Only":
        mortgage_data["repayment_type"] = "Interest Only"
    else:
        mortgage_data["repayment_type"] = "Interest Only - Part & Part"

    mortgage_data["repayment_amt_capital"] = str(Loan_Amount)
    mortgage_data["repayment_amt_interest"] = "0"
    mortgage_data["property_type"] = data["Property Details"].get("Property Type") 

    return mortgage_data

def get_applicants(data):
    applicant_data = []
    num_of_dependants = 0
    applicant_details = data.get("Client Details", [])

    for applicant in applicant_details:
        num_of_dependants = len(applicant.get("dependants"))
        BBS = {
            "applicant_number": applicant_details.index(applicant) + 1,
            "date_of_birth": datetime.strptime(applicant.get("Date of Birth"), "%d/%m/%Y").strftime("%Y-%m-%d"),
            "current_age": (datetime.now().year - int(applicant["Date of Birth"].split("/")[-1])),
            "planned_retirement_age": applicant.get("expected retirement age"),
            "live_in_property": "No",
            "employment_status": applicant["Employment Details"].get("Employment Status"),
            "dependants_0_to_5": "0",
            "dependants_6_to_11": "0",
            "dependants_12_to_17": "0",
            "dependants_18_and_over": str(num_of_dependants),
            "annual_gross_salary": str(applicant["Employment Details"].get("Basic Annual Income")),
            "shareholding_percentage": "0",
            "annual_net_profit_current": str(applicant["Employment Details"].get("Last Year's Net Profits", 0)),
            "annual_net_profit_previous": str(applicant["Employment Details"].get("Previous Year's Net Profits", 0)),
            "annual_net_profit_period_3": str(applicant["Employment Details"].get("3rd Year's Net Profits", 0)),
            "annual_directors_salary_current": str(applicant["Employment Details"].get("Last Year's Salary", 0)),
            "annual_directors_salary_previous": str(applicant["Employment Details"].get("Previous Year's Salary", 0)),
            "annual_directors_salary_period_3": str(applicant["Employment Details"].get("3rd Year's Salary", 0)),
            "annual_gross_dividend_current": str(applicant["Employment Details"].get("Last Year's Dividends", 0)),
            "annual_gross_dividend_previous": str(applicant["Employment Details"].get("Previous Year's Dividends", 0)),
            "annual_gross_dividend_period_3": str(applicant["Employment Details"].get("3rd Year's Dividends", 0)),
            "annual_net_profit_ltd_latest_period": applicant["Employment Details"].get("Last Year's Retained Profits", 0),
            "annual_net_profit_ltd_period_2": applicant["Employment Details"].get("Previous Year's Retained Profits", 0),
            "annual_net_profit_ltd_period_3": applicant["Employment Details"].get("3rd Year's Retained Profits", 0),
            "length_of_time_current_job_years": 0,
            "length_of_time_current_job_months": 0,
            "second_job_annual_gross_salary": "0",
            "second_job_annual_net_profit_current": "0",
            "second_job_annual_net_profit_previous": "0",
            "second_job_annual_net_profit_period_3": "0",
            "second_job_annual_directors_salary_current": "0",
            "second_job_annual_directors_salary_previous": "0",
            "second_job_annual_directors_salary_period_3": "0",
            "second_job_annual_gross_dividend_current": "0",
            "second_job_annual_gross_dividend_previous": "0",
            "second_job_annual_gross_dividend_period_3": "0",
            "second_job_annual_net_profit_ltd_latest_period": 0,
            "second_job_annual_net_profit_ltd_period_2": 0,
            "second_job_annual_net_profit_ltd_period_3": 0,
            "length_of_time_second_job_years": "0",
            "length_of_time_second_job_months": "0",
            "annual_bonus": applicant["Additional Income (Annual)"].get("Regular Bonus", 0),
            "bonus_payment_frequency": "",
            "annual_commission": 0,
            "commission_payment_frequency": "",
            "annual_overtime": applicant["Additional Income (Annual)"].get("Irregular Overtime", 0),
            "overtime_payment_frequency": "",
            "annual_bank_work": 0,
            "annual_bursary": 0,
            "annual_foster_income": 0,
            "annual_stipend": 0,
            "annual_car_allowance": 0,
            "annual_large_town_allowance": 0,
            "annual_london_weighting": 0,
            "annual_shift_allowance": 0,
            "annual_gross_pension": 0,
            "annual_child_benefit": 0,
            "annual_child_tax_credits": 0,
            "annual_working_tax_credits": 0,
            "annual_carers_allowance": 0,
            "annual_dla_pip": 0,
            "annual_universal_credit": 0,
            "annual_investment_income": 0,
            "annual_lodger_income": 0,
            "annual_rental_income": 0,
            "annual_maintenance_income": 0,
            "student_rent_income": 0,
            "total_credit_card_balance": str(0 if applicant["Outgoings"].get("Credit Commitments") in ["null", None] else applicant["Outgoings"].get("Credit Commitments")),
            "credit_card_balance_to_be_repaid": "0",
            "annual_loan_payments": 0,
            "annual_household_expenses": applicant["Outgoings"]["Household"].get("Mortgage / Rent", 0),
            "annual_gas_electric": applicant["Outgoings"]["Household"].get("Electricity", 0),
            "annual_water": applicant["Outgoings"]["Household"].get("Electricity", 0) if applicant["Outgoings"]["Household"].get("Electricity") else 0,
            "annual_tv_internet": applicant["Outgoings"]["Household"].get("Television", 0),
            "annual_mobile_landlines": applicant["Outgoings"]["Living Costs"].get("Mobile Phone", 0),
            "annual_council_tax": 0,
            "annual_home_insurances": 0,
            "annual_life_insurances": 0,
            "annual_ground_rent_service_charge": 0,
            "annual_travel_transport": 0 if applicant["Outgoings"].get("Transport") in ["null", None] else applicant["Outgoings"].get("Transport"),
            "annual_maintenance_payments": 0,
            "annual_childcare": 0 if applicant["Outgoings"].get("Children") in ["null", None] else applicant["Outgoings"].get("Children"),
            "annual_car_upkeep": 0,
            "annual_personal_essential": 0,
            "annual_recreation": 0,
            "annual_other_expenditure": 0,
            "annual_student_loan_contributions": 0,
            "annual_pension_contributions": 0
        }

        applicant_data.append(BBS)

    return applicant_data

def get_payload(data):
	mortgage_data = get_mortgage_data(data)
	applicant_data = get_applicants(data)

	payload = mortgage_data
	payload["applicants"] = applicant_data
	payload["other_mortgages"] = []
	payload["buy_for_uni"] = "No"

	return payload

def main():
    with open(config) as file:
        data = json.load(file)
    payload = get_payload(data)

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        response_json = response.json()
        formatted_response = json.dumps(response_json, indent=4)
        print(f"Response : {formatted_response}\n")
    elif response.status_code == 429:
        response = requests.post(url, payload)
        print(f"429")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Error message: {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
	main()
