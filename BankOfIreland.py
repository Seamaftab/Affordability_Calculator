import requests
import json

def get_params(data):
	applicant_details = data.get("Client Details", [])
	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details)>1 else {}

	num_of_dependants = 0
	num_of_dependants = len(applicant_one.get("dependants", [])) + len(applicant_two.get("dependants", []))
	Product_term = int(data["Mortgage Requirement"].get("Product term", 0)/12)
	Purchase_Price = data["Mortgage Requirement"].get("Purchase Price", 0)
	Loan_Amount = data["Mortgage Requirement"].get("Loan Term", 0)
	LTV = (Loan_Amount/Purchase_Price)*100

	outgoings_one = applicant_one.get("Outgoings", {})
	outgoings_two = applicant_two.get("Outgoings", {})

	sum_of_outgoings_one = sum(value if value is not None and isinstance(value, (int, float)) else 0 for category, value in outgoings_one.items() if value is not None)
	sum_of_outgoings_two = sum(value if value is not None and isinstance(value, (int, float)) else 0 for category, value in outgoings_two.items() if value is not None)

	sum_of_outgoings = sum_of_outgoings_one + sum_of_outgoings_two

	params = {
		"Adults":data.get("No of Applicant", 0),
		"Children":num_of_dependants,
		"MortgageYears":int(data["Mortgage Requirement"].get("Loan Term")/12),
		"MortgageMonths":int(data["Mortgage Requirement"].get("Loan Term", 0)%12),
		"App1Income":applicant_one["Employment Details"].get("Basic Annual Income", 0),
		"App2Income":applicant_two.get("Employment Details", {}).get("Basic Annual Income", 0),
		"FiveYearFixedRate":1 if Product_term == 5 else 0,
		"FiveYearFixedPercent":1 if Product_term == 5 else {},
		"Outgoings":sum_of_outgoings,
		"LTVBelow90":"true" if LTV<90 else "false",
		"Ref":"",
		"typeid":"1cfa7353-6474-41f0-91d8-cd224ab090c7",
		"versionid":"4eac95b6-3208-4271-b473-3f126cc63d09"
	}

	return params

url = "https://calculator.bankofirelanduk.com/api/calculate"

headers = {
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"Content-Type":"application/x-www-form-urlencoded"
}

def main(config_file):
	with open(config_file) as file:
		data = json.load(file)
	params = get_params(data)
	data_to_return = {
		"result": None,
		"max_affordable_loan" : None,
		"remarks": ""
	}

	response = requests.get(url, params=params)
	if response.status_code==200:
		try:
			response_json = response.json()
			data_to_return["max_affordable_loan"] = response_json
			data_to_return["result"] = "Pass"
		except:
			data_to_return["remarks"] = "Something went wrong. Please try again"
	else:
		data_to_return["remarks"] = "Request failed, status: {}".format(response.status_code)

	return data_to_return

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
    print(main(config_file))
