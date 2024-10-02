import json
import requests
import urllib
from bs4 import BeautifulSoup

url = "https://assets.lloydsbankbusiness.com/sw-affordabilitycalculator/?type=consumer"

headers = {
	"Accept":"*/*",
	"Accept-Encoding":"gzip, deflate, br, zstd",
	"Accept-Language":"en-US,en;q=0.9,bn;q=0.8",
	"Cache-Control":"no-cache",
	"Connection":"keep-alive",
	"Content-Length":"5261",
	"Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
	"Dnt":"1",
	"Host":"assets.lloydsbankbusiness.com",
	"Origin":"https://assets.lloydsbankbusiness.com",
	"Referer":"https://assets.lloydsbankbusiness.com/sw-affordabilitycalculator/?type=consumer",
	"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"X-Microsoftajax":"Delta=true",
	"X-Requested-With":"XMLHttpRequest"
}

VIEWSTATE = None
VIEWSTATEGENERATOR = None
EVENTVALIDATION = None
cookies = None

def get_tokens():
	global VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION, cookies
	try:
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			soup = BeautifulSoup(response.content, "html.parser")
			view_state = soup.find("input", {"id": "__VIEWSTATE"})["value"]
			view_state_generator = soup.find("input", {"id": "__VIEWSTATEGENERATOR"})["value"]
			event_validation = soup.find("input", {"id": "__EVENTVALIDATION"})["value"]

			VIEWSTATE = view_state
			VIEWSTATEGENERATOR = view_state_generator
			EVENTVALIDATION = event_validation
			cookies = response.cookies

			return VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION
		else:
			return f"Request failed with status code {response.status_code}"
	except requests.RequestException as e:
		return f"Request failed: {e}"

def get_mortgage_data(data, num_of_dependants):
	global VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION, cookies
	mortgage_data = {}

	Mortgage_Type = data["Mortgage Requirement"].get("Mortgage Type")

	mortgage_data["scriptManager"] = "udpAffordabilityCalc|submitproduct"
	mortgage_data["__EVENTTARGET"] = "submitproduct"
	mortgage_data["__EVENTARGUMENT"] = ""
	mortgage_data["__VIEWSTATE"] = VIEWSTATE
	mortgage_data["__VIEWSTATEGENERATOR"] = VIEWSTATEGENERATOR
	mortgage_data["__EVENTVALIDATION"] = EVENTVALIDATION
	mortgage_data["adults"] = data.get("No of Applicant", 1)
	mortgage_data["children"] = num_of_dependants
	mortgage_data["ddlIsScottish"] = "Y" if data["Property Details"].get("Property Location") == "Soctland" else "N"
	mortgage_data["propertyValue"] = data["Mortgage Requirement"].get("Purchase Price", 0)
	mortgage_data["amount"] = data["Mortgage Requirement"].get("Loan Amount", 0)
	mortgage_data["term"] = int(data["Mortgage Requirement"].get("Loan Term")/12)
	mortgage_data["interestonly"] = 0
	mortgage_data["monthlypremium"] = 0
	mortgage_data["propertytype"] = "freehold"

	return mortgage_data

def get_applicants(data):
	applicant_data = {}
	applicant_details = data.get("Client Details", [])
	num_of_dependants = 0

	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details)>1 else {}

	num_of_dependants = len(applicant_one.get("dependants", [])) + len(applicant_two.get("dependants", []))

	credit_one = applicant_one["Outgoings"].get("Credit Commitments")
	credit_two = applicant_two.get("Outgoings", {}).get("Credit Commitments")

	applicants = {
		"ddlselfEmployedIncome":"N",
		"annualincome1":applicant_one["Employment Details"].get("Basic Annual Income", 0),
		"annualincome2":applicant_two.get("Employment Details", {}).get("Basic Annual Income", 0),
		"overtime1":applicant_one.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0),
		"overtime2":applicant_two.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0),
		"bonus1":applicant_one.get("Additional Income (Annual)", {}).get("Regular Bonus", 0),
		"bonus2":applicant_two.get("Additional Income (Annual)", {}).get("Regular Bonus", 0),
		"commission1":applicant_one.get("Additional Income (Annual)", {}).get("Commission", 0),
		"commission2":applicant_two.get("Additional Income (Annual)", {}).get("Commission", 0),
		"otherincome1":"None",
		"otherincome11":0,
		"otherincome21":0,
		"otherincome2":"None",
		"otherincome12":0,
		"otherincome22":0,
		"otherincome3":"None",
		"otherincome13":0,
		"otherincome23":0,
		"otherincome4":"None",
		"otherincome14":0,
		"otherincome24":0,
		"credit1":0 if credit_one in ["null", None] else credit_one,
		"credit2":0 if credit_two in ["null", None] else credit_two,
		"card1":0,
		"card2":0,
		"mortgage1":0,
		"mortgage2":0,
		"ddlOtherProperties":"No",
		"txtMorBalance1":0,
		"txtMorTerm1":0,
		"txtMorBalance2":0,
		"txtMorTerm2":0,
		"txtMorBalance3":0,
		"txtMorTerm3":0,
	}

	applicant_data.update(applicants)

	return applicant_data, num_of_dependants

def get_payload(data):
    applicants, num_of_dependants = get_applicants(data)
    mortgages = get_mortgage_data(data, num_of_dependants)

    json_payload = mortgages
    json_payload.update(applicants)
    json_payload["__ASYNCPOST"] = "true"

    payload = urllib.parse.urlencode(json_payload)

    return payload

def main(config_file):
    global VIEWSTATE, VIEWSTATEGENERATOR, EVENTVALIDATION, cookies

    if not (VIEWSTATE and VIEWSTATEGENERATOR and EVENTVALIDATION and cookies):
        get_tokens()

    with open(config_file) as file:
        data = json.load(file)
    payload = get_payload(data)

    response = requests.post(url, data=payload, headers=headers, cookies=cookies)
    if response.status_code==200:
    	try:
    		soup = BeautifulSoup(response.content, 'html.parser')
    		max_borrowing = soup.select_one("#loanamount").text
    		print("Result : PASS")
    		print(f"Maximum Loan Amount : {max_borrowing}\n")
    	except:
    		print(f"Something went wrong\n")
    else:
    	print(f"Error : {response.status_code}\n")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)