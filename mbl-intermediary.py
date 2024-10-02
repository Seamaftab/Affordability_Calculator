import requests
import json
from bs4 import BeautifulSoup
import urllib.parse


url = "https://www.mbs-intermediaries.com/affordability-calculator/"
req_cookies = None
request_verification_token = None
ufport_token = None

headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
  'Content-Type': 'application/x-www-form-urlencoded',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def update_request_verification_token():
	global req_cookies, request_verification_token, ufport_token
	try:
		response = requests.get(url, headers=headers)
		if response.status_code == 200:
			soup = BeautifulSoup(response.content, "html.parser")
			token = soup.select_one('input[name="__RequestVerificationToken"]')["value"]
			ufprt_token = soup.select_one('input[name="ufprt"]')["value"]
			
			request_verification_token = token
			ufport_token = ufprt_token
			req_cookies = response.cookies
			return request_verification_token
		else:
			return f"Request failed with status code {response.status_code}"
	except requests.RequestException as e:
		return f"Request failed: {e}"

def get_applicants(data):
	applicant_data = {}
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])

	for i, applicant in enumerate(applicant_details):
		num_of_dependants += len(applicant.get("dependants"))

		regular = applicant.get("Employment Details", [])

		mbs_basic = {
			f"GrossAnnualIncome{i+1}": regular.get("Basic Annual Income", 0),
			f"NetMonthlyMainIncome{i+1}": 0,
			f"GrossAnnualOtherIncome{i+1}": 0,
			f"NetMonthlyOtherIncome{i+1}": 0,
			f"Retired{i+1}": True if regular.get("Employment Status") == "Retired" else False,
		}
		applicant_data.update(mbs_basic)

	if len(applicant_details)<2:
		reserve_basic = {
			"GrossAnnualIncome2": "",
			"NetMonthlyMainIncome2": "",
			"GrossAnnualOtherIncome2": "",
			"NetMonthlyOtherIncome2": "",
			"Retired2": False,
		}
		applicant_data.update(reserve_basic)

	return applicant_data, num_of_dependants

def get_expenses(data):
	expenses = {}
	applicant_details = data.get("Client Details", [])

	for i, applicant in enumerate(applicant_details):
		credit = applicant["Outgoings"].get("Credit Commitments")

		mbs_ex = {
			f"PersonalLoans{i+1}": 0,
			f"BankOverdraft{i+1}": 0,
			f"HirePurchase{i+1}": 0,
			f"MortgageOrSecuredLoans{i+1}": 0,
			f"ChildMaintenanceCSA{i+1}": 0,
			f"IntOnlyRepaymentVehicle{i+1}": 0,
			f"CreditCardBalance{i+1}": 0 if credit in ["null", None] else credit,
			f"Other{i+1}": 0,
		} 
		expenses.update(mbs_ex)

	if len(applicant_details)<2:
		reserve_ex = {
			"PersonalLoans2": "",
			"BankOverdraft2": "",
			"HirePurchase2": "",
			"MortgageOrSecuredLoans2": "",
			"ChildMaintenanceCSA2": "",
			"IntOnlyRepaymentVehicle2": "",
			"CreditCardBalance2": "",
			"Other2": "",
		}
		expenses.update(reserve_ex)

	return expenses

def get_mortgage_data(data, num_of_dependants):
	global request_verification_token
	mortgage_data = {}
	no_of_applicants = data.get("No of Applicant")
	mortgage_data["__RequestVerificationToken"] = request_verification_token
	mortgage_data["NumberOfApplicants"]=no_of_applicants
	mortgage_data["Dependants"]=num_of_dependants
	mortgage_data["PostcodeArea"]="Birmingham"
	mortgage_data["LoanBasis"]= "R" if data["Mortgage Requirement"].get("Payment Method") == "Repayment" else "I"
	mortgage_data["LoanAmount"]= data["Mortgage Requirement"].get("Loan Amount", 0)
	mortgage_data["PropertyValuation"]= data["Mortgage Requirement"].get("Purchase Price", 0)
	mortgage_data["MortgageTerm"]=int(data["Mortgage Requirement"].get("Loan Term")/12)
	mortgage_data["ProductPeriod"]=int(data["Mortgage Requirement"].get("Product Term", 60)/12)

	return mortgage_data

def get_rest():
	global ufport_token
	rest = {}

	rest["StandardMultiplier"]=4.5
	rest["OtherMultiplier"]=5
	rest["CreditCardMonthlyRate"]=3
	rest["Type"]="AFO"
	rest["ufprt"] = ufport_token
	return rest

def get_payload(data):
	# request_verification_token = update_request_verification_token()
	applicants, num_of_dependants = get_applicants(data)
	mortgages = get_mortgage_data(data, num_of_dependants)
	expense = get_expenses(data)
	rest = get_rest()

	payload=mortgages
	payload.update(applicants)
	payload.update(expense)
	payload.update(rest)

	return payload

def main(config_file):
	global request_verification_token

	if not request_verification_token:
		update_request_verification_token()

	with open(config_file) as file:
		data = json.load(file)
	for _ in range(2):
		payload = get_payload(data)
		# payload = {f'__RequestVerificationToken={request_verification_token}&NumberOfApplicants=1&Dependants=0&PostcodeArea=Cambridge&GrossAnnualIncome1=60000&NetMonthlyMainIncome1=5000&GrossAnnualOtherIncome1=&NetMonthlyOtherIncome1=&Retired1=false&GrossAnnualIncome2=%20&NetMonthlyMainIncome2=%20&GrossAnnualOtherIncome2=%20&NetMonthlyOtherIncome2=%20&Retired2=false&LoanBasis=R&LoanAmount=150000&PropertyValuation=250000&MortgageTerm=35&ProductPeriod=5&PersonalLoans1=0&BankOverdraft1=&HirePurchase1=%20&MortgageOrSecuredLoans1=%20&ChildMaintenanceCSA1=%20&IntOnlyRepaymentVehicle1=%20&CreditCardBalance1=%20&Other1=%20&PersonalLoans2=%20&BankOverdraft2=%20&HirePurchase2=%20&MortgageOrSecuredLoans2=%20&ChildMaintenanceCSA2=%20&IntOnlyRepaymentVehicle2=%20&CreditCardBalance2=%20&Other2=%20&StandardMultiplier=4.5&OtherMultiplier=5&CreditCardMonthlyRate=3&Type=AFO&ufprt={ufport_token}'}
		response = requests.post(url, headers=headers, data=payload, cookies=req_cookies)
		
		data_to_return = {
			"result": None,
			"max_affordable_loan" : None,
			"remarks": ""
		}

		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			data_to_return["max_affordable_loan"] = soup.select_one('.calcloan-amount.__orange').text.strip()
			data_to_return["result"] = "Pass"
			break
		else:
			data_to_return["result"] = "Fail"
			data_to_return["remarks"] = "Request failed, status: {}".format(response.status_code)
			update_request_verification_token()
			continue
	
	return data_to_return

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	print(main(config_file))