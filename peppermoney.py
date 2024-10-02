from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
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
	rent_1 = household_expenses_1.get("Mortgage / Rent", 0)
	serviceCharge_1 = household_expenses_1.get("Service Charge", 0)
	household_expenses_2 = applicant_two.get("Outgoings", {}).get("Household", {})
	rent_2 = household_expenses_2.get("Mortgage / Rent", 0)
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
	driver.get("https://www.pepper.money/broker/mortgage-calculators/residential-mortgage-calculator/")
	try:
		driver.find_element(By.CSS_SELECTOR, "#CybotCookiebotDialogBodyButtonDecline").click()
	except:
		pass

	try:
		applicants_location = driver.find_element(By.CSS_SELECTOR, "#form-wizard-final-results")
		driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", applicants_location)
		time.sleep(1)
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#number-applicant-label-two").click()

		if num_of_dependants==1:
			driver.find_element(By.CSS_SELECTOR, '[for="one-dependent"]').click()
		elif num_of_dependants==2:
			driver.find_element(By.CSS_SELECTOR, '[for="two-dependents"]').click()
		elif num_of_dependants>=3:
			driver.find_element(By.CSS_SELECTOR, '[for="three-dependents"]').click()
		else:
			pass

		purchase_or_mortgage = "purchase" if Loan_Type == "Purchase" else "remortgage"
		purchase_or_mortgage_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#purchase-remortgage"))
		purchase_or_mortgage_dropdown.select_by_value(purchase_or_mortgage)

		if Loan_Type == "Purchase":
			driver.find_element(By.CSS_SELECTOR, "#purchase-price").send_keys(str(Purchase_Price))
			driver.find_element(By.CSS_SELECTOR, "#deposit-amount").send_keys(str(Purchase_Price - loan_amount))
		else:
			driver.find_element(By.CSS_SELECTOR, "#estimated-property-value").send_keys(str(Purchase_Price))
			driver.find_element(By.CSS_SELECTOR, "#outstanding-mortgage-balance").send_keys(str(loan_amount))
		product_choice = Select(driver.find_element(By.CSS_SELECTOR, "#product-choice"))
		product_choice.select_by_value("unknown")
		repay = "capital-repayment" if int((loan_amount/Purchase_Price)*100)>60 else "interest-only"
		repayment_choice = Select(driver.find_element(By.CSS_SELECTOR, "#repayment-type-choice"))
		repayment_choice.select_by_value(repay)
		term_input = driver.find_element(By.ID, "term-input")
		driver.execute_script(f"arguments[0].value = {Loan_Term};", term_input)
		driver.execute_script("arguments[0].oninput();", term_input)

		continue_button_1 = driver.find_element(By.CSS_SELECTOR, "#page-one-continue")
		driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", continue_button_1)
		time.sleep(1)
		continue_button_1.click()
	except Exception as e:
		print(e)

	try:
		if applicant_one_empstatus == "Employed":
			emp_stat_1 = "employed"
		else:
			emp_stat_1 = "sole-trader-partnership"
		employment_1 = Select(driver.find_element(By.CSS_SELECTOR, "#income-type-applicant-one"))
		employment_1.select_by_value(emp_stat_1)
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#basic-employed-salary-applicant-one").send_keys(str(basic_annual_income1))
		if overtime1:
			driver.find_element(By.CSS_SELECTOR, "#overtime-income").clear()
			driver.find_element(By.CSS_SELECTOR, "#overtime-income").send_keys(str(overtime1))
		if bonus1:
			driver.find_element(By.CSS_SELECTOR, "#bonus-income").clear()
			driver.find_element(By.CSS_SELECTOR, "#bonus-income").send_keys(str(bonus1))

		driver.find_element(By.CSS_SELECTOR, "#gross-monthly-income-value").location_once_scrolled_into_view
		# gross_income_1 = driver.find_element(By.CSS_SELECTOR, "#gross-monthly-income-value").location_once_scrolled_into_view
		# if not gross_income_1.is_displayed():
		# 	gross_income_1.location_once_scrolled_into_view
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#page-two-continue").click()
		else:
			driver.find_element(By.CSS_SELECTOR, "#initial-calculate-btn-one button").click()
		
		time.sleep(1)
		if num_of_applicants>1:
			if applicant_two_empstatus == "Employed":
				emp_stat_2 = "employed"
			else:
				emp_stat_2 = "sole-trader-partnership"
			employment_2 = Select(driver.find_element(By.CSS_SELECTOR, "#income-type-applicant-two"))
			employment_2.select_by_value(emp_stat_2)
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#basic-employed-salary-applicant-two").send_keys(str(basic_annual_income2))
			if overtime2:
				driver.find_element(By.CSS_SELECTOR, "#overtime-income").clear()
				driver.find_element(By.CSS_SELECTOR, "#overtime-income").send_keys(str(overtime2))
			if bonus2:
				driver.find_element(By.CSS_SELECTOR, "#bonus-income").clear()
				driver.find_element(By.CSS_SELECTOR, "#bonus-income").send_keys(str(bonus2))

			driver.find_element(By.CSS_SELECTOR, "#gross-annual-income-value-applicant-two").location_once_scrolled_into_view
			driver.find_element(By.CSS_SELECTOR, "#page-three-continue").click()
	except Exception as e:
		print(e)

	try:
		driver.find_element(By.CSS_SELECTOR, "#credit-cards-applicant-one-value").clear()
		driver.find_element(By.CSS_SELECTOR, "#credit-cards-applicant-one-value").send_keys(credit_commitments1)
		driver.find_element(By.CSS_SELECTOR, "#total-monthly-commitments-applicant-one-value").location_once_scrolled_into_view

		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#page-five-continue").click()
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#credit-cards-applicant-two-value").clear()
			driver.find_element(By.CSS_SELECTOR, "#credit-cards-applicant-two-value").send_keys(credit_commitments2)

			driver.find_element(By.CSS_SELECTOR, "#total-monthly-commitments-applicant-two-value").location_once_scrolled_into_view
			driver.find_element(By.CSS_SELECTOR, "#page-six-continue").click()
		else:
			driver.find_element(By.CSS_SELECTOR, "#continue-to-expenditure button").click()
	except Exception as e:
		print(e)

	try:
		driver.find_element(By.CSS_SELECTOR, "#housekeeping-value").send_keys(household_expenses_1)
		driver.find_element(By.CSS_SELECTOR, "#ground-rent-value").send_keys(rent_1)
		driver.find_element(By.CSS_SELECTOR, "#basic-recreation-value").location_once_scrolled_into_view

		driver.find_element(By.CSS_SELECTOR, "#resiSubmit").click()
	except Exception as e:
		print(e)
	time.sleep(1)
	try:
		year_2_fixed = driver.find_element(By.CSS_SELECTOR, "#two-year-four-five-final-result").text
		print("2 year Affordable : ", year_2_fixed)

		year_5_fixed = driver.find_element(By.CSS_SELECTOR, "#five-year-four-five-final-result").text
		print("5 year Affordable : ", year_5_fixed)
	except Exception as e:
		print(e)

	driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)