import requests
import json

url = 'https://openapi.natwest.com/mortgages/v1/ui-coord-affordability/calculate'

def get_applicants(data):
    num_of_dependants = 0
    applicant_data = []
    applicant_details = data.get("Client Details", [])

    for applicant in applicant_details:
        num_of_dependants += len(applicant["dependants"])
        BasicAnnualIncome = applicant["Employment Details"]["Basic Annual Income"]
        AdditionalIncome = applicant["Additional Income (Annual)"]["Irregular Overtime"] + applicant["Additional Income (Annual)"]["Regular Bonus"]
        grossIncome = BasicAnnualIncome + AdditionalIncome

        natwest = {
            "creditCards": {
                "totalBalancePostMortgage": applicant["Outgoings"]["Credit Commitments"],
            },
            "employment": {
                "grossSalary": grossIncome,
                "otherIncomeAmount": applicant["Additional Income (Annual)"]["Irregular Overtime"],
                "grossBonusMonthlyOrQuarterly": 0,
                "grossBonusHalfYearlyOrAnnually": applicant["Additional Income (Annual)"]["Regular Bonus"]
            },
            "expenditure": {
                "hirePurchasePayment": 0,
                "leasePayment": 0,
                "mortgageRent": 0,
                "loanPayments": 0,
                "maintenancePaymentsContinuing": 0
            }
        }
        applicant_data.append(natwest)
    return applicant_data, num_of_dependants

def get_mortgage_data(data):
    mortgage_data = {}

    mortgage_type = data["Mortgage Requirement"].get("Payment Method")
    loan_amount = data["Mortgage Requirement"].get("Loan Amount")
    Purchase_Price = data["Mortgage Requirement"].get("Purchase Price")
    
    mortgage_data["loanToValue"] = int((loan_amount / Purchase_Price) * 100)
    mortgage_data["isMortgageSharedEquity"] = False
    mortgage_data["mortgagePrisoner"] = False
    mortgage_data["mortgageTerm"] = int(data["Mortgage Requirement"].get("Loan Term") / 12)
    mortgage_data["mortgageTermMonths"] = int(data["Mortgage Requirement"].get("Loan Term") % 12)
    mortgage_data["capitalAndInterestAmount"] = 0 if mortgage_type == "Interest Only" else loan_amount
    mortgage_data["isRepaymentSaleOfMainResidency"] = False
    mortgage_data["currentValueOfInterestOnlyRepayment"] = 0
    mortgage_data["interestOnlyAmount"] = 0 if mortgage_type == "Repayment" else (Purchase_Price - loan_amount)
    
    if data["Mortgage Requirement"].get("Payment Method") == "Interest Only":
        mortgage_data["mortgageType"] = "INTEREST_ONLY"
    elif data["Mortgage Requirement"].get("Payment Method") == "Repayment":
        mortgage_data["mortgageType"] = "REPAYMENT"
    else:
        mortgage_data["mortgageType"] = "MIXED"

    return mortgage_data

def get_payload(data):
    mortgages = get_mortgage_data(data)
    applicants, num_of_dependants = get_applicants(data)
    
    payload = {
        "numberOfDependants": num_of_dependants,
        "calculatorType": "RESIDENTIAL",
        "isPersonalCircumstancesChanging": False,
        "applicants": applicants,
        "numberOfApplicants": data.get("No of Applicant"),
        "mortgage": mortgages
    }
    return payload


def main():
    with open(config) as file:
        data = json.load(file)
    payload = get_payload(data)

    response = requests.post(url, json=payload)
    if response.status_code==200:
    	response_json = response.json()
    	print(f"Response : {response_json}\n")
    elif response.status_code==429:
    	response = requests.post(url, json=payload)
    	print(f"retrying...")
    else:
    	print(f"Request failed, status code : {response.status_code}")
    	print(f"Error : {response.text}\n")

# main()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
	main()
