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

	if Payment_Method == "Interest Only" and loan_amount<250000:
		print("Max Affordable: 0")
		print("'Interest only' Payment Method requires a minimum gross amount of 250000")
	else:
		service = Service(executable_path="chromedriver.exe")
		driver = webdriver.Chrome(service=service)
		driver.get("https://www.santanderforintermediaries.co.uk/calculators-and-forms/affordability/")
		try:
			driver.find_element(By.CSS_SELECTOR, ".btn-cookie-settings.btn-cookie-settings_alt.btn-cookie-settings_accept").click()
		except:
			pass

		time.sleep(2)
		mortgage_details = WebDriverWait(driver, 30).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "#pnlApplicationType"))
		)		
		driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", mortgage_details)

		time.sleep(2)
		try:
			if num_of_applicants>1:
				driver.find_element(By.CSS_SELECTOR, '[for="rbApplicationTypeJoint"]').click()
			else:
				driver.find_element(By.CSS_SELECTOR, '[for="rbApplicationTypeSingle"]').click()

			driver.find_element(By.CSS_SELECTOR, "#tbFinancialDependents").send_keys(str(num_of_dependants))
		except Exception as e:
			print(f"You have this problem : ",e)

		purchase_details = WebDriverWait(driver, 30).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "#rbMortgageTypePurchase"))
			)
		driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", purchase_details)
		time.sleep(2)
		try:
			if Loan_Type=="Purchase":
				driver.find_element(By.CSS_SELECTOR, '[for="rbMortgageTypePurchase"]').click()
			else:
				driver.find_element(By.CSS_SELECTOR, '[for="rbMortgageTypeRemortgage"]').click()

			if Loan_Type=="Purchase":
				driver.find_element(By.CSS_SELECTOR, "#tbDeposit").send_keys(str(Purchase_Price-loan_amount))
				driver.find_element(By.CSS_SELECTOR, '[for="rbExistingSantanderCustomersNo"]').click()
			else:
				driver.find_element(By.CSS_SELECTOR, "#tbEstimatedPropertyValue").send_keys(str(Purchase_Price))
				driver.find_element(By.CSS_SELECTOR, "#tbMonthlyRent").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, '[for="rbAllBorrowersSameYes"]').click()

			pay_dropdown = WebDriverWait(driver, 30).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, "#ddlMethodRepaymentSelectBoxIt")
				))
			driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", pay_dropdown)
			pay_dropdown.click()
			if Payment_Method == "Repayment":
				driver.find_element(By.CSS_SELECTOR, '[data-val="Capital and interest"]').click()
			elif Payment_Method == "Interest Only":
				driver.find_element(By.CSS_SELECTOR, '[data-val="Interest only - sale of mortgaged property"]').click()
			else:
				driver.find_element(By.CSS_SELECTOR, '[data-val="Part and part - sale of mortgaged property"]').click()

			driver.find_element(By.CSS_SELECTOR, "#tbLoanTermYears").send_keys(str(Loan_Term))
			driver.find_element(By.CSS_SELECTOR, "#tbLoanTermMonths").send_keys(str(loan_term_months))

			continue_button = WebDriverWait(driver,30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#btnContinue")))
			driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center'});", continue_button)
			driver.find_element(By.CSS_SELECTOR, '[for="rbOtherPropertiesNo"]').click()

			continue_button.click()
		except Exception as e:
			print(f"You have this problem : ",e)

		time.sleep(2)
		try:
			salary_1 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tbPermanentEmploymentBasicSalary1")))
			salary_1.send_keys(str(basic_annual_income1))
			if num_of_applicants>1:
				salary_2 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#tbPermanentEmploymentBasicSalary2")))
				driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center'});", salary_2)
				salary_2.send_keys(str(basic_annual_income2))

			time.sleep(1)
			calculate_net = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#btnNetIncomeCalculate")))
			driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center'});", calculate_net)
			calculate_net.click()

			time.sleep(2)

			continue_button_of_page_2 = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#btnContinue")))
			driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center'});", continue_button_of_page_2)
			continue_button_of_page_2.click()
		except Exception as e:
			print(f"You have this problem : ",e)

		time.sleep(2)
		try:
			if credit_commitments1:
				driver.find_element(By.CSS_SELECTOR, "#tbCreditCommitmentsMonthlySum").send_keys(str(credit_commitments1))

			no_extra_monthly_expnditure = WebDriverWait(driver, 30).until(
				EC.presence_of_element_located((By.CSS_SELECTOR, '[for="rbNonRegularMonthlyExpenditureNo"]'))
				)
			driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center'});", no_extra_monthly_expnditure)
			no_extra_monthly_expnditure.click()
			driver.find_element(By.CSS_SELECTOR, "#btnContinue").click()
		except Exception as e:
			print(f"You have this problem : ",e)

		time.sleep(2)
		try:
			results_msgs = driver.find_element(By.CLASS_NAME, "resultsMsgs")
			elements = results_msgs.find_elements(By.XPATH, ".//strong/span")
			first_value = elements[0].text if elements else None
			second_value = elements[1].text if len(elements) >= 2 else None
			print("Max Affordable: ",first_value)
			print("Max Affordable for 5 Year fixed rate : ", second_value)
		except:
			print("No Affordable element found")

		driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)
# config_file = 'config_one.json'
# main(config_file)