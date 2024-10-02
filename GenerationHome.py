import requests
import json

#Deposite Amount is (Purchase Price - Loan Amount)
#Every amount is calculated in cents or 1$ = 100cents

url = 'https://app.generationhome.com/brokers/api/v1/affordability_calculator/calculate'

def get_applicants(data):
	applicant_data = []
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])

	for applicant in applicant_details:
		num_of_dependants += len(applicant.get("dependants"))

		dob = applicant.get("Date of Birth")
		birthday = dob.split("/") if dob else ["01", "01", "1990"]

		GenerationHome = {
			"date_of_birth": {
			"day": str(birthday[0]),
			"month": str(birthday[1]),
			"year": str(birthday[2])
			},
			"planned_retirement_age": str(applicant.get("expected retirement age", 60)),
			"applicant_type": "owner",
			"liability": {
				"personal_loan_repayments_amount": 0,
				"child_maintenance_amount": 0,
				"mortgage_repayments_amount": 0,
				"credit_card_debt_amount": 0 if applicant["Outgoings"].get("Credit Commitments") in ["null", None] else applicant["Outgoings"].get("Credit Commitments")
			},
			"property": {},
			"incomes": {
			"employments": {
			  "base_salary_amount": applicant["Employment Details"].get("Basic Annual Income")*100,
			  "bonus_amount": applicant["Additional Income (Annual)"].get("Regular Bonus")*100,
			  "overtime_amount": applicant["Additional Income (Annual)"].get("Irregular Overtime", 0)*100
			},
			"sole_trader_or_partnerships": {},
			"limited_companies": {},
			"benefits": {},
			"rents": {},
			"pensions": {},
			"other_incomes": {}
			}
		}
		applicant_data.append(GenerationHome)
	return applicant_data, num_of_dependants

def get_payload(data):
	applicants, num_of_dependants = get_applicants(data)

	region = data["Property Details"].get("Property Location")

	if region == "Wales":
		region_code = "TLL"
	elif region == "Northern Ireland":
		region_code = "TLC"
	elif region == "England":
		region_code = "TLH"
	else:
		region_code = "TLD"

	payload = {
	  "total_owners_dependants": num_of_dependants,
	  "total_boosters_dependants": 0,
	  "offer_accepted": True,
	  "purchase_price_amount": data["Mortgage Requirement"].get("Purchase Price", 0)*100,
	  "property_type": data["Property Details"]["Property Details"].get("Property Type", "House").lower(),
	  "new_build": True,
	  "property_tenure": "freehold",
	  "region_code": region_code,
	  "requested_loan_amount": data["Mortgage Requirement"].get("Loan Amount", 0)*100,
	  "deposit_amount": (data["Mortgage Requirement"].get("Purchase Price", 0)-data["Mortgage Requirement"].get("Loan Amount", 0))*100
	}
	payload["applicants"] = applicants

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