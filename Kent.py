import json
import requests
from bs4 import BeautifulSoup

url = "https://www.kentrelianceforintermediaries.co.uk/Umbraco/Surface/ResidentialCalculatorSurface/SubmitForm"

def get_mortgage_data(data):
	mortgage_data = {}
	applicants, num_of_dependants = get_applicants(data)

	mortgage_data["txtNoOfApplicants"] = data.get("No of Applicant")
	mortgage_data["txtNoOfDependentChild"] = num_of_dependants
	mortgage_data["txtNoOfOtherAdults"] = 0
	mortgage_data["txtLoanAmount"] = data["Mortgage Requirement"].get("Loan Amount", 0)
	mortgage_data["txtLoanTerms"] = int(data["Mortgage Requirement"].get("Loan Term", 0)/12)
	mortgage_data["txtInitialInterestRate"] = 1
	mortgage_data["txtReversionaryMarginRate"] = 1
	mortgage_data["txtInterestOnlyPortion"] = 0

	Mortgage_Type = data["Mortgage Requirement"].get("Mortgage Type")
	if Mortgage_Type == "Standard Residential":
		mortgage_data["txtproducttype"] = "Residential"
	elif Mortgage_Type == "Shared Ownership":
		mortgage_data["txtproducttype"] = "Shared"
	else:
		mortgage_data["txtproducttype"] = "Income Flex"

	mortgage_data["txtfiveyrfixed"] = "Fixed - 5 Year"
	mortgage_data["txtsmoker"] = ""

	return mortgage_data

def get_applicants(data):
	applicant_data = {}
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])

	for i in range(4):
		try:
			applicant = applicant_details[i]
		except Exception as e:
			applicant = None

		num_of_dependants += len(applicant.get("dependants")) if applicant else 0
		Income = applicant.get("Employment Details", []) if applicant else 0
		AdditionalIncome = applicant.get("Additional Income (Annual)", []) if applicant else 0

		kent = {
            f"Customer_Employment_Primary_App{i+1}": "Please Select",
            f"txtGrossSalary1App{i+1}": applicant["Employment Details"].get("Basic Annual Income", 0) if applicant else 0,
            f"txtBonus1App{i+1}": AdditionalIncome.get("Regular Bonus", 0) if applicant else 0,
            f"txtCommission1App{i+1}": AdditionalIncome.get("Commission", 0) if applicant else 0,
            f"txtOvertime1App{i+1}": AdditionalIncome.get("Irregular Overtime", 0) if applicant else 0,
            f"txtAllowance1App{i+1}": 0,
            f"txtNetProfit11App{i+1}": 0,
            f"txtNetProfit21App{i+1}": 0,
            f"txtNetProfit31App{i+1}": 0,
            f"third_emp_App{i+1}": "Yes",
            f"txtDividendIncome{i+1}": 0,
            f"secondary_emp_App{i+1}": "No",
            f"Customer_Employment_Secondary_App{i+1}": "Please Select",
            f"txtGrossSalary2App{i+1}": 0,
            f"txtBonus2App{i+1}": 0,
            f"txtCommission2App{i+1}": 0,
            f"txtOvertime2App{i+1}": 0,
            f"txtAllowance2App{i+1}": 0,
            f"txtNetProfit12App{i+1}": 0,
            f"txtNetProfit22App{i+1}": 0,
            f"txtNetProfit32App{i+1}": 0,
            f"other_income_App{i+1}": "No",
            f"txtPensionApp{i+1}": 0,
            f"txtCourtOrderMaintenanceApp{i+1}": 0,
            f"txtWorkingTaxCreditApp{i+1}": 0,
            f"txtChildTaxCreditApp{i+1}": 0,
            f"txtHousingAllowanceApp{i+1}": 0,
            f"txtInvestmentIncomeApp{i+1}": 0,
            f"txtTrustFundApp{i+1}": 0,
            f"txtFamilyAllowanceApp{i+1}": 0,
            f"txtMobilityAllowanceApp{i+1}": 0,
            f"txtOtherIncomeApp{i+1}": 0
		}
		applicant_data.update(kent)

	credit = applicant["Outgoings"].get("Credit Commitments", 0) if applicant else 0
	Rent = applicant["Outgoings"]["Household"].get("Mortgage / Rent", 0) if applicant else 0
	for i in range(4):
		expenses = {
            f"txtMonthlySacrificeApp{i+1}": 0,
            f"txtCreditCardBalanceApp{i+1}": 0 if credit in ["null", None] else credit,
            f"txtMonthlyLoanPaymentApp{i+1}": 0,
            f"txtMonthlyMaintenancePaymentApp{i+1}": 0,
            f"txtMonthlyNurseryorSchoolPaymentApp{i+1}": 0,
            f"txtMonthlyMailOrderPaymentApp{i+1}": 0,
            f"txtRentalorServiceChargesApp{i+1}": 0 if Rent in ["null", None] else Rent
		}
		applicant_data.update(expenses)

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
	payload = get_payload(data)

	response = requests.request("POST", url, data=payload)

	if response.status_code == 200:
		soup = BeautifulSoup(response.text, "html.parser")
		yearly_amount = soup.select_one("#ltrMaxLoanAmtIntOnly").text
		monthly_rate = soup.select_one("#ltrMonthlyPaymentIntOnly").text
		print(f"Max Loan Amount : ", yearly_amount,"\nMonthly Rate : ", monthly_rate, "\n")
	elif response.status_code == 429:
		response = requests.post(url,headers=headers, data=payload)
		print(f"429")
	else:
		print(f"Request failed with status code: {response.status_code}")
		print(f"Error message: {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
   main()
