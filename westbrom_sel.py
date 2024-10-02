from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import json
import requests
import time

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
	driver.get("https://apps.westbrom.co.uk/AffordabilityCalculator/default?wbfi=true")

	try:
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtClientRef").send_keys("12345")
		applying = "2" if num_of_applicants>2 else str(num_of_applicants)
		applicant_number = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_selNoApplying"))
		applicant_number.select_by_value(applying)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Name").send_keys("John")
		if num_of_applicants==2:
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Name").send_keys("John")
		number_of_adult_dependents = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_selAdultDependants"))
		number_of_adult_dependents.select_by_value("0")
		number_of_children = "3+" if num_of_dependants>2 else str(num_of_dependants)
		number_of_child_dependents = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_selAdultDependants"))
		number_of_child_dependents.select_by_value(number_of_children)
	except Exception as e:
		print(e)

	try:
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtBorrowingAmount1").send_keys(Keys.CONTROL + "a", Keys.DELETE)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtBorrowingAmount1").send_keys(str(loan_amount))
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtTermYears1").send_keys(Keys.CONTROL + "a", Keys.DELETE)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtTermYears1").send_keys(str(Loan_Term))
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtTermMonths1").send_keys(Keys.CONTROL + "a", Keys.DELETE)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtTermMonths1").send_keys(str(loan_term_months))
	except Exception as e:
		print(e)

	try:
		if applicant_one_empstatus == "Employed":
			emp_stat_1 = "Employed"
		elif applicant_one_empstatus == "Self Employed (Sole Trader/Partnership)":
			emp_stat_1 = "Self Employed"
		elif applicant_one_empstatus == "Retired":
			emp_stat_1 = "Retired"
		elif applicant_one_empstatus == "Not Working":
			emp_stat_1 = "Unemployed"
		else:
			emp_stat_1 = "Homemaker"

		emp_1 = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_selApp1Income1EmployStatus"))
		emp_1.select_by_value(emp_stat_1)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1Salary").send_keys(Keys.CONTROL + "a", Keys.DELETE)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1Salary").send_keys(str(basic_annual_income1))
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1Overtime").send_keys(Keys.CONTROL + "a", Keys.DELETE)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1Overtime").send_keys(str(overtime1))
		ot_freq_1 = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1OvertimeFreq"))
		ot_freq_1.select_by_value("Non-Monthly")
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1Commission").send_keys(Keys.CONTROL + "a", Keys.DELETE)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1Commission").send_keys(str(commision1))
		com_freq_1 = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1CommissionFreq"))
		com_freq_1.select_by_value("Non-Monthly")
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1Bonus").send_keys(Keys.CONTROL + "a", Keys.DELETE)
		driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1Bonus").send_keys(str(bonus1))
		bonus_freq_1 = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp1Income1BonusFreq"))
		bonus_freq_1.select_by_value("Non-Monthly")
		if num_of_applicants>1:
			if applicant_two_empstatus == "Employed":
				emp_stat_2 = "Employed"
			elif applicant_two_empstatus == "Self Employed (Sole Trader/Partnership)":
				emp_stat_2 = "Self Employed"
			elif applicant_two_empstatus == "Retired":
				emp_stat_2 = "Retired"
			elif applicant_two_empstatus == "Not Working":
				emp_stat_2 = "Unemployed"
			else:
				emp_stat_2 = "Homemaker"

			emp_2 = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_selApp2Income1EmployStatus"))
			emp_2.select_by_value(emp_stat_2)
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1Salary").send_keys(Keys.CONTROL + "a", Keys.DELETE)
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1Salary").send_keys(str(basic_annual_income2))
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1Overtime").send_keys(Keys.CONTROL + "a", Keys.DELETE)
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1Overtime").send_keys(str(overtime2))
			ot_freq_2 = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1OvertimeFreq"))
			ot_freq_2.select_by_value("Non-Monthly")
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1Commission").send_keys(Keys.CONTROL + "a", Keys.DELETE)
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1Commission").send_keys(str(commision2))
			com_freq_2 = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1CommissionFreq"))
			com_freq_2.select_by_value("Non-Monthly")
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1Bonus").send_keys(Keys.CONTROL + "a", Keys.DELETE)
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1Bonus").send_keys(str(bonus2))
			bonus_freq_2 = Select(driver.find_element(By.CSS_SELECTOR, "#MainContent_txtApp2Income1BonusFreq"))
			bonus_freq_2.select_by_value("Non-Monthly")
	except Exception as e:
		print(e)

	try:
		if rent_1:
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtGroundRentDeduct").send_keys(str(rent_1))
		if household_expenses_1:
			driver.find_element(By.CSS_SELECTOR, "#MainContent_txtPowerCommsDeduct").send_keys(str(household_expenses_1))
	except Exception as e:
		print(e)

	try:
		driver.find_element(By.CSS_SELECTOR, "#MainContent_btnCalc").click()
		time.sleep(1)
		max_affordable = driver.find_element(By.CSS_SELECTOR, "#MainContent_lblMaxLoanAmount").text
		print("Max Affordable : ", max_affordable)
	except Exception as e:
		print(e)

	driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)