from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import re
import time
import json
import requests

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

	household_expenses = sum(int(value) for value in applicant_one.get("Outgoings", {}).get("Household").values())
	energy = applicant_one.get("Outgoings", {}).get("Household", {}).get("Electricity", 0)
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
	driver.get("https://www.chorleybs.co.uk/intermediary/")
	time.sleep(1)
	try:
		driver.find_element(By.CSS_SELECTOR, "#cookie_action_close_header_reject").click()
	except:
		pass
	time.sleep(1)
	driver.find_element(By.CSS_SELECTOR, 'a input[value="Calculators"]').click()
	time.sleep(1)
	driver.find_element(By.CSS_SELECTOR, ".button.pink-outline.mortgage-calculator-button.affordability").click()
	time.sleep(1)

	try:
		driver.find_element(By.CSS_SELECTOR, "#inpPropertyPurchasePrice").send_keys(str(Purchase_Price))
		driver.find_element(By.CSS_SELECTOR, "#inpMortgageAmount").send_keys(str(loan_amount))
		term_selected = driver.find_element(By.CSS_SELECTOR, "#customRange1")
		driver.execute_script("arguments[0].value = arguments[1]; arguments[0].dispatchEvent(new Event('input', { bubbles: true }))", term_selected, str(Loan_Term))
		# term_selected.send_keys(str(Loan_Term))
		# term_selected.click()
		repay = "c" if Payment_Method=="Repayment" else "i"
		repayment_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#inpRepaymentType"))
		repayment_dropdown.select_by_value(repay)
		applicant_number_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#inpNumberOfApplicants"))
		applicant_number_dropdown.select_by_value(str(num_of_applicants))

		if property_type=="House":
			proptype = "detached"
		elif property_type=="Flat":
			proptype = "flat"
		else:
			proptype = "bungalow"
		prop = Select(driver.find_element(By.CSS_SELECTOR, "#inpPropertyType"))
		prop.select_by_value(proptype)
	except Exception as e:
		print(e)

	try:
		driver.find_element(By.CSS_SELECTOR, "#inpNetIncomeA1").send_keys(str(net_income1))
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#inpNetIncomeA2").send_keys(str(net_income2))

		driver.find_element(By.CSS_SELECTOR, "#inpGrossIncomeA1").send_keys(str(basic_annual_income1))
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#inpGrossIncomeA2").send_keys(str(basic_annual_income2))
	except Exception as e:
		print(e)

	try:
		driver.find_element(By.CSS_SELECTOR, "#formInput_expenditureA1").send_keys(str(household_expenses))
		driver.find_element(By.CSS_SELECTOR, "#formInput_creditCommitments").send_keys(str(credit_commitments1))
		driver.find_element(By.CSS_SELECTOR, "#formInput_energyCosts").send_keys(str(energy))

		adults = Select(driver.find_element(By.CSS_SELECTOR, "#inpWorkingAdult"))
		adults.select_by_value(str(num_of_applicants))
		retired = Select(driver.find_element(By.CSS_SELECTOR, "#inpRetiredAdult"))
		retired.select_by_value("0")
		children = Select(driver.find_element(By.CSS_SELECTOR, "#inpChildren"))
		children.select_by_value(str(num_of_dependants))

		driver.find_element(By.CSS_SELECTOR, 'input[value="Calculate"]').click()
	except Exception as e:
		print(e)

	time.sleep(1)
	pattern = r"£(\d+(?:,\d{3})*(?:\.\d{2})?)"
	result_text = driver.find_element(By.CSS_SELECTOR, ".sO.sStmt").text
	max_affordable = re.findall(pattern, result_text)
	print(max_affordable)

	driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
    main(config_file)