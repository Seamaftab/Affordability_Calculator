import json
import requests
import urllib.parse
import re
from datetime import datetime

url = "https://www.kensingtonmortgages.co.uk/kmc-api/webcalculator"

headers = {	
	"Accept":"application/json, text/javascript, */*; q=0.01",
	"Accept-Encoding":"gzip, deflate, br",
	"Accept-Language":"en-US,en;q=0.9",
	"Content-Length":"1997",
	"Content-Type":"application/x-www-form-urlencoded",
	"Origin":"https://www.kensingtonmortgages.co.uk",
	"Referer":"https://www.kensingtonmortgages.co.uk/archive/calculators/residential",
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0",
	"X-Requested-With":"XMLHttpRequest"
}

def calculate_age(birthdate):
	birth_date = datetime.strptime(birthdate, '%d/%m/%Y')
	current_date = datetime.now()
	age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
	return age

def get_applicants(data):
	applicant_data = []
	dep_age = []
	applicant_details = data.get("Client Details", [])
	num_of_dependants = 0

	for i, applicant in enumerate(applicant_details):
		dependants = applicant.get("dependants")
		num_of_dependants += len(dependants)

		for dep in dependants:
			age = calculate_age(dep.get("date of birth"))
			dep_age.append(age)

		e_stat = applicant.get("Employment Details", {}).get("Employment Status", {})

		if e_stat == "Employed":
			employment = "Employed"
		elif e_stat == "Self Employed (Sole Trader/Partnership)":
			employment = "Self Employed"
		elif e_stat == "Self Employed (Ltd Company/Director)":
			employment = "Contractor"
		elif e_stat == "Retired":
			employment = "Retired"
		else:
			employment = "Not Employed"

		AdditionalIncome = applicant.get("Additional Income (Annual)", [])
		ftb = applicant.get("Applicant Type")
		postcode = data["Property Details"]["Property Details"].get("Post Code", "BT15GS")

		kensington = {
				"main_applicant": True if i==0 else False,
				"date_of_birth": datetime.strptime(applicant.get("Date of Birth", ""), "%d/%m/%Y").strftime("%Y-%m-%d"),
				"planned_retirement_age": applicant.get("expected retirement age", 0),
				"post_code": postcode,
				"employment_status": employment,
				"salary": applicant.get("Employment Details", 0).get("Basic Annual Income", 0),
				"bonus": AdditionalIncome.get("Regular Bonus", 0),
				"commission": AdditionalIncome.get("Commission", 0),
				"overtime": AdditionalIncome.get("Irregular Overtime", 0),
				"allowances": 0,
				"self_employed_income": 0,
				"ftb": True if ftb == "First Time Buyer" else False,
				"other_income": [],
				"ai_score": 0,
				"rn_score": 500
			}

		applicant_data.append(kensington)

	return applicant_data, num_of_dependants, dep_age

def get_product_range(data):
	Loan_Amount = data["Mortgage Requirement"].get("Loan Amount", 0)
	Purchase_Price = data["Mortgage Requirement"].get("Purchase Price", 0)
	loan_term = data["Mortgage Requirement"].get("Loan Term", 60)
	loan_term_years = str(int(loan_term/12)) + "yr"
	product_term = str(int(data["Mortgage Requirement"].get("Product term", 0)/12))+"yr"
	terms = [loan_term_years, product_term]

	ken_product = json.load(open("kensington_product_range.json"))
	mortgage_type = data["Mortgage Requirement"].get("Mortgage Type")
	LTV = int((Loan_Amount / Purchase_Price)*100)

	max_ltv = 0
	if LTV<=60:
		max_ltv = 60
	elif LTV>60 and LTV<=75:
		max_ltv = 75
	elif LTV>75 and LTV<=80:
		max_ltv = 80
	elif LTV>80 and LTV<=85:
		max_ltv = 85
	elif LTV>85 and LTV<=90:
		max_ltv = 90
	else:
		max_ltv = 95

	if mortgage_type == "Standard Residential":
		range_name = "Residential Fixed For Term"
	elif mortgage_type == "Right To Buy":
		range_name = "Residential RTB"
	elif mortgage_type == "Shared Ownership":
		range_name = "Residential Shared Ownership"
	elif mortgage_type == "Shared Equity / Help To Buy":
		range_name = "Residential HTB"
	else:
		range_name = "Residential Select"

	if range_name=="Residential Fixed For Term":
		subtype = "Individual"
	elif range_name=="Residential HTB":
		subtype = "HTB"
	elif range_name=="Residential RTB":
		subtype = "RTB"
	elif range_name=="Residential Shared Ownership":
		subtype = "SharedOwnership"
	else:
		subtype = "Individual"

	#options = [x for x in ken_product if f"{range_name}" in x["PROD_RELEASE_NARR"]]

	#selected_options = [x for x in options if any(term in x["PROD_RELEASE_NARR"] for term in (loan_term_years, product_term)) and str(max_ltv) in x["PROD_RELEASE_NARR"]]
	selected = []
	for x in ken_product:
		if f"{range_name}" in x["PROD_RELEASE_NARR"]:
			for term in terms:
				if term in x["PROD_RELEASE_NARR"] and str(max_ltv) in x["PROD_RELEASE_NARR"]:
					selected.append(x)
		else:
			if "Shared Own" in x["PROD_RELEASE_NARR"]:
				for term in terms:
					if term in x["PROD_RELEASE_NARR"] or str(max_ltv) in x["PROD_RELEASE_NARR"]:
						selected.append(x)

	selected_option = selected[0]

	product_range = range_name.replace(' ','+')
	product_code = selected_option.get("PROD_REFERENCE", "").replace(' ','+')
	product_description = selected_option.get("PROD_RELEASE_NARR", "").replace(' ','+')
	product_assessment_rate = round(float(selected_option.get("INTRA_RATE_01", 0).strip('%'))/100, 4)
	product_base_interest_rate = round(float(selected_option.get("Affordability_Assessment_Rate", 0).strip('%'))/100, 4)

	return product_range, product_code, product_description, product_assessment_rate, product_base_interest_rate, max_ltv, subtype

