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

	self_income_last_year_1 = applicant_one.get("Employment Details", {}).get("Last Year's Salary", 0)
	self_income_previous_year_1 = applicant_one.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	net_profit_1 = applicant_one.get("Employment Details", {}).get("Last Year's Net Profits", 0)
	dividend_1 = applicant_one.get("Employment Details", {}).get("Last Year's Dividends", 0)
	self_income_last_year_2 = applicant_two.get("Employment Details", {}).get("Last Year's Salary", 0)
	self_income_previous_year_2 = applicant_two.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	net_profit_2 = applicant_two.get("Employment Details", {}).get("Last Year's Net Profits", 0)
	dividend_2 = applicant_two.get("Employment Details", {}).get("Last Year's Dividends", 0)

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

	service= Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	driver.get("https://intermediaries.hrbs.co.uk/resources/calculators/residential-calculator/")

	try:
		driver.find_element(By.CSS_SELECTOR, "#mortgage-required").send_keys(str(loan_amount))
		driver.find_element(By.CSS_SELECTOR, "#property-value").send_keys(str(Purchase_Price))
		debt = Select(driver.find_element(By.CSS_SELECTOR, "#debt-consolidation"))
		debt.select_by_value("no")
		driver.find_element(By.CSS_SELECTOR, "#mortgage-term-years").send_keys(str(Loan_Term))

		if Payment_Method == "Repayment":
			repay = "capital"
		elif Payment_Method == "Interest Only":
			repay = "interest"
		else:
			repay = "partnpart"

		repayment = Select(driver.find_element(By.CSS_SELECTOR, "#repayment-type"))
		repayment.select_by_value(str(repay))
		if repay == "partnpart":
			driver.find_element(By.CSS_SELECTOR, "#capital-repayment-amount").send_keys(str(Purchase_Price - loan_amount))

		prod_term = "fixed" if Product_Term == 60 else "other"
		five_year_fixed = Select(driver.find_element(By.CSS_SELECTOR, "#product-length"))
		five_year_fixed.select_by_value(str(prod_term))

		if prod_term == "fixed":
			driver.find_element(By.CSS_SELECTOR, "#interest-rate").send_keys("1")

		driver.find_element(By.CSS_SELECTOR, '[data-step="step-2"]').click()

	except Exception as e:
		print(e)

	try:
		if location == "Northern Ireland":
			prop_loc = "NE"
		elif location == "England":
			prop_loc = "E"
		elif location == "Wales":
			prop_loc = "WA"
		else:
			prop_loc = "NW"

		property_place =Select(driver.find_element(By.CSS_SELECTOR, "#property-region"))
		property_place.select_by_value(prop_loc)

		if num_of_applicants==1:
			if num_of_dependants==1:
				applicants_with_dependants = "1A1C"
			elif num_of_dependants==2:
				applicants_with_dependants = "1A2C"
			else:
				applicants_with_dependants = "1A"
		elif num_of_applicants==2:
			if num_of_dependants==1:
				applicants_with_dependants = "2A1C"
			elif num_of_dependants==2:
				applicants_with_dependants = "2A2C"
			elif num_of_dependants==3:
				applicants_with_dependants = "2A2C"
			else:
				applicants_with_dependants = "2A"
		else:
			if num_of_dependants==0:
				applicants_with_dependants = "3ANC"
			else:
				applicants_with_dependants = "3AWC"

		a_w_c =Select(driver.find_element(By.CSS_SELECTOR, "#household-occupancy-composition"))
		a_w_c.select_by_value(applicants_with_dependants)

		tax_data = "yes" if council_tax>0 else "no"
		tax = Select(driver.find_element(By.CSS_SELECTOR, "#res-council-tax-reduction"))
		tax.select_by_value(tax_data)

		driver.find_element(By.CSS_SELECTOR, '[data-step="step-3"]').click()

	except Exception as e:
		print(e)

	try:
		driver.find_element(By.CSS_SELECTOR, '[name="app1_Salary"]').send_keys(str(basic_annual_income1))
		driver.find_element(By.CSS_SELECTOR, '[name="app1_Allowance"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="app1_OthEmpAcceptable"]').send_keys(str(self_income_last_year_1))
		driver.find_element(By.CSS_SELECTOR, '[name="app1_SoleTrader"]').send_keys(str(net_profit_1))
		driver.find_element(By.CSS_SELECTOR, '[name="app1_LTDSalary"]').send_keys(str(self_income_last_year_1))
		driver.find_element(By.CSS_SELECTOR, '[name="app1_LTDDividend"]').send_keys(str(dividend_1))
		driver.find_element(By.CSS_SELECTOR, '[name="app1_Pension"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="app1_OtherIncome"]').send_keys("0")

		driver.find_element(By.CSS_SELECTOR, '[name="loans"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="overdraft"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="childcare"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="other-mortgages"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="student-loans"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="pension-contributions"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="residential-property-costs"]').send_keys("0")

		if num_of_applicants>1:
			driver.find_element(By.ID, "add-applicant").click()
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, '[name="app1_Salary-2"]').send_keys(str(basic_annual_income2))
			driver.find_element(By.CSS_SELECTOR, '[name="app1_Allowance-2"]').send_keys("0")
			driver.find_element(By.CSS_SELECTOR, '[name="app1_OthEmpAcceptable-2"]').send_keys(str(self_income_last_year_2))
			driver.find_element(By.CSS_SELECTOR, '[name="app1_SoleTrader-2"]').send_keys(str(net_profit_2))
			driver.find_element(By.CSS_SELECTOR, '[name="app1_LTDSalary-2"]').send_keys(str(self_income_last_year_2))
			driver.find_element(By.CSS_SELECTOR, '[name="app1_LTDDividend-2"]').send_keys(str(dividend_2))
			driver.find_element(By.CSS_SELECTOR, '[name="app1_Pension-2"]').send_keys("0")
			driver.find_element(By.CSS_SELECTOR, '[name="app1_OtherIncome-2"]').send_keys("0")

			driver.find_element(By.CSS_SELECTOR, '[name="loans-2"]').send_keys("0")
			driver.find_element(By.CSS_SELECTOR, '[name="overdraft-2"]').send_keys("0")
			driver.find_element(By.CSS_SELECTOR, '[name="childcare-2"]').send_keys("0")
			driver.find_element(By.CSS_SELECTOR, '[name="other-mortgages-2"]').send_keys("0")
			driver.find_element(By.CSS_SELECTOR, '[name="student-loans-2"]').send_keys("0")
			driver.find_element(By.CSS_SELECTOR, '[name="pension-contributions-2"]').send_keys("0")
			driver.find_element(By.CSS_SELECTOR, '[name="residential-property-costs-2"]').send_keys("0")

		driver.find_element(By.CSS_SELECTOR, "#calculate-affordability").click()
	except Exception as e:
		print(e)

	try:
		max_affordable = driver.find_element(By.CSS_SELECTOR, '#output-box input.form-control').get_attribute('value')
		print("Max Affordable : ", max_affordable)
	except:
		pass

	driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)
