import requests
import json
from bs4 import BeautifulSoup

url = 'https://www.precisemortgages.co.uk/Residential/ResidentialCalculate'

def get_mortgage_data(data):
    mortgage_data = {}
    PayMethod =data["Mortgage Requirement"].get("Payment Method")
    property_location = data["Property Details"].get("Property Location")

    if property_location == "Northern Ireland":
        mortgage_data["SecurityAddressRegion"] = "North East"
    elif property_location == "England":
        mortgage_data["SecurityAddressRegion"] = "Greater London"
    elif property_location == "Wales":
        mortgage_data["SecurityAddressRegion"] = "Wales"
    elif property_location == "Scotland":
        mortgage_data["SecurityAddressRegion"] = "Scotland"
    else:
        mortgage_data["SecurityAddressRegion"] = "North West"

    mortgage_data["MonthlyUnsecuredCommitments"] = data["Mortgage Requirement"].get("Monthly Rent to Pay", 1000)
    mortgage_data["ProductType"]= "LessThan5Fixed"
    mortgage_data["PropertyValue"]= data["Mortgage Requirement"].get("Purchase Price", 0)
    mortgage_data["InitialRate"]= 2
    mortgage_data["ReversionaryRate"]= 2
    mortgage_data["MortgageTerm"]= int(data["Mortgage Requirement"].get("Loan Term")/12)
    mortgage_data["ProductFee"] = 0
    mortgage_data["ProductFeePercentage"] = 0

    if data["Mortgage Requirement"].get("Mortgage Type") == "Shared Equity / Help To Buy":
        mortgage_data["RepaymentType"] = "Capital & Interest"
        mortgage_data["HTBEquityLoanAmount"]= data["Mortgage Requirement"].get("Loan Amount",0)
        mortgage_data["HTBOnGoing"] = str((data["Mortgage Requirement"].get("Loan Amount")*0.0214368)/12)

        if data["Mortgage Requirement"].get("Loan Purpose") == "Remortgage":
            mortgage_data["LoanPurpose"]= "Remortgage"            
            mortgage_data["PartNone"] = "Part"
            mortgage_data["HTBEquityLoanMonthlyInterestFee"] = 2 if mortgage_data["PartNone"] == "Part" else 0
        else:
            mortgage_data["LoanPurpose"]= "Purchase"            

    if PayMethod == "Repayment":
        mortgage_data["RepaymentType"] = "Capital & Interest"
    elif PayMethod == "Interest Only":
        mortgage_data["RepaymentType"] = "Interest Only"
    else:
        mortgage_data["RepaymentType"] = "Part & Part"
        mortgage_data["InterestOnlyPart"] = 10
        mortgage_data["CapitalInterestPart"] = 90

    mortgage_data["PayingInterestFee"]= False

    return mortgage_data

def get_applicants(data):
    applicant_data = {}
    num_of_dependants = 0
    num_of_applicants = data.get("No of Applicant", 1)
    if data["Property Details"]["Property Details"].get("Country") == "United Kingdom":
        country = "EnglandWales"
    else:
        country = "Scotland"

    applicant_details = data.get("Client Details", {})

    applicant_type = "Sole" if num_of_applicants == 1 else "Joint"
    applicant_data["ApplicationType"] = applicant_type

    for i,applicant in enumerate(applicant_details):
        num_of_dependants += len(applicant.get("dependants"))
        applicant_data[f"Application{i+1}GrossIncome"] = applicant["Employment Details"].get("Basic Annual Income")
        applicant_data[f"App{i+1}Region"] = country
    
    applicant_data["NoOfDependants"] = num_of_dependants

    return applicant_data

def get_payload(data):
    mortgages = get_mortgage_data(data)
    applicants = get_applicants(data)

    json_payload = applicants
    json_payload.update(mortgages)

    payload = {'app':json.dumps(json_payload, separators=(',', ':'))}

    return payload


def main():
    with open(config) as file:
        data = json.load(file)
    payload = get_payload(data)

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        specific_div = soup.find('div', class_='col-xs-6')
        if specific_div:
            amount = specific_div.get_text(strip=True)
            print("Your Mortgage amount is : ",amount)
        else:
            print("Specific HTML segment not found.")
    elif response.status_code == 429:
        response = requests.post(url, payload)
        print(f"429")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Error message: {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
    main()
