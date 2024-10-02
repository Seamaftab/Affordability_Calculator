import requests
import json
import urllib
from bs4 import BeautifulSoup

url = "https://online.accordmortgages.com/public/mortgages/quick_enquiry.do"
request_cookies = None

headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
  'Connection': 'keep-alive',
  'Content-Type': 'application/x-www-form-urlencoded',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

def get_csrf_token():
	global csrf_token, request_cookies
	try:
		response = requests.get(url, headers=headers, verify=False)
		if response.status_code == 200:
			soup = BeautifulSoup(response.content, "html.parser")
			token_input = soup.find("input", {"name": "appname_token"})
			if token_input:
				csrf_token = token_input.get("value")
				request_cookies = response.cookies
				return csrf_token
			else:
				return "Token input not found."
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
		additonals = applicant.get("Additional Income (Annual)", [])

		count = i+1
		if count == 1:
			num = "One"
		else:
			num = "Two"

		accord = {
			f"applicant{num}AdultsIndependent": 1,
			f"applicant{num}ChildrenUnder17": len(applicant.get("dependants")),
			f"applicant{num}EmploymentType": "Employed/retired clients",
			f"applicant{num}GrossIncome": regular.get("Basic Annual Income", 0),
			f"applicant{num}OvertimeOrBonus": additonals.get("Regular Bonus", 0),
			f"applicant{num}Commission": additonals.get("Commission", 0),
			f"applicant{num}SecondJob": 0,
			f"applicant{num}CommuttingAllow": 0,
			f"applicant{num}StandbyAllow": 0,
			f"applicant{num}AccommodationAllow": 0,
			f"applicant{num}ChildcareVouchers": 0,
			f"applicant{num}LastYearProfit": regular.get("Last Year's Net Profits", 0),
			f"applicant{num}Year2Profit": regular.get("Previous Year's Net Profits", 0),
			f"applicant{num}Remuneration": 0,
			f"applicantShareHolding": "N",
			f"applicant{num}CurrentYearDividend": regular.get("Last Year's Dividends", 0),
			f"applicant{num}Year2Dividend": regular.get("Previous Year's Dividends", 0),
			f"applicant{num}CurrentYearDividendNetProfit": regular.get("Last Year's Retained Profits",0),
			f"applicant{num}Year2DividendNetProfit": regular.get("Previous Year's Retained Profits",0),
			f"applicant{num}MaintRcvd": 0,
			f"applicant{num}RentalIncome": 0,
			f"applicant{num}ChildIncomeDetails": 0,
			f"applicant{num}OtherBenefitsDetails": 0,
			f"applicant{num}HousingAssociationRentExp": "",
			f"applicant{num}TotalLoansHP": 0,
			f"applicant{num}MonthlyLoansHP": 0,
			f"applicant{num}MonthlyMaint": 0,
			f"applicant{num}MonthlySchoolFees": 0,
			f"applicant{num}MonthlyMortgagePayments": 0,
			f"applicant{num}MonthlySigOutgoings": 0,
			f"applicant{num}MonthlyLoansHPToBeRepaid": 0,
			f"applicant{num}TotalCCBalances": 0,
			f"applicant{num}TotalCCBalancesToBeRepaid": 0,
			f"applicant{num}OverdraftBalance": 0
		}

		applicant_data.update(accord)

	if len(applicant_details)<2:
		Two = {
			"applicantTwoAdultsIndependent": 0,
			"applicantTwoChildrenUnder17": 0,
			"applicantTwoEmploymentType": 0,
			"applicantTwoGrossIncome": 0,
			"applicantTwoOvertimeOrBonus": 0,
			"applicantTwoCommission": 0,
			"applicantTwoSecondJob": 0,
			"applicantTwoCommuttingAllow": 0,
			"applicantTwoStandbyAllow": 0,
			"applicantTwoAccommodationAllow": 0,
			"applicantTwoChildcareVouchers": 0,
			"applicantTwoLastYearProfit": 0,
			"applicantTwoYear2Profit": 0,
			"applicantTwoRemuneration": 0,
			"applicantTwoCurrentYearDividend": 0,
			"applicantTwoYear2Dividend": 0,
			"applicantTwoCurrentYearDividendNetProfit": 0,
			"applicantTwoYear2DividendNetProfit": 0,
			"applicantTwoMaintRcvd": 0,
			"applicantTwoRentalIncome": 0,
			"applicantTwoChildIncomeDetails": 0,
			"applicantTwoOtherBenefitsDetails": 0,
			"applicantTwoHousingAssociationRentExp": "",
			"applicantTwoTotalLoansHP": 0,
			"applicantTwoMonthlyLoansHP": 0,
			"applicantTwoMonthlyMaint": 0,
			"applicantTwoMonthlySchoolFees": 0,
			"applicantTwoMonthlyMortgagePayments": 0,
			"applicantTwoMonthlySigOutgoings": 0,
			"applicantTwoMonthlyLoansHPToBeRepaid": 0,
			"applicantTwoTotalCCBalances": 0,
			"applicantTwoTotalCCBalancesToBeRepaid": 0,
			"applicantTwoOverdraftBalance": 0
		}

		applicant_data.update(Two)

	applicant_data["calculateBtn.value"] = "Calculate"

	return applicant_data, num_of_dependants

def get_mortgage_data(data, csrf):
	mortgage_data = {}
	no_of_applicants = data.get("No of Applicant")
	applicants, num_of_dependants = get_applicants(data)

	mortgage_data["appname_token"]=csrf
	mortgage_data["adults17OverType"]="Joint" if no_of_applicants>1 else "Sole"
	mortgage_data["adultsIndependent"]=0
	mortgage_data["childrenUnder17"]=num_of_dependants
	mortgage_data["termYears"]=int(data["Mortgage Requirement"].get("Loan Term")/12)
	mortgage_data["termMonths"]=int(data["Mortgage Requirement"].get("Loan Term")%12)
	mortgage_data["purchaseType"]="Y" if data["Mortgage Requirement"].get("Loan Purpose") == "Purchase" else "N"
	mortgage_data["mortgageType"]="Standard Purchase" if data["Mortgage Requirement"].get("Mortgage Type") == "Standard Residential" else "Standard Remortgage"
	mortgage_data["newBuild"]="Y"
	mortgage_data["purchasePriceValuation"]=data["Mortgage Requirement"].get("Purchase Price", 0)
	mortgage_data["equityLoanAmount"]=""
	mortgage_data["purchasePriceOfBorrowerShare"]=""
	mortgage_data["repaymentAmount"]=data["Mortgage Requirement"].get("Loan Amount", 0)

	return mortgage_data

def get_payload(data):
	csrf = get_csrf_token()
	mortgages = get_mortgage_data(data, csrf)
	applicants, num_of_dependants = get_applicants(data)

	json_payload = mortgages
	json_payload.update(applicants)
	payload = urllib.parse.urlencode(json_payload)

	return payload

def main():
	global request_cookies
	with open(config) as file:
		data = json.load(file)
	payload = get_payload(data)

	response = requests.request("POST", url, headers=headers, data=payload, cookies=request_cookies, verify=False)
	soup = BeautifulSoup(response.text, 'html.parser')
	try:
		result = soup.select_one("#results-calc h2").text
		print("Response : ACCEPTED\n",result)
	except:
		result = soup.select_one("#results-calc").text
		print("Response : DECLINED\n",result)

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
   main()