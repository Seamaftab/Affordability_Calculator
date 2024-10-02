import requests
import json

url = 'https://www.nationwide-intermediary.co.uk/_service/mortgages/affordability'

def get_mortgage_data(data):
    mortgage_data = {}

    mortgage_data["NumberOfApplicants"] = str(data.get("No of Applicant", 0))
    if data["Mortgage Requirement"].get("Loan Purpose") == "Purchase":
        mortgage_data["ApplicationType"] = "MG"
    else:
        mortgage_data["ApplicationType"] = "RM"
    mortgage_data["BorrowingAmount"] = str(data["Mortgage Requirement"].get("Loan Amount"))
    mortgage_data["MortgageTermYears"] = str(int(data["Mortgage Requirement"].get("Loan Term")/12))
    mortgage_data["MortgageTermMonths"] = str(int(data["Mortgage Requirement"].get("Loan Term")%12))

    Ownership = data["Mortgage Requirement"].get("Mortgage Type")
    if Ownership == "Standard Residential":
        mortgage_data["OwnershipType"] = "SD"
    elif Ownership == "Right To Buy":
        mortgage_data["OwnershipType"] = "RB"
        mortgage_data["MarketValue"] = "10000"
    elif Ownership == "Shared Equity / Help To Buy":
        mortgage_data["OwnershipType"] = "ES"
        mortgage_data["MarketValue"] = "10000"
    elif Ownership == "Shared Ownership":
        mortgage_data["OwnershipType"] = "SO"
        mortgage_data["MarketValue"] = "10000"
    else:
        mortgage_data["OwnershipType"] = "SD"

    mortgage_data["PropertyFound"] = "true"
    mortgage_data["PropertyTenure"] = "0"

    Property = data["Property Details"].get("Property Type")
    if Property == "House":
        mortgage_data["PropertyType"] = "3"
    elif Property == "Maisonette":
        mortgage_data["PropertyType"] = "7"
    elif Property == "Bungalow":
        mortgage_data["PropertyType"] = "6"
    else:
        mortgage_data["PropertyType"] = "8"

    mortgage_data["RegionCode"] = "12" if data["Property Details"].get("Property Location") == "Soctland" else ""
    mortgage_data["PurchasePrice"] = str(data["Mortgage Requirement"].get("Purchase Price", 0))

    return mortgage_data

def get_applicants(data):
    applicant_data = {}
    num_of_dependants = 0
    applicant_details = data.get("Client Details", [])

    for i, applicant in enumerate(applicant_details):
        num_of_dependants = len(applicant.get("dependants"))
        Customer = applicant.get("Applicant Type")
        employment_status = applicant["Employment Details"].get("Employment Status")
        if Customer == "First Time Buyer":
            CustomerType = "1"
        elif Customer == "Existing Mortgage Joint":
            CustomerType = "2"
        else:
            CustomerType = "3"

        MA = {
            "DateOfBirth": applicant.get("Date of Birth"),
            "CustomerType": CustomerType,
            "HaveDependents": "true" if num_of_dependants > 0 else "false",
            "Dependents": {
                "Age0_5": "0",
                "Age6_11": str(num_of_dependants),
                "Age12_17": "0",
                "Age18_More": "0"
            },
            "IsCustomerRetired": "true" if employment_status == "Retired" else "false",
            "PlannedRetirementAge": "0" if employment_status == "Retired" else str(applicant.get("expected retirement age")),
            "MainEmployment": {
                "EmploymentCategory": employment_status,
                "EmploymentType": "PM" if employment_status == "Employed" else "",
                "EmploymentTimeYY": "2" if employment_status == "Employed" else "",
                "EmploymentTimeMM": "0" if employment_status == "Employed" else "",
                "GrossAnnualIncome": str(applicant["Employment Details"].get("Basic Annual Income", 0)),
                "Bonus": str(applicant["Additional Income (Annual)"].get("Regular Bonus", 0)),
                "BonusFrequency": "1",
                "Overtime": str(applicant["Additional Income (Annual)"].get("Irregular Overtime", 0)),
                "OvertimeFrequency": "1",
                "Commission": "0"
            },
            "HasSecondJob": "false",
            "HasOtherIncome": "false",
            "GeneralOutgoings": {
                "TotalCreditCardBalances": "0" if applicant["Outgoings"].get("Credit Commitments") in [None, "null"] else str(applicant["Outgoings"].get("Credit Commitments")),
                "MonthlyPersonalLoanOrHire": "0",
                "MonthlySecuredLoanPayments": "0",
                "MonthlyDpaPayment": "0",
                "MonthlyStudentLoan": "0",
                "MonthlyTravelCosts": str(applicant["Outgoings"]["Living Costs"].get("Travel", 0)),
                "MonthlyOtherExpenditure": "0",
                "MonthlyChildCare": "0",
                "MonthlySchoolFees": "0",
                "MonthlyDependentMaintenance": "0",
                "MonthlyCostOfFinancialDependents": "0"
            },
            "HasExistingMortgages": "false",
        }

        if i == 0:
            applicant_data["MainApplicant"] = MA
        elif i == 1:
            applicant_data["JointApplicant"] = MA
        else:
            pass

    return applicant_data


def get_payload(data):
    mortgages = get_mortgage_data(data)
    applicants = get_applicants(data)

    payload = mortgages
    payload.update(applicants)

    return payload

def main():
    with open(config) as file:
        data = json.load(file)
    payload = get_payload(data)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code==200:
        response_json = response.json()
        formatted_response = json.dumps(response_json, indent=4)
        print(f"Response : {formatted_response}\n")
    elif response.status_code==429:
        response = requests.post(url, json=payload)
        print(f"retrying...")
    else:
        print(f"Request failed, status code : {response.status_code}")
        print(f"Error : {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
    main()