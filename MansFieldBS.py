import requests
import json
import urllib
from bs4 import BeautifulSoup

url = "https://www.mansfieldbs.co.uk/intermediaries/affordability-calculator/?DoCalc"

headers = {
	"Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
	"Accept-Encoding":"gzip, deflate, br, zstd",
	"Accept-Language":"en-US,en;q=0.9,bn;q=0.8",
	"Content-Type":"application/x-www-form-urlencoded",
	"Dnt":"1",
	"Host":"www.mansfieldbs.co.uk",
	"Origin":"https://www.mansfieldbs.co.uk",
	"Referer":"https://www.mansfieldbs.co.uk/intermediaries/affordability-calculator/?DoCalc",
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_mortgage_data(data, num_of_dependants):
	mortgage_data = {}

	Product_term = data["Mortgage Requirement"].get("Product term", 0)
	no_of_applicants = data.get("No of Applicant")
	payment = data["Mortgage Requirement"].get("Payment Method")
	location = data["Property Details"].get("Property Location")

	mortgage_data["product_is_5_year"] = "yes" if Product_term>=60 else "no"
	mortgage_data["product_user_rate"] = 1 if Product_term>=60 else ""
	mortgage_data["product_type"] = "standard_variable_rate" if Product_term<60 else "" # "lifetime_discount" can also be n option instead of "standard_variable_rate"
	mortgage_data["application"] = "joint" if no_of_applicants>1 else "single"
	mortgage_data["dependent_partner"] = "N" if no_of_applicants ==1 else ""
	mortgage_data["type"] = "repayment" if payment == "Repayment" else "interest-only"
	mortgage_data["dependents"]= num_of_dependants

	if location == "England" or location == "Wales":
		mortgage_data["tax-authority"] = "england and wales"
	else:
		mortgage_data["tax-authority"] = "scotland"

	mortgage_data["purchase-price"]= data["Mortgage Requirement"].get("Purchase Price", 0)
	mortgage_data["mortgage-amount"]= data["Mortgage Requirement"].get("Loan Amount", 0)
	mortgage_data["term"]= int(data["Mortgage Requirement"].get("Loan Term", 0)/12)

	return mortgage_data

def get_rest():
	rest = {}

	rest["adviser"]= ""
	rest["company"]= ""
	rest["_do_calc_field"]= "2d623f27b8"
	rest["_wp_http_referer"]= "/intermediaries/affordability-calculator/?DoCalc"

	return rest

def get_applicants(data):
	applicant_data = {}
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])

	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details)>1 else {}
	num_of_dependants += len(applicant_one.get("dependants", [])) + len(applicant_two.get("dependants", []))

	e_one = applicant_one.get("Employment Details", {}).get("Employment Status", {})

	if e_one == "Employed":
		e_stat_one = "employed - full time"
	elif e_one == "Self Employed (Sole Trader/Partnership)":
		e_stat_one = "self employed"
	elif e_one == "Self Employed (Ltd Company/Director)":
		e_stat_one = "company director"
	elif e_one == "Retired":
		e_stat_one = "retired"
	else:
		e_stat_one = "not working"

	e_two = applicant_two.get("Employment Details", {}).get("Employment Status", {})

	if e_two == "Employed":
		e_stat_two = "employed - full time"
	elif e_two == "Self Employed (Sole Trader/Partnership)":
		e_stat_two = "self employed"
	elif e_two == "Self Employed (Ltd Company/Director)":
		e_stat_two = "company director"
	elif e_two == "Retired":
		e_stat_two = "retired"
	elif e_two == "Not Working":
		e_stat_two = "not working"
	else:
		e_stat_two = ""

	outgoings_one = applicant_one.get("Outgoings", {})
	sum_of_outgoings_one = sum(value if value is not None and isinstance(value, (int, float)) else 0 for category, value in outgoings_one.items() if value is not None)
	outgoings_two = applicant_two.get("Outgoings", {})
	sum_of_outgoings_two = sum(value if value is not None and isinstance(value, (int, float)) else 0 for category, value in outgoings_two.items() if value is not None)

	applicant_one_credit = applicant_one["Outgoings"].get("Credit Commitments")
	applicant_two_credit = applicant_two.get("Outgoings", {}).get("Credit Commitments", 0)

	applicants = {
		"app-1-date-of-birth":applicant_one.get("Date of Birth", {}),
		"app-2-date-of-birth":applicant_two.get("Date of Birth", ""),
		"app-1-employment": e_stat_one,
		"app-1-gross-annual-income":applicant_one["Employment Details"].get("Basic Annual Income", 0),
		"app-1-guaranteed-extra-annual-income":applicant_one.get("Additional Income (Annual)").get("Regular Bonus", 0),
		"app-1-gross-dividend":applicant_one.get("Employment Details", {}).get("Last Year's Dividends", 0),
		"app-1-other-annual-income":0,
		"app-2-employment": e_stat_two,
		"app-2-gross-annual-income":applicant_two.get("Employment Details", {}).get("Basic Annual Income", ""),
		"app-2-guaranteed-extra-annual-income":applicant_two.get("Additional Income (Annual)", {}).get("Regular Bonus", ""),
		"app-2-gross-dividend":applicant_two.get("Employment Details", {}).get("Last Year's Dividends", ""),
		"app-2-other-annual-income":0,
		"app-1-monthly-outgoings":sum_of_outgoings_one,
		"app-1-outstanging-credit":0 if applicant_one_credit in ["null", None] else applicant_one_credit,
		"app-2-monthly-outgoings":sum_of_outgoings_two,
		"app-2-outstanging-credit":0 if applicant_two_credit in ["null", None] else applicant_two_credit,
	}

	applicant_data.update(applicants)

	return applicant_data, num_of_dependants

def get_payload(data):
	applicants, num_of_dependants = get_applicants(data)
	mortgages = get_mortgage_data(data, num_of_dependants)
	rest = get_rest()

	json_payload = mortgages
	json_payload.update(applicants)
	json_payload.update(rest)

	payload = urllib.parse.urlencode(json_payload)
	return payload

def main(config_file):
	with open(config_file) as file:
		data = json.load(file)
	payload = get_payload(data)

	data_to_return = {
		"result": None,
		"max_affordable_loan" : "",
		"remarks": ""
	}

	response = requests.post(url, headers=headers, data=payload)

	if response.status_code == 200 :
		try:
			soup = BeautifulSoup(response.text, 'html.parser')
			data_to_return["result"] = soup.select_one(".ap-alert p").text
			data_to_return["remarks"] = soup.select_one(".ap-alert").text
		except:
			data_to_return["result"] = "Something went wrong!"
	else:
		data_to_return["remarks"] = "Request failed, status: {}".format(response.status_code)
	
	return data_to_return

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	print(main(config_file))
	print("\n")