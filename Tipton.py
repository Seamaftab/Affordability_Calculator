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

	household_expenses = applicant_one["Outgoings"].get("Household")
	rent = household_expenses.get("Mortgage / Rent")
	serviceCharge = household_expenses.get("Service Charge", 0)
	sum_household_expenses = sum(household_expenses.values())

	credit_commitments1 = 0 if applicant_one.get("Outgoings", {}).get("Credit Commitments") in null else applicant_one.get("Outgoings", {}).get("Credit Commitments")
	credit_commitments2 = 0 if applicant_two.get("Outgoings", {}).get("Credit Commitments") in null else applicant_one.get("Outgoings", {}).get("Credit Commitments")

	location = data["Property Details"].get("Property Location")
	property_type = data["Property Details"].get("Property Type")
	property_age = data["Property Details"].get("Property Age", 0)

	expenses = data["Client Details"][0].get("Outgoings", [])
	groceries = expenses.get("Living Costs", {}).get("Groceries", 0)
	council_tax = expenses.get("Household", {}).get("Council Tax", 0)
	transport = 0 if expenses.get("Transport") in null else expenses.get("Transport", 0)

	service = Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	driver.get("https://www.thetipton.co.uk/our-mortgages/affordability-calculator/")
	try:
		time.sleep(2)
		driver.find_element(By.CSS_SELECTOR ,"#CybotCookiebotDialogBodyButtonDecline").click()
	except:
		pass
	try:
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#FirstName").send_keys("John")
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#BorrowerTypeSelectBoxItText").click()
		purchase_or_remortgage = "First Time Buyer" if Loan_Type == "Purchase" else "Remortgage"
		borrower_type_select = driver.find_element(By.CSS_SELECTOR, f'li[data-val="{purchase_or_remortgage}"]').click()

		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#A2").send_keys(str(num_of_applicants))
		# applicants = driver.find_element(By.CSS_SELECTOR, "#A2")
		# driver.execute_script("arguments[0].value = '{}';".format(num_of_applicants), applicants)
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#A5").send_keys(str(num_of_applicants))
		driver.find_element(By.CSS_SELECTOR, "#A3").send_keys("0")
		driver.find_element(By.CSS_SELECTOR, "#A4").clear()
		driver.find_element(By.CSS_SELECTOR, "#A4").send_keys(str(num_of_dependants))
		#time.sleep(5)
		driver.find_element(By.CSS_SELECTOR, '.step-one.current .row .desk-7 [name="next"]').click()
		#time.sleep(3)
	except Exception as e:
		print(f"Error: {e}")

	try:
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#E15").send_keys(str(basic_annual_income1))
		driver.find_element(By.CSS_SELECTOR, "#E16").send_keys(str(bonus1))
		driver.find_element(By.CSS_SELECTOR, "#E17").send_keys(str(overtime1))
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, "#J15").send_keys(str(basic_annual_income2))
			driver.find_element(By.CSS_SELECTOR, "#J16").send_keys(str(bonus2))
			driver.find_element(By.CSS_SELECTOR, "#J17").send_keys(str(overtime2))
		#time.sleep(5)
		driver.find_element(By.CSS_SELECTOR, '.step-two.current .row .desk-7 [name="next"]').click()
		#time.sleep(3)
	except Exception as e:
		print(f"Error: {e}")

	try:
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, '[name="E23"]').send_keys(str(net_income1))
		if num_of_applicants>1:
			driver.find_element(By.CSS_SELECTOR, '[name="E24"]').send_keys(str(net_income2))
		#time.sleep(5)
		driver.find_element(By.CSS_SELECTOR, '.step-three.current .row .desk-7 [name="next"]').click()
		#time.sleep(3)
	except Exception as e:
		print(f"Error: {e}")

	try:
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, '[name="E33"]').send_keys(str(credit_commitments1+credit_commitments2))
		driver.find_element(By.CSS_SELECTOR, '[name="E37"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E38"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E39"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E40"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E42"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E44"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E45"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E46"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E47"]').send_keys(str(rent))
		driver.find_element(By.CSS_SELECTOR, '[name="E48"]').send_keys("0")
		driver.find_element(By.CSS_SELECTOR, '[name="E49"]').send_keys("0")
		#time.sleep(5)
		driver.find_element(By.CSS_SELECTOR, '.step-four.current .row .desk-7 [name="next"]').click()
		#time.sleep(3)
	except Exception as e:
		print(f"Error: {e}")

	try:
		time.sleep(1)
		driver.find_element(By.CSS_SELECTOR, "#G5SelectBoxItText").click()
		place = "2" if location == "England" else "1"
		driver.find_element(By.CSS_SELECTOR, f'li[data-val="{place}"]').click()
		year = driver.find_element(By.CSS_SELECTOR, "#J24")
		driver.execute_script("arguments[0].value = '{}';".format(Loan_Term), year)

		driver.find_element(By.CSS_SELECTOR, "#J25").send_keys(str(Purchase_Price))
		driver.find_element(By.CSS_SELECTOR, "#J26").send_keys(str(loan_amount))    
		#time.sleep(5)
		driver.find_element(By.CSS_SELECTOR, "#Submit").click()
		#time.sleep(3)
	except Exception as e:
		print(f"Error: {e}")

	max_affordable = driver.find_element(By.CSS_SELECTOR, "#Borrowing").text
	print("Max Affordable : ", max_affordable)

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)
# main()
