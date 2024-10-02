import requests
import json
from datetime import datetime

url = 'https://portal.intermediaries.hsbc.co.uk/ajax/calculateaffordability.php'

def get_mortgage_data(data):
	mortgage_data = {}
	applicants, num_of_dependants = get_applicants(data)

	LTV = (data["Mortgage Requirement"].get("Loan Amount")/data["Mortgage Requirement"].get("Purchase Price"))*100
	if LTV <= 85:
		mortgage_data["maximumLTV"] = 85
	elif LTV>85 and LTV<=90:
		mortgage_data["maximumLTV"] = 90
	else:
		mortgage_data["maximumLTV"] = 95

	PType = data["Client Details"][0].get("Applicant Type")
	if PType == "First Time Buyer":
		mortgage_data["purchaserType"] = "F"
	elif PType == "Existing Mortgage Single" or PType == "Existing Mortgage Joint":
		mortgage_data["purchaserType"] = "M"
	else:
		mortgage_data["purchaserType"] = "T"

	mortgage_data["isJointMortgage"] = 0 if data.get("No of Applicant")==1 else 1
	mortgage_data["noDependantAdults"] = 0
	mortgage_data["noDependantChildren"] = num_of_dependants
	mortgage_data["postcode"] = data["Property Details"]["Property Details"].get("Post Code")
	mortgage_data["depositAmount"] = 0
	mortgage_data["estimatedPropertyValue"] = data["Mortgage Requirement"].get("Purchase Price")
	mortgage_data["requiredMortgageTerm"] = int(data["Mortgage Requirement"].get("Loan Term")/12)
	mortgage_data["assessOnInterestOnlyBasis"] = 0
	mortgage_data["loan_amount"] = data["Mortgage Requirement"].get("Loan Amount")

	return mortgage_data

def get_applicants(data):
	applicant_data = {}
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])

	for i,applicant in enumerate(applicant_details):
		num_of_dependants += len(applicant.get("dependants"))

		e_stat = applicant["Employment Details"].get("Employment Status")
		if e_stat == "Employed":
			employment_status = "E"
		elif e_stat == "Self Employed (Sole Trader/Partnership)" or e_stat == "Self Employed (Ltd Company/Director)":
			employment_status = "S"
		elif e_stat == "Retired":
			employment_status = "P"
		else:
			employment_status = "H"

		marry = applicant.get("Marital Status")
		BasicAnnualIncome = applicant["Employment Details"].get("Basic Annual Income", 0)
		AdditionalIncome = applicant["Additional Income (Annual)"]["Irregular Overtime"] + applicant["Additional Income (Annual)"]["Regular Bonus"]
		Credit = applicant["Outgoings"].get("Credit Commitments")
		Transport = applicant["Outgoings"].get("Transport")

		applicant_data[f"a{i+1}employmentStatus"] = employment_status
		applicant_data[f"a{i+1}maritalStatus"] = "S" if marry == "Single" else "M"
		applicant_data[f"a{i+1}applicantsAge"] = (datetime.now().year - int(applicant["Date of Birth"].split("/")[-1]))
		applicant_data[f"a{i+1}grossIncome"] = BasicAnnualIncome + AdditionalIncome		
		applicant_data[f"a{i+1}additionalIncome"] = AdditionalIncome
		applicant_data[f"a{i+1}dividendIncome"] = applicant["Employment Details"].get("Last Year's Dividends", 0)
		applicant_data[f"a{i+1}otherNonTaxableIncome"] = 0
		applicant_data[f"a{i+1}existingBTLRentalIncome"] = 0
		applicant_data[f"a{i+1}existingBTLOutgoings"] = 0
		applicant_data[f"a{i+1}totalMonthlyLoanPayments"] = 0
		applicant_data[f"a{i+1}outstandingCreditCardBalances"] = 0 if Credit in ["null", None] else Credit
		applicant_data[f"a{i+1}travel"] = 0 if Transport in ["null", None] else Transport
		applicant_data[f"a{i+1}childcareCosts"] = 0
		applicant_data[f"a{i+1}otherExpenditure"] = 0
		applicant_data[f"a{i+1}childcareVouchers"] = 0
		applicant_data[f"a{i+1}rentAndServiceCharge"] = applicant["Outgoings"]["Household"].get("Mortgage / Rent", 0)

	return applicant_data, num_of_dependants

def get_payload(data):
	applicants, num_of_dependants = get_applicants(data)
	mortgages = get_mortgage_data(data)

	payload = mortgages
	payload.update(applicants)

	return payload

def main():
    with open(config) as file:
        data = json.load(file)
    json_payload = get_payload(data)

    payload ='&'.join([f'{key}={value}' for key, value in json_payload.items()])

    headers = {
	    'Content-Type': 'application/x-www-form-urlencoded',
	    'Cookie': 'PHPSESSID=li1odg1coquft133m9veiq1md6'
	}

    response = requests.post(url, data=payload, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        formatted_response = json.dumps(response_json, indent=4)
        print(f"Response : {formatted_response}\n")
    elif response.status_code == 429:
        response = requests.post(url, data=payload, headers=headers)
        print(f"429")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Error message: {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
	main()
