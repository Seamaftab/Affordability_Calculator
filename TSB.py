import json
import requests

url = 'https://intermediary.tsb.co.uk/calculator/mortgage-affordability'

headers = {
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_mortgage_data(data, num_of_dependants):
	mortgage_data = {}

	Location = data["Property Details"].get("Property Location")
	if Location == "Wales":
		mortgage_data["CustomerLocation"] = "4"
	elif Location == "Scotland":
		mortgage_data["CustomerLocation"] = "3"
	else:
		mortgage_data["CustomerLocation"] = "2"

	applicationType = data["Client Details"][0].get("Applicant Type")

	if applicationType == "First Time Buyer":
		mortgage_data["ApplicationType"] = "2"
	elif applicationType == "No Current Mortgage":
		mortgage_data["ApplicationType"] = "3"
	elif applicationType == "Existing Mortgage Single":
		mortgage_data["ApplicationType"] = "4"
	else:
		mortgage_data["ApplicationType"] = "5"

	e_stat = data["Client Details"][0]["Employment Details"].get("Employment Status")

	mortgage_data["IsSelfEmployedValue"] = "Yes" if e_stat == "Self Employed (Sole Trader/Partnership)" or e_stat == "Self Employed (Ltd Company/Director)" else "No"
	mortgage_data["IsAnyPartInterestOnly"] = "No"
	mortgage_data["TotalMortgageBalance"] = "0"
	mortgage_data["TotalEstimatedRentalIncomePerMonth"] = "0"
	mortgage_data["NoOfAdults"] = str(data.get("No of Applicant"))
	mortgage_data["NoOfChildrens"] = str(num_of_dependants)
	mortgage_data["MortgageTerm"] = str(int(data["Mortgage Requirement"].get("Loan Term")/12))
	
	Purchase_Price = data["Mortgage Requirement"].get("Purchase Price", 0)
	Loan_Amount = data["Mortgage Requirement"].get("Loan Amount", 0)
	mortgage_data["LTV"] = str(int((Loan_Amount/Purchase_Price)*100))
	mortgage_data["InterestOnlyReqTotalLoanAmount"] =  ""
	mortgage_data["InterestOnlyReqInterestOnlyAmount"] =  ""
	mortgage_data["InterestOnlyMonthlyCostForRepaymentStrategy"] =  ""
	mortgage_data["CurrentBlockId"] =  "741"

	return mortgage_data

def get_applicants(data):
	applicant_data = []
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])
	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details) > 1 else {}
	credit_one = applicant_one["Outgoings"].get("Credit Commitments", 0)
	credit_two = applicant_two.get("Outgoings", {}).get("Credit Commitments", 0)

	num_of_dependants += len(applicant_one.get("dependants", [])) + len(applicant_two.get("dependants", []))

	applicant_data.extend([
		{
			"Basic": str(applicant_one.get("Employment Details", {}).get("Basic Annual Income", 0)),
			"GuranteedOvertime": str(applicant_one.get("Additional Income (Annual)").get("Irregular Overtime")),
			"GuranteedBonus": str(applicant_one.get("Additional Income (Annual)").get("Regular Bonus", 0)),
			"GuranteedCommission": "0",
			"OtherIncome": [
				{"Name": "1", "Income": ""},
				{"Name": "1", "Income": ""},
				{"Name": "1", "Income": ""},
				{"Name": "1", "Income": ""}
			],
			"Expenses": {
				"MonthlyMortgage": "0",
				"MonthlyLoan": "0",
				"Cards": "0" if credit_one in ["null", None] else credit_one,
				"AdditionalMonthlyCosts": "0"
			}
		},
		{
			"Basic": str(applicant_two.get("Employment Details", {}).get("Basic Annual Income", 0)),
			"GuranteedOvertime": str(applicant_two.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0)),
			"GuranteedBonus": str(applicant_two.get("Additional Income (Annual)", {}).get("Regular Bonus", 0)),
			"GuranteedCommission": "",
			"OtherIncome": [
				{"Income": ""},
				{"Income": ""},
				{"Income": ""},
				{"Income": ""}
			],
			"Expenses": {
				"MonthlyMortgage": "",
				"MonthlyLoan": "",
				"Cards": "0" if credit_two in ["null", None] else credit_two,
				"AdditionalMonthlyCosts": ""
			}
		}
	])

	return applicant_data, num_of_dependants

def get_payload(data):
	applicants, num_of_dependants = get_applicants(data)
	mortgages = get_mortgage_data(data, num_of_dependants)

	payload = mortgages
	payload["Applicants"] = applicants

	return payload

def main():
	with open(config) as file:
		data = json.load(file)
	payload = get_payload(data)

	response = requests.post(url, json=payload, headers=headers)
	if response.status_code==200:
		response_json = response.json()
		item_2 = response_json.get('Item2')
		print(f"Response : {item_2}\n\n")
	elif response.status_code==429:
		response = requests.post(url, json=payload)
		print(f"retrying...")
	else:
		print(f"Request failed, status code : {response.status_code}")
		print(f"Error : {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
	main()