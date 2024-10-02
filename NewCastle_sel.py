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
# def main():
# 	with open('config_one.json') as file:
# 		data = json.load(file)

	null = ["null", None]
	mortgage_type = data["Mortgage Requirement"].get("Mortgage Type")
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
	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details)>1 else {}
	num_of_dependants += len(applicant_one.get("dependants", [])) + len(applicant_two.get("dependants", []))

	applicant_one_empstatus = applicant_one.get("Employment Details", {}).get("Employment Status", "")
	applicant_two_empstatus = applicant_two.get("Employment Details", {}).get("Employment Status", "")
	basic_annual_income1 = applicant_one.get("Employment Details", {}).get("Basic Annual Income", 0)
	basic_annual_income2 = applicant_two.get("Employment Details", {}).get("Basic Annual Income", 0)
	net_income1 = int(basic_annual_income1*0.06704) if applicant_one.get("Employment Details", {}).get("Net Monthly Income") in null else applicant_one.get("Employment Details", {}).get("Net Monthly Income")
	net_income2 = int(basic_annual_income2*0.06704) if applicant_two.get("Employment Details", {}).get("Net Monthly Income") in null else applicant_two.get("Employment Details", {}).get("Net Monthly Income")
	overtime1 = applicant_one.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0)
	overtime2 = applicant_two.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0)
	bonus1 = applicant_one.get("Additional Income (Annual)", {}).get("Regular Bonus", 0)
	bonus2 = applicant_two.get("Additional Income (Annual)", {}).get("Regular Bonus", 0)
	commision1 = applicant_one.get("Additional Income (Annual)", {}).get("Commission", 0)
	commision2 = applicant_two.get("Additional Income (Annual)", {}).get("Commission", 0)

	self_income_last_year_1 = applicant_one.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	self_income_previous_year_1 = applicant_one.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	self_income_last_year_2 = applicant_two.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	self_income_previous_year_2 = applicant_two.get("Employment Details", {}).get("Previous Year's Net Profits", 0)

	location = data["Property Details"].get("Property Location")

	household_expenses_1 = applicant_one.get("Outgoings", {}).get("Household")
	rent_1 = household_expenses_1.get("Mortgage / Rent")
	serviceCharge_1 = household_expenses_1.get("Service Charge", 0)
	household_expenses_2 = applicant_two.get("Outgoings", {}).get("Household", {})
	# rent_2 = 0 if applicant_two.get("Outgoings", {}).get("Household", {}).get("Mortgage / Rent", 0) in null else applicant_two.get("Outgoings", {}).get("Household").get("Mortgage / Rent", 0)
	# serviceCharge_2 = 0 if applicant_two.get("Outgoings", {}).get("Household", {}).get("Service Charge", 0) in null else applicant_two.get("Outgoings", {}).get("Household").get("Service Charge", 0)
	rent_2 = 0
	credit_commitments1 = 0 if applicant_one.get("Outgoings", {}).get("Credit Commitments") in null else applicant_one.get("Outgoings", {}).get("Credit Commitments")
	credit_commitments2 = 0 if applicant_two.get("Outgoings", {}).get("Credit Commitments") in null else applicant_one.get("Outgoings", {}).get("Credit Commitments")

	property_type = data["Property Details"].get("Property Type")
	property_age = data["Property Details"].get("Property Age", 0)

	expenses = data["Client Details"][0].get("Outgoings", [])
	groceries = expenses.get("Living Costs", {}).get("Groceries", 0)
	council_tax = expenses.get("Household", {}).get("Council Tax", 0)
	transport = 0 if expenses.get("Transport") in null else expenses.get("Transport", 0)

	service = Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	driver.get("https://online.newcastle.co.uk/MortgageAffordabilityCalculator/AffordabilityCalculator.aspx?AspxAutoDetectCookieSupport=1")
	try:
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#onetrust-close-btn-container button").click()
	except:
		pass

	try:
		purchase_or_remortgage = "1" if Loan_Type == "Purchase" else "2"
		equity_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#LoanType"))
		equity_dropdown.select_by_value(purchase_or_remortgage)

		if mortgage_type == "Standard Residential":
		    HTB_equity = "4"
		elif mortgage_type == "Shared Ownership":
		    HTB_equity = "5"
		elif mortgage_type == "Shared Equity / Help To Buy":
		    if location == "London":
		        HTB_equity = "3"
		    else:
		        HTB_equity = "2"
		else:
		    HTB_equity = "1"

		equity_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#HelpToBuyEquity"))
		equity_dropdown.select_by_value(HTB_equity)

		if HTB_equity == "2" or HTB_equity == "3":
			driver.find_element(By.CSS_SELECTOR, "#HelpToBuyAmount").send_keys(str(Purchase_Price-loan_amount))

		driver.find_element(By.CSS_SELECTOR, "#LoanAmt").send_keys(str(loan_amount))

		if location == "Scotland":
		    region = "S"
		elif location == "Wales":
		    region = "W"
		elif location == "Northern Ireland":
		    region = "NW"
		elif location == "England":
		    region = "L"
		else:
		    region = "EA"

		region_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#propRegion"))
		region_dropdown.select_by_value(region)

		driver.find_element(By.CSS_SELECTOR, "#PropValue").send_keys(str(Purchase_Price))
		years_fixed_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#LongTermFixedRate"))
		years_fixed_dropdown.select_by_value("true")
		driver.find_element(By.CSS_SELECTOR, "#Term").send_keys(str(Loan_Term))

		if Payment_Method == "Repayment":
		    repay = "1"
		elif Payment_Method == "Interest Only":
		    repay = "2"
		else:
		    repay = "3"

		repay_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#RepaymentBasis"))
		repay_dropdown.select_by_value(repay)

		if repay == "3":
			driver.find_element(By.CSS_SELECTOR, "#InterestOnlyAmount").send_keys(str(Purchase_Price-loan_amount))

		driver.find_element(By.CSS_SELECTOR, "#stepno0Next").click()

	except Exception as e:
		print(e)

	time.sleep(1)
	try:
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#noofapplicants2").click()

		if applicant_one_empstatus == "Employed":
		    status_1 = "1"
		elif applicant_one_empstatus == "Retired":
		    status_1 = "6"
		elif applicant_one_empstatus == "Self Employed (Sole Trader/Partnership)":
		    status_1 = "2"
		elif applicant_one_empstatus == "Self Employed (Ltd Company/Director)":
		    status_1 = "3"
		elif applicant_one_empstatus == "Not Working":
		    status_1 = "4"
		else:
		    status_1 = "5"

		emp_status_1 = Select(driver.find_element(By.CSS_SELECTOR, "#App1_Status"))
		emp_status_1.select_by_value(status_1)

		driver.find_element(By.CSS_SELECTOR, "#App1_Income").send_keys(str(basic_annual_income1))
		if num_of_applicants>1:
		    if applicant_two_empstatus == "Employed":
		        status_2 = "1"
		    elif applicant_two_empstatus == "Retired":
		        status_2 = "6"
		    elif applicant_two_empstatus == "Self Employed (Sole Trader/Partnership)":
		        status_2 = "2"
		    elif applicant_two_empstatus == "Self Employed (Ltd Company/Director)":
		        status_2 = "3"
		    elif applicant_two_empstatus == "Not Working":
		        status_2 = "4"
		    else:
		        status_2 = "5"

		    emp_status_2 = Select(driver.find_element(By.CSS_SELECTOR, "#App2_Status"))
		    emp_status_2.select_by_value(status_2)

		    driver.find_element(By.CSS_SELECTOR, "#App2_Income").send_keys(str(basic_annual_income2))

		driver.find_element(By.CSS_SELECTOR, "#stepno1Next").click()
	except Exception as e:
		print(e)

	time.sleep(1)
	driver.find_element(By.CSS_SELECTOR, "#stepno2Next").click()

	time.sleep(1)
	try:
		if rent_1>0:
			driver.find_element(By.CSS_SELECTOR, "#App1_C_G1_7").send_keys(str(rent_1))
		if credit_commitments1>0:
			driver.find_element(By.CSS_SELECTOR, "#App1_C_G2_9").send_keys(str(credit_commitments1))
		if num_of_applicants>1:
		    if rent_2>0:
		        driver.find_element(By.CSS_SELECTOR, "#App2_C_G1_7").send_keys(str(rent_2))
		    if credit_commitments2>0:
		        driver.find_element(By.CSS_SELECTOR, "#App2_C_G2_9").send_keys(str(credit_commitments2))

		driver.find_element(By.CSS_SELECTOR, "#stepno3Next").click()
	except Exception as e:
		print(e)

	time.sleep(1)
	try:
		driver.find_element(By.CSS_SELECTOR, "#NumberOfChildrenUnderThreshold").send_keys("0")
		benifit = Select(driver.find_element(By.CSS_SELECTOR, "#ChildBenefitReceived"))
		benifit.select_by_value("N")
		driver.find_element(By.CSS_SELECTOR, "#FinancialDependantsOverThreshold").send_keys(str(num_of_dependants))
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_1").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_2").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_3").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_4").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_5").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_6").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_7").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_8").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_10").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_11").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#Outgoings_12").send_keys("0")

		driver.find_element(By.CSS_SELECTOR, "#linkButton").click()
	except Exception as e:
		print(e)

	time.sleep(3)
	max_affordable = [x.text for x in driver.find_elements(By.CSS_SELECTOR, "#pnMaxLendingEqual .answerConfirmation") if x.text]
	max_affordable += [x.text for x in driver.find_elements(By.CSS_SELECTOR, "#pnMaxLendingNotEqual .answerConfirmation") if x.text]

	print("Max Affordable : ", max_affordable)
	driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)
# main()