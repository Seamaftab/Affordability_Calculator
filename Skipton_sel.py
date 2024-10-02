from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import time
import json

def main(config_file):
	with open(config_file) as file:
		data = json.load(file)

	null = ["null", None]
	Mortgage_Type = data["Mortgage Requirement"].get("Mortgage Type")
	Payment_Method = data["Mortgage Requirement"].get("Payment Method")
	Loan_Term = int(data["Mortgage Requirement"].get("Loan Term")/12)
	loan_term_months = int(data["Mortgage Requirement"].get("Loan Term")%12)
	Product_Term = data["Mortgage Requirement"].get("Product term")
	Loan_Type = data["Mortgage Requirement"].get("Loan Purpose")
	Purchase_Price = data["Mortgage Requirement"].get("Purchase Price", 0)
	loan_amount = data["Mortgage Requirement"].get("Loan Amount", 0)
	share = data["Mortgage Requirement"].get("Share of Value (%)")
	existing_mortgage_amount = data.get("Existing Mortgage Details", {}).get("current Mortgage Outstanding", 0)

	num_of_applicants = data.get("No of Applicant")
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])
	for applicant in applicant_details:
		num_of_dependants += len(applicant.get("dependants"))

	location = data["Property Details"].get("Property Location")

	expenses = data["Client Details"][0].get("Outgoings", [])
	groceries = expenses.get("Living Costs", {}).get("Groceries", 0)
	council_tax = expenses.get("Household", {}).get("Council Tax", 0)
	transport = 0 if expenses.get("Transport") in null else expenses.get("Transport", 0)

	service = Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	driver.get("https://affordability.skipton-intermediaries.co.uk/default.aspx")
	try:
		time.sleep(3)
		driver.find_element(By.CSS_SELECTOR, "#onetrust-accept-btn-handler").click()
	except:
		pass

	if num_of_applicants==1:
		applicant_number = "#MainContent_rblNumberOfApplicants_0"
	elif num_of_applicants==2:
		applicant_number = "#MainContent_rblNumberOfApplicants_1"
	elif num_of_applicants==3:
		applicant_number = "#MainContent_rblNumberOfApplicants_2"
	else:
		applicant_number = "#MainContent_rblNumberOfApplicants_3"

	driver.find_element(By.CSS_SELECTOR, applicant_number).click()
	driver.find_element(By.CSS_SELECTOR, "#MainContent_txtNoOfAdultDependants").send_keys(str(num_of_applicants+1+num_of_dependants))
	driver.find_element(By.CSS_SELECTOR, "#MainContent_txtNoOfChildDependants").send_keys(str(num_of_dependants))
	driver.find_element(By.CSS_SELECTOR, "#MainContent_txtPurchasePrice").send_keys(str(Purchase_Price))
	driver.find_element(By.CSS_SELECTOR, "#MainContent_txtLoanAmount").send_keys(str(loan_amount))
	if Product_Term>=60:
		driver.find_element(By.CSS_SELECTOR, "#MainContent_rblWillTakeLongTermFixedProduct_0").click()
	else:
		driver.find_element(By.CSS_SELECTOR, "#MainContent_rblWillTakeLongTermFixedProduct_1").click()

	if Payment_Method == "Repayment":
		repay = "#MainContent_rblRepaymentType_0"
	elif Payment_Method == "Interest Only":
		repay = "#MainContent_rblRepaymentType_1"
	else:
		repay = "#MainContent_rblRepaymentType_2"

	driver.find_element(By.CSS_SELECTOR, repay).click()
	if repay == "#MainContent_rblRepaymentType_2":
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtInterestOnlyAmount").send_keys(str(Purchase_Price-loan_amount))

	driver.find_element(By.CSS_SELECTOR, "#MainContent_txtTermYears").send_keys(str(Loan_Term))
	driver.find_element(By.CSS_SELECTOR, "#MainContent_txtTermMonths").send_keys(str(loan_term_months))

	if location == "Northern Ireland":
		loc = "ni"
	elif location == "England":
		loc = "ea"
	elif location == "Scotland":
		loc = "sc"
	else:
		loc = "wa"

	property_at = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_ddlRegion"))
	property_at.select_by_value(loc)

	driver.find_element(By.CSS_SELECTOR, "#MainContent_rblMainResidence_0").click()
	driver.find_element(By.CSS_SELECTOR, "#MainContent_txtFeeAmount").send_keys("0")

	driver.find_element(By.CSS_SELECTOR, "#MainContent_btnNext").click()

	for i, applicant in enumerate(applicant_details):
		time.sleep(1)
		apptype = applicant.get("Applicant Type")
		if apptype == "First Time Buyer":
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rptApplicants_rblFirstTimeBuyer_{i}_0_{i}").click()
		else:
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rptApplicants_rblFirstTimeBuyer_{i}_1_{i}").click()

		emp_status = applicant["Employment Details"].get("Employment Status")
		if emp_status == "Employed":
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rptApplicants_rblEmploymentTypes_{i}_0_{i}").click()
		elif emp_status == "Retired":
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rptApplicants_rblEmploymentTypes_{i}_2_{i}").click()
		elif emp_status == "Self Employed (Sole Trader/Partnership)":
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rptApplicants_rblEmploymentTypes_{i}_3_{i}").click()
		elif emp_status == "Not Working":
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rptApplicants_rblEmploymentTypes_{i}_4_{i}").click()
		else:
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rptApplicants_rblEmploymentTypes_{i}_1_{i}").click()

		driver.find_element(By.CSS_SELECTOR, f"#MainContent_rptApplicants_rblresidentialStatus_{i}_1_{i}").click()

	driver.find_element(By.CSS_SELECTOR, "#MainContent_btnNext").click()

	for i, applicant in enumerate(applicant_details):
		time.sleep(1)
		income = applicant["Employment Details"].get("Basic Annual Income")
		overtime = applicant.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0)
		regular_bonus = applicant.get("Additional Income (Annual)", {}).get("Regular Bonus", 0)
		commission = applicant.get("Additional Income (Annual)", {}).get("Commission", 0)
		self_income_last_year = applicant.get("Employment Details", {}).get("Last Year's Net Profits", 0)
		dividends_last_year = applicant.get("Employment Details", {}).get("Last Year's Dividends", 0)

		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome000001{i}").send_keys(income)
		if self_income_last_year > 0:
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rblAdditionalIncome{i}_0").click()
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome2{i}").send_keys(str(overtime+regular_bonus))
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome3{i}").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome4{i}").send_keys(str(self_income_last_year))
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome5{i}").send_keys(str(dividends_last_year))
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome6{i}").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome7{i}").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome8{i}").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome9{i}").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome10{i}").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtIncome110{i}").send_keys("0")
		else:
			driver.find_element(By.CSS_SELECTOR, f"#MainContent_rblAdditionalIncome{i}_1").click()

	driver.find_element(By.CSS_SELECTOR, "#MainContent_btnNext").click()

	for i, applicant in enumerate(applicant_details):
		time.sleep(1)
		credit = 0 if applicant.get("Outgoings", {}).get("Credit Commitments") in null else applicant.get("Outgoings", {}).get("Credit Commitments")
		household_expenses = applicant.get("Outgoings", {}).get("Household")
		rent = household_expenses.get("Mortgage / Rent")
		serviceCharge = household_expenses.get("Service Charge", 0)
		sum_household_expenses = sum(household_expenses.values())

		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000003_{i}").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000005_{i}").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000006_{i}").send_keys("0")
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000023_{i}").send_keys(str(credit))
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000024_{i}").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000031_{i}").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000033_{i}").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000034_{i}").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000035_{i}").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000036_{i}").send_keys(str(serviceCharge))
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000037_{i}").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000038_{i}").send_keys(str(rent))
		driver.find_element(By.CSS_SELECTOR, f"#MainContent_txtExpenditure_000041_{i}").send_keys("0")

	driver.find_element(By.CSS_SELECTOR, "#MainContent_btnNext").click()

	max_affordable = driver.find_element(By.CSS_SELECTOR, "#MainContent_lblMaximumLoan").text
	print("max_affordable : ",max_affordable)

	driver.close()
config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)