import requests
import json

url = 'https://apply.metrobankonline.co.uk/eforms/resi-mortgage'

def get_mortgage_data(data):
	mortgage_data = {}
	if data["Mortgage Requirement"]["Payment Method"] == "Repayment":
		mortgage_data["repaymentMethod"] = "Capital and Interest"
	elif data["Mortgage Requirement"]["Payment Method"] == "Split":
		mortgage_data["repaymentMethod"] = "Part and Part"
	else:
		mortgage_data["repaymentMethod"] = "Interest Only"

	mortgage_data["partAndPartInterest"] = str(data["Mortgage Requirement"].get("Share of Value (%)",0))
	mortgage_data["mortgageTermYears"] = int(data["Mortgage Requirement"].get("Loan Term")/12)
	mortgage_data["mortgageTermMonths"] = int(data["Mortgage Requirement"].get("Loan Term")%12)
	mortgage_data["loanToValuePercent"] = int((data["Mortgage Requirement"].get("Loan Amount")/data["Mortgage Requirement"].get("Purchase Price"))*100)
	return mortgage_data

def get_customer_data(data):
	num_of_dependants = 0
	customer_info = []
	customer_details = data.get("Client Details", [])

	for customer in customer_details:
		num_of_dependants = len(customer.get("dependants", 0))
		BasicAnnualIncome = customer["Employment Details"]["Basic Annual Income"]
		AdditionalIncome = customer["Additional Income (Annual)"]["Irregular Overtime"] + customer["Additional Income (Annual)"]["Regular Bonus"]
		grossIncome = BasicAnnualIncome + AdditionalIncome
		
		additionalExpenditure = customer["Outgoings"].get("Children")

		household = sum(value for key, value in customer["Outgoings"]["Household"].items())
		living_costs = sum(value for key, value in customer["Outgoings"]["Living Costs"].items())
		credit = customer["Outgoings"]["Credit Commitments"]
		through = {
		      "household": 1,
		      "grossIncome": grossIncome,
		      "monthlyPayments": 0,
		      "creditCardBalance": 0 if credit in ["null", None] else credit,
		      "additionalExpenditure": additionalExpenditure if additionalExpenditure else 0,
		      "dependents": num_of_dependants,
		      "householdExpenditure": household + living_costs
			}
		customer_info.append(through)
	
	return customer_info

def get_payload(data):
	mortgage_data = get_mortgage_data(data)
	customer_data = get_customer_data(data)

	payload = {}

	payload["customer"] = customer_data
	payload.update(mortgage_data)

	payload.update({
		  "poundForPoundRemortgage": False,
		  "poundForPoundRemortgageInterestRate": 0,
		  "professionalMortgage": False,
		  "professionalMortgageInterestRate": 0
		})

	return payload

def main():
    with open(config) as file:
        data = json.load(file)
    payload = get_payload(data)

    response = requests.post(url, json=payload)
    if response.status_code==200:
    	response_json = response.json()
    	print(f"Response : {response_json}")
    elif response.status_code==429:
    	response = requests.post(url, json=payload)
    	print(f"retrying...")
    else:
    	print(f"Request failed, status code : {response.status_code}")
    	print(f"Error : {response.text}")

#main()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
	main()