def get_mortgage_data(data, num_of_dependants, dep_age):
	product_range, product_code, product_description, product_assessment_rate, product_base_interest_rate, max_ltv, subtype = get_product_range(data)
	mortgage_data = {}
	Loan_Amount = data["Mortgage Requirement"].get("Loan Amount", 0)
	Purchase_Price = data["Mortgage Requirement"].get("Purchase Price", 0)
	credit = data["Client Details"][0]["Outgoings"].get("Credit Commitments", 0)
	postcode = data["Property Details"]["Property Details"].get("Post Code", "BT15GS")
	loan_term = data["Mortgage Requirement"].get("Loan Term", 60)
	loan_term_years = str(int(loan_term/12)) + "yr"
	product_term = str(int(data["Mortgage Requirement"].get("Product term", 0)/12))+"yr"
	
	#mortgage_data["checking"] = loan_term_years
	mortgage_data["loan_type"] = "Residential"
	mortgage_data["loan_subtype"] = subtype
	mortgage_data["loan_purpose"] = data["Mortgage Requirement"].get("Loan Purpose")
	mortgage_data["product_initial_rate_period"] = 60
	mortgage_data["credit_impaired"] = False
	mortgage_data["loan_amount"] = Loan_Amount
	mortgage_data["loan_term_requested"] = loan_term
	mortgage_data["equity_loan_htb"] = False
	mortgage_data["equity_loan_start_date"] = "0001-01-01"
	mortgage_data["number_applicants"] = data.get("No of Applicant")
	mortgage_data["property_region"] = ""
	mortgage_data["property_postcode"] = postcode.replace(' ','')
	mortgage_data["property_valuation"] = Purchase_Price

	mortgage_data["product_range"] = product_range
	mortgage_data["product_code"] = product_code
	mortgage_data["product_description"] = product_description
	mortgage_data["product_assessment_rate"] = product_assessment_rate
	mortgage_data["covid_product_assessment_rate"] = 0
	mortgage_data["product_base_interest_rate"] = product_base_interest_rate

	mortgage_data["product_max_ltv"] = round(float(max_ltv/100),2)
	mortgage_data["credit_expenditure"] = 0 if credit in ["null", None] else credit
	mortgage_data["childcare"] = 0
	mortgage_data["school_fees"] = 0
	mortgage_data["maintenance"] = 0
	mortgage_data["ground_rent_service_charge"] = 0
	mortgage_data["shared_ownership_rent"] = 0
	mortgage_data["number_other_occupants"] = num_of_dependants
	mortgage_data["age_other_occupants"] = str(dep_age)
	mortgage_data["application_identifier"] = "KMC_Residential"

	return mortgage_data

def get_payload(data):
	applicants, num_of_dependants, dependents_age_list = get_applicants(data)
	mortgages = get_mortgage_data(data, num_of_dependants, dependents_age_list)

	json_payload = {}

	json_payload = {
		"applicant": applicants,
		**mortgages
	}

	base_payload = json.dumps(json_payload, separators=(',',':'))
	payload = f"={urllib.parse.quote(base_payload)}"
	# payload = f"={base_payload}"

	return payload

def main(config_file):
	with open(config_file) as file:
		data = json.load(file)
	payload = get_payload(data)

	response = requests.post(url, headers=headers, data=payload)
	if response.status_code==200:
		response_json = response.json()
		print("result : PASS")
		print(response_json)
	else:
		print(f"Error : {response.status_code}\n")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)