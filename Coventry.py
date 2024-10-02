from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
import time
import json

def main(config_file):
	with open(config_file) as file:
		data = json.load(file)
	# with open('config_seven.json') as file:
	# 	data = json.load(file)
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

	date_of_birth_1 = applicant_one.get("Date of Birth").split("/")
	date_1, month_1, year_1 = date_of_birth_1
	date_of_birth_2 = applicant_two.get("Date of Birth", "01/01/1990").split("/")
	date_2, month_2, year_2 = date_of_birth_2
	title_1 = applicant_one.get("Title", "Mr")
	title_2 = applicant_two.get("Title", "Mr")
	retirement_age_1 = applicant_one.get("expected retirement age", 70)
	retirement_age_2 = applicant_two.get("expected retirement age", 70)

	self_income_last_year_1 = applicant_one.get("Employment Details", {}).get("Last Year's Salary", 0)
	self_income_previous_year_1 = applicant_one.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	net_profit_1 = applicant_one.get("Employment Details", {}).get("Last Year's Net Profits", 0)
	dividend_1 = applicant_one.get("Employment Details", {}).get("Last Year's Dividends", 0)
	self_income_last_year_2 = applicant_two.get("Employment Details", {}).get("Last Year's Salary", 0)
	self_income_previous_year_2 = applicant_two.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	net_profit_2 = applicant_two.get("Employment Details", {}).get("Last Year's Net Profits", 0)
	dividend_2 = applicant_two.get("Employment Details", {}).get("Last Year's Dividends", 0)

	location = data["Property Details"].get("Property Location")
	post_code =data["Property Details"].get("Property Details", {}).get("Post Code")

	household_expenses_1 = applicant_one.get("Outgoings", {}).get("Household")
	rent_1 = household_expenses_1.get("Mortgage / Rent")
	serviceCharge_1 = household_expenses_1.get("Service Charge", 0)
	household_expenses_2 = applicant_two.get("Outgoings", {}).get("Household", {})
	rent_2 = 0
	credit_commitments1 = 0 if applicant_one.get("Outgoings", {}).get("Credit Commitments") in null else applicant_one.get("Outgoings", {}).get("Credit Commitments")
	credit_commitments2 = 0 if applicant_two.get("Outgoings", {}).get("Credit Commitments") in null else applicant_one.get("Outgoings", {}).get("Credit Commitments")

	property_type = data["Property Details"].get("Property Type")
	property_age = data["Property Details"].get("Property Age", 0)

	expenses = data["Client Details"][0].get("Outgoings", [])
	groceries = expenses.get("Living Costs", {}).get("Groceries", 0)
	council_tax = expenses.get("Household", {}).get("Council Tax", 0)
	transport = 0 if expenses.get("Transport") in null else expenses.get("Transport", 0)

	service= Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	driver.get("https://www.coventrybuildingsociety.co.uk/Calculators/AffordabilityCalculator.aspx")

	try:
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_421").send_keys(str(Purchase_Price))
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_422").send_keys(str(post_code))
		applicant_number = "2" if num_of_applicants>2 else str(num_of_applicants)
		applicant_number_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_DDL_423"))
		applicant_number_dropdown.select_by_value(applicant_number)
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_424").send_keys(str(num_of_applicants))
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_425").send_keys(str(num_of_dependants))
		council_tax_benifit_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_DDL_426"))
		council_tax_benifit_dropdown.select_by_value("false")

		purchase_or_remortgage = "NEW" if Loan_Type == "Purchase" else "RMTG"
		type_of_loan = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_DDL_430"))
		type_of_loan.select_by_value(purchase_or_remortgage)
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_431").send_keys(str(loan_amount))
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_432").send_keys(str(Loan_Term))
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_433").send_keys(str(loan_term_months))

		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_AppDets1_TB_428_DAY").send_keys(date_1)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_AppDets1_TB_428_MONTH").send_keys(month_1)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_AppDets1_TB_428_YEAR").send_keys(year_1)
		male_or_female_1 = "M" if title_1 == "Mr" or title_1 == "Mister" or title_1 == "Mr." else "F"
		male_or_female_1_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_AppDets1_DDL_429"))
		male_or_female_1_dropdown.select_by_value(male_or_female_1)
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_AppDets2_TB_428_DAY").send_keys(date_2)
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_AppDets2_TB_428_MONTH").send_keys(month_2)
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_AppDets2_TB_428_YEAR").send_keys(year_2)
			male_or_female_2 = "M" if title_2 == "Mr" or title_2 == "Mister" or title_2 == "Mr." else "F"
			male_or_female_2_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_AppDets2_DDL_429"))
			male_or_female_2_dropdown.select_by_value(male_or_female_2)

		driver.find_element(By.CSS_SELECTOR, "#ContBtn").click()
	except Exception as e:
		print(e)

	time.sleep(1)

	try:
		if applicant_one_empstatus == "Employed":
			emptype_1 = "1"
		elif applicant_one_empstatus == "Self Employed (Sole Trader/Partnership)" or applicant_one_empstatus == "Self Employed (Ltd Company/Director)":
			emptype_1 = "2"
		elif applicant_one_empstatus == "Retired":
			emptype_1 = "3"
		elif applicant_one_empstatus == "Not Working":
			emptype_1 = "4"
		else:
			emptype_1 = "5"

		emptype_1_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_DDL_434"))
		emptype_1_dropdown.select_by_value(emptype_1)
		time.sleep(2)
		if emptype_1 == "1":
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_TB_436").send_keys(str(basic_annual_income1))
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_TB_439").send_keys(str(bonus1))
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_TB_440").send_keys(str(overtime1))
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_TB_445").send_keys(str(retirement_age_1))
			if num_of_applicants>1:
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_TB_446").send_keys("0")
		if emptype_1 == "2":
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_TB_443").send_keys(str(net_profit_1))
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_TB_445").send_keys(str(retirement_age_1))
			if num_of_applicants>1:
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc1_TB_446").send_keys("0")
		else:
			pass

		if num_of_applicants>1:
			if applicant_two_empstatus == "Employed":
				emptype_2 = "1"
			elif applicant_two_empstatus == "Self Employed (Sole Trader/Partnership)" or applicant_two_empstatus == "Self Employed (Ltd Company/Director)":
				emptype_2 = "2"
			elif applicant_two_empstatus == "Retired":
				emptype_2 = "3"
			elif applicant_two_empstatus == "Not Working":
				emptype_2 = "4"
			else:
				emptype_2 = "5"

			emptype_2_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_DDL_434"))
			emptype_2_dropdown.select_by_value(emptype_2)
			time.sleep(2)
			if emptype_2 == "1":
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_TB_436").send_keys(str(basic_annual_income2))
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_TB_439").send_keys(str(bonus2))
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_TB_440").send_keys(str(overtime2))
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_TB_445").send_keys(str(retirement_age_2))
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_TB_446").send_keys("0")
			if emptype_2 == "2":
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_TB_443").send_keys(str(net_profit_2))
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_TB_445").send_keys(str(retirement_age_2))
				driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_EmpInc2_TB_446").send_keys("1")
			else:
				pass

		driver.find_element(By.CSS_SELECTOR, "#ContBtn").click()
	except Exception as e:
		print(e)

	time.sleep(1)
	try:
		if credit_commitments1>0:
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_502_1").clear()
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_502_1").send_keys(str(credit_commitments1))
		if credit_commitments2>0:
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_502_2").clear()
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_502_2").send_keys(str(credit_commitments2))
		if credit_commitments1+credit_commitments2>0:
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_502_3").clear()
			driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_TB_502_2").send_keys(str(credit_commitments1+credit_commitments2))

		driver.find_element(By.CSS_SELECTOR, "#ContBtn").click()
	except Exception as e:
		print(e)

	time.sleep(1)
	try:
		max_affordable = driver.find_element(By.CSS_SELECTOR, "#MainContent_AffordabilityCalculator1_MaxLoanAmtLbl").text
		print("Max Affordable : ", max_affordable)
	except Exception as e:
		print(e)
	driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)

