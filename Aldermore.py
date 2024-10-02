import requests
import json

url = 'https://intermediaries.aldermore.co.uk/Umbraco/Api/ResiOOMortgageAffordability/Calculate/'

def get_mortgage_data(data):
	mortgage_data = {}

	mortgage_data["loanAmount"] = str(data["Mortgage Requirement"].get("Loan Amount"))
	mortgage_data["propertyValue"] = data["Mortgage Requirement"].get("Purchase Price")
	mortgage_data["term"] = str(int(data["Mortgage Requirement"].get("Loan Term")/12))
	mortgage_data["productType"] = "FixedOrDiscounted"
	mortgage_data["fixedRateYears"] = str(int(data["Mortgage Requirement"].get("Product Term", 60)/12))
	mortgage_data["reversionRate"] = 0.02 #Not in the reference/Default Value
	mortgage_data["payRate"] = 0.05 #Not in the reference/Default Value

	return mortgage_data

def get_applicants(data):
    applicant_data = []
    num_of_dependants = 0
    applicant_details = data.get("Client Details", [])

    for applicant in applicant_details:
        num_of_dependants = len(applicant["dependants"])
        household = sum(int(value) for value in applicant["Outgoings"]["Household"].values() if str(value).isdigit())
        living_costs = sum(int(value) for value in applicant["Outgoings"]["Living Costs"].values() if str(value).isdigit())

        Aldermore = {
            "landPropertyChk": True,
            "employedChk": True if applicant["Employment Details"].get("Employment Status") == "Employed" else False,
            "selfEmployedChk": True if applicant["Employment Details"].get("Employment Status") == "Self Employed (Sole Trader/Partnership)" else False,
            "otherIncomeChk": True,
            "isAboveNIAgeThreshold": False,
            "landPropertyAnnualProfit": "0",
            "landPropertyBtlBorrowing": "0",
            "employedAnnualIncome": str(applicant["Employment Details"].get("Basic Annual Income")),
            "employedBonusOvertimeCommission": str(applicant["Additional Income (Annual)"].get("Irregular Overtime", 0)),
            "employedAllowance": "0",
            "selfEmployedAnnualIncome": str(applicant["Employment Details"].get("Last Year's Salary", 0)),
            "otherIncome": [
                {
                    "incomeAmount": "0",
                    "incomeType": "Other"
                }
            ],
            "dependents": str(num_of_dependants),
            "creditCardBalance": "0" if applicant["Outgoings"].get("Credit Commitments", 0) in ["null", None] else str(applicant["Outgoings"].get("Credit Commitments")),
            "overdraftBalance": "0",
            "monthlyLoanVehicleRepayments": "0",
            "monthlyExpenditure": str(household + living_costs),
            "equityLoanBalance": "0"
        }
        applicant_data.append(Aldermore)
    return applicant_data


def get_payload(data):
	mortgages = get_mortgage_data(data)
	applicants = get_applicants(data)

	payload = mortgages
	payload["ApplicantPersonalIncomes"] = applicants

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
