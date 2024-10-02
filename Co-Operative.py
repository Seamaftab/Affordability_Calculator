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
	# with open('config_three.json') as file:
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

	service = Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	driver.get("https://www.intermediary.co-operativebank.co.uk/help-and-calculators/calculators/affordability-calculator/")
	try:
		driver.find_element(By.CSS_SELECTOR, "#advanced_consent_options").click()
		time.sleep(1)
		cat1_button = driver.find_element(By.ID, "toggle_cat1")
		driver.execute_script("arguments[0].click();", cat1_button)
		cat2_button = driver.find_element(By.ID, "toggle_cat2")
		driver.execute_script("arguments[0].click();", cat2_button)
		cat3_button = driver.find_element(By.ID, "toggle_cat3")
		driver.execute_script("arguments[0].click();", cat3_button)
		driver.find_element(By.CSS_SELECTOR, "#preferences_prompt_submit").click()
	except:
		pass

	try:
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#affordability-joint-applicant-Yes").click()
		else:
			driver.find_element(By.CSS_SELECTOR, "#affordability-joint-applicant-No").click()

		driver.find_element(By.CSS_SELECTOR, "#affordability-date1-day").send_keys(str(date_1))
		driver.find_element(By.CSS_SELECTOR, "#affordability-date1-month").send_keys(str(month_1))
		driver.find_element(By.CSS_SELECTOR, "#affordability-date1-year").send_keys(str(year_1))
		emp_stat_1 = driver.find_element(By.CSS_SELECTOR, "#affordability-employment1")
		driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", emp_stat_1)
		time.sleep(1)
		emp_stat_1.click()
		if applicant_one_empstatus == "Employed":
			driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="affordability-employment1"] li[data-value="Employed"]').click()
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#affordability-main-income1").send_keys(str(basic_annual_income1))
			driver.find_element(By.CSS_SELECTOR, "#affordability-bonus-income1").send_keys(str(bonus1))
		elif applicant_one_empstatus == "Self Employed (Sole Trader/Partnership)" or applicant_one_empstatus=="Self Employed (Ltd Company/Director)":
			driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="affordability-employment1"] li[data-value="Self Employed"]').click()
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#affordability-last-year-income1").send_keys(str(self_income_last_year_1))
			driver.find_element(By.CSS_SELECTOR, "#affordability-previous-year-income1").send_keys(str(self_income_previous_year_1))
		elif applicant_one_empstatus == "Retired":
			driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="affordability-employment1"] li[data-value="Retired"]').click()
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#affordability-main-income1").send_keys(str(basic_annual_income1))
			driver.find_element(By.CSS_SELECTOR, "#affordability-bonus-income1").send_keys(str(bonus1))
		else:
			driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="affordability-employment1"] li[data-value="Unemployed"]').click()
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#affordability-main-income1").send_keys(str(basic_annual_income1))
			driver.find_element(By.CSS_SELECTOR, "#affordability-bonus-income1").send_keys(str(bonus1))

		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#affordability-date2-day").send_keys(str(date_2))
			driver.find_element(By.CSS_SELECTOR, "#affordability-date2-month").send_keys(str(month_2))
			driver.find_element(By.CSS_SELECTOR, "#affordability-date2-year").send_keys(str(year_2))
			emp_stat_2 = driver.find_element(By.CSS_SELECTOR, "#affordability-employment2")
			driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", emp_stat_2)
			time.sleep(1)
			emp_stat_2.click()
			if applicant_two_empstatus == "Employed":
				driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="affordability-employment2"] li[data-value="Employed"]').click()
				time.sleep(1)
				driver.find_element(By.CSS_SELECTOR, "#affordability-main-income2").send_keys(str(basic_annual_income2))
				driver.find_element(By.CSS_SELECTOR, "#affordability-bonus-income2").send_keys(str(bonus2))
			elif applicant_two_empstatus == "Self Employed (Sole Trader/Partnership)" or applicant_two_empstatus=="Self Employed (Ltd Company/Director)":
				driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="affordability-employment2"] li[data-value="Self Employed"]').click()
				time.sleep(1)
				driver.find_element(By.CSS_SELECTOR, "#affordability-last-year-income2").send_keys(str(self_income_last_year_2))
				driver.find_element(By.CSS_SELECTOR, "#affordability-previous-year-income2").send_keys(str(self_income_previous_year_2))
			elif applicant_two_empstatus == "Retired":
				driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="affordability-employment2"] li[data-value="Retired"]').click()
				time.sleep(1)
				driver.find_element(By.CSS_SELECTOR, "#affordability-main-income2").send_keys(str(basic_annual_income2))
				driver.find_element(By.CSS_SELECTOR, "#affordability-bonus-income2").send_keys(str(bonus2))
			else:
				driver.find_element(By.CSS_SELECTOR, '[aria-labelledby="affordability-employment2"] li[data-value="Unemployed"]').click()
				time.sleep(1)
				driver.find_element(By.CSS_SELECTOR, "#affordability-main-income2").send_keys(str(basic_annual_income2))
				driver.find_element(By.CSS_SELECTOR, "#affordability-bonus-income2").send_keys(str(bonus2))
	except Exception as e:
		print(e)

	try:
		driver.find_element(By.CSS_SELECTOR, "#affordability-credit-card-commitment").send_keys(str(credit_commitments1))
		driver.find_element(By.CSS_SELECTOR, "#affordability-personal-loan-commitment").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#affordability-other-commitment").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#affordability-dependent").send_keys(str(num_of_dependants))
		ltv_option = driver.find_element(By.CSS_SELECTOR, "#affordability-loan-to-value-Yes")
		driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", ltv_option)
		ltv = int((loan_amount/Purchase_Price)*100)
		time.sleep(1)
		if ltv<=85:
			ltv_option.click()
		else:
			driver.find_element(By.CSS_SELECTOR, "#affordability-loan-to-value-No").click()

		driver.find_element(By.CSS_SELECTOR, "#affordability-term").send_keys(str(Loan_Term))
		half_postcode = post_code[:3]
		driver.find_element(By.CSS_SELECTOR, "#affordability-postcode").send_keys(half_postcode)
		driver.find_element(By.CSS_SELECTOR, "#affordability-valuation").send_keys(str(Purchase_Price))
	except Exception as e:
		print(e)

	try:
		htb_option = driver.find_element(By.CSS_SELECTOR, "#affordability-help-to-buy-Yes")
		driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", htb_option)
		time.sleep(1)
		if mortgage_type=="Shared Equity / Help To Buy":
			driver.find_element(By.CSS_SELECTOR, "#affordability-help-to-buy-Yes").click()
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#affordability-shared-equity").send_keys("0")
		else:
			driver.find_element(By.CSS_SELECTOR, "#affordability-help-to-buy-No").click()
	except Exception as e:
		print(e)

	try:
		purchase_or_mortgage = driver.find_element(By.CSS_SELECTOR, "#affordability-professional-No")
		driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", purchase_or_mortgage)
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#affordability-purpose-of-loan").click()
		time.sleep(1)
		if Loan_Type=="Purchase":
			driver.find_element(By.CSS_SELECTOR, '[data-value="Purchase"]').click()
		else:
			remort = driver.find_element(By.CSS_SELECTOR, '[data-value="Remortgage - Capital Raising"]')
			driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", remort)
			time.sleep(1)
			remort.click()

		driver.find_element(By.CSS_SELECTOR, "#affordability-professional-No").click()
	except Exception as e:
		print(e)

	button = driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Calculate affordability"]')
	driver.execute_script("arguments[0].scrollIntoView({ behavior: 'auto', block: 'center' });", button)
	time.sleep(1)
	driver.find_element(By.CSS_SELECTOR, 'button[aria-label="Calculate affordability"]').click()
	try:
		max_affordable = driver.find_element(By.CSS_SELECTOR, ".Result_ExternalCalculator").text
		print("Max Affordable : ",max_affordable)
		driver.close()
	except Exception as e:
		print(e)


config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)
# main()