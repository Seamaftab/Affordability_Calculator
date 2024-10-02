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

	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details)>1 else {}

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

	marital_status = applicant_details[0].get("Marital Status")

	applicant_type = applicant_details[0].get("Applicant Type")

	location = data["Property Details"].get("Property Location")
	product_type = data["Property Details"].get("Property Type")
	property_age = data["Property Details"].get("Property Age")

	expenses = data["Client Details"][0].get("Outgoings", [])
	groceries = expenses.get("Living Costs", {}).get("Groceries", 0)
	council_tax = expenses.get("Household", {}).get("Council Tax", 0)
	transport = 0 if expenses.get("Transport") in null else expenses.get("Transport", 0)

	service = Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	driver.get("https://affordability.clydesdalebankintermediaries.co.uk/")

	try:
		sole_or_joint = "Joint" if num_of_applicants>1 else "Sole"
		sole_or_joint_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#a0865482-e783-4b32-b434-370745a608bc"))
		sole_or_joint_dropdown.select_by_value(sole_or_joint)

		residential_or_not = "Buy to Let" if Mortgage_Type == "Buy To Let" else "Residential"
		residential_or_not_dropdown = Select(driver.find_element(By.ID, "38e37411-e8f2-4b33-f83a-28b7c8f26698"))
		residential_or_not_dropdown.select_by_value(residential_or_not)

		if location == "Northern Ireland":
			country = "Northern Ireland"
		elif location == "England":
			country = "England"
		elif location == "Scotland":
			country = "Scotland"
		else:
			country = "Wales"

		country_dropdown = Select(driver.find_element(By.ID, "7ce1737b-ffcb-4e0d-cb2b-0e5cb0e84e9c"))
		country_dropdown.select_by_value(country)

		if property_age<24:
			if property_type == "House":
				build = "Yes (House)"
			else:
				build = "Yes (Flat)"
		else:
			build = "No"

		build_dropdown = Select(driver.find_element(By.ID, "6b629ea9-8012-4271-aecf-07378a8c0c30"))
		build_dropdown.select_by_value(build)

		dependants = driver.find_element(By.CSS_SELECTOR, "#dfe68bd1-73ff-420d-a8d2-380da017c461")
		dependants.clear()
		dependants.send_keys(num_of_dependants)

		married_or_single = "Married / Civil Partnership" if marital_status == "Married" else "Single"
		married_or_single_dropdown = Select(driver.find_element(By.ID, "d31a1584-44ac-4287-8235-01c44f38b361"))
		married_or_single_dropdown.select_by_value(married_or_single)

		first_time_buyer = "First Time Buyer" if applicant_type == "First Time Buyer" else "Remortgage with additional lending"
		buyer_type = Select(driver.find_element(By.ID, "d6eb5350-700f-43ab-967a-af0396058fac"))
		buyer_type.select_by_value(first_time_buyer)

		if Payment_Method == "Repayment":
			repay = "Capital and Interest"
		elif Payment_Method == "Interest Only":
			repay = "Interest Only"
		else:
			repay = "Part & Part"
		repayment = Select(driver.find_element(By.ID, "06cf0513-ebfb-4890-f2ae-48745467f25f"))
		repayment.select_by_value(repay)

		driver.find_element(By.ID, "28c30c92-4d1f-4e41-9207-077554bab9c5").send_keys(str(Loan_Term))

		loan_months = driver.find_element(By.ID, "67327a23-e15b-4b76-ca83-6d112ea1ed98")
		loan_months.clear()
		loan_months.send_keys(str(loan_term_months))

		driver.find_element(By.ID, "e9d5c1f1-4ce8-4c4d-af9c-b0fef482860e").send_keys(str(loan_amount))
		driver.find_element(By.ID, "0c857694-e719-43e0-bdd2-314d15534912").send_keys(str(Purchase_Price))

		fixed_term = Select(driver.find_element(By.ID, "917a7c5e-e9f2-43a5-bbdf-9d7224ab499b"))
		fixed_term.select_by_value("Fixed")

		driver.find_element(By.ID, "0897c929-465c-4d51-fb9d-9441750df1eb").send_keys("1")

		term = "5 Years" if Product_Term == 60 else "2 Years"
		term_selected = Select(driver.find_element(By.ID, "bcaf949c-b20b-42af-d723-359e27e3a0a2"))
		term_selected.select_by_value(term)

		any_other_house = Select(driver.find_element(By.ID, "b151081b-5b14-4bff-f4ae-d10f7e54d47f"))
		any_other_house.select_by_value("No")

		driver.find_element(By.CSS_SELECTOR, ".c-a-button__title").click()
	except Exception as e:
		print(e)

	try:
		if applicant_one_empstatus == "Employed":
			emp_stat_1 = "Employed"
		elif applicant_one_empstatus == "Self Employed (Sole Trader/Partnership)":
			emp_stat_1 = "Self-employed"
		elif applicant_one_empstatus == "Retired":
			emp_stat_1 = "Retired"
		elif applicant_one_empstatus == "Not Working":
			emp_stat_1 = "Unemployed"
		else:
			emp_stat_1 = "Student"
		employment_status_1 = Select(driver.find_element(By.ID, "ad623ea5-ce00-4e12-ec9a-f6ef3d4fb9c5"))
		employment_status_1.select_by_value(emp_stat_1)

		over_30k_1 = "Yes" if basic_annual_income1>=30000 else "No"
		over_30k_1_dropdown = Select(driver.find_element(By.ID, "d1a159f1-0284-4ce5-a6cc-aae2549c5fa5"))
		over_30k_1_dropdown.select_by_value(over_30k_1)

		income_1 = driver.find_element(By.ID, "6dcafae9-7f49-4705-c584-787dcca68689")
		income_1.clear()
		income_1.send_keys(str(basic_annual_income1))

		bonus_income_1 = driver.find_element(By.ID, "a13da10d-506d-41b2-8205-ffa176fc8bab")
		bonus_income_1.clear()
		bonus_income_1.send_keys(str(bonus1+overtime1))

		driver.find_element(By.ID, "62608785-d216-4796-c5e0-d2d9d5c27458").clear()
		driver.find_element(By.ID, "62608785-d216-4796-c5e0-d2d9d5c27458").send_keys("0")
		driver.find_element(By.ID, "2ca59395-acf3-486a-867d-5d32b8d1f817").clear()
		driver.find_element(By.ID, "2ca59395-acf3-486a-867d-5d32b8d1f817").send_keys("0")
		driver.find_element(By.ID, "1dfb2ec7-1882-48f2-c8ba-df39c5cff6f0").clear()
		driver.find_element(By.ID, "1dfb2ec7-1882-48f2-c8ba-df39c5cff6f0").send_keys(str(self_income_last_year_1))
		driver.find_element(By.ID, "43c078b3-cf73-4b2c-dcc5-a52bf37f3d32").clear()
		driver.find_element(By.ID, "43c078b3-cf73-4b2c-dcc5-a52bf37f3d32").send_keys(str(self_income_previous_year_1))

		if num_of_applicants>1:
			if applicant_one_empstatus == "Employed":
				emp_stat_2 = "Employed"
			elif applicant_one_empstatus == "Self Employed (Sole Trader/Partnership)":
				emp_stat_2 = "Self-employed"
			elif applicant_one_empstatus == "Retired":
				emp_stat_2 = "Retired"
			elif applicant_one_empstatus == "Not Working":
				emp_stat_2 = "Unemployed"
			else:
				emp_stat_2 = "Student"
			employment_status_2 = Select(driver.find_element(By.ID, "e99236fd-75fc-4051-9bf6-a7e46ab97795"))
			employment_status_2.select_by_value(emp_stat_2)

			over_30k_2 = "Yes" if basic_annual_income1>=30000 else "No"
			over_30k_2_dropdown = Select(driver.find_element(By.ID, "fe26ef94-afa5-42cf-a2cc-036a504e52f5"))
			over_30k_2_dropdown.select_by_value(over_30k_2)

			income_2 = driver.find_element(By.ID, "865fc541-9675-4e7e-d20d-f67240a06523")
			income_2.clear()
			income_2.send_keys(str(basic_annual_income2))

			bonus_income_2 = driver.find_element(By.ID, "4ff0c532-14be-4214-b55e-ff8293bb3d6a")
			bonus_income_2.clear()
			bonus_income_2.send_keys(str(bonus2+overtime2))

			driver.find_element(By.ID, "88f2b608-8807-4c31-fbe3-2335d0c105d6").clear()
			driver.find_element(By.ID, "88f2b608-8807-4c31-fbe3-2335d0c105d6").send_keys("0")
			driver.find_element(By.ID, "8dfdd723-7f9c-4afe-8f98-eec5ea2f1b1d").clear()
			driver.find_element(By.ID, "8dfdd723-7f9c-4afe-8f98-eec5ea2f1b1d").send_keys("0")
			driver.find_element(By.ID, "598edfaa-492d-4537-dbda-4f20d34764b0").clear()
			driver.find_element(By.ID, "598edfaa-492d-4537-dbda-4f20d34764b0").send_keys(str(self_income_last_year_2))
			driver.find_element(By.ID, "4206dde2-b8a4-400b-92f1-7cc0ee686786").clear()
			driver.find_element(By.ID, "4206dde2-b8a4-400b-92f1-7cc0ee686786").send_keys(str(self_income_previous_year_2))

		buy_to_let_rent = data["Mortgage Requirement"].get("Buy to Let Details", {}).get("Expected Rental Income Per Month", 0)
		driver.find_element(By.ID, "86012891-d37e-4682-b489-379a1da0a596").send_keys(buy_to_let_rent)

		driver.find_element(By.CSS_SELECTOR, ".c-a-button__title").click()
	except Exception as e:
		print(e)

	try:
		driver.find_element(By.ID, "5b04c847-9971-4fc2-a539-458196704c17").send_keys("0")
		driver.find_element(By.ID, "9d098580-5134-408f-d6c2-46c10c2c4c3a").send_keys(str(credit_commitments1))
		driver.find_element(By.ID, "f7c68123-8454-4d3e-8d10-ce32c518b616").send_keys("0")
		driver.find_element(By.ID, "a43e8cf3-81e3-4f64-fe1e-2ec119a03cc6").send_keys("0")
		driver.find_element(By.ID, "69ec42c0-1395-41d9-d88c-3dac1b73d404").send_keys("0")

		if num_of_applicants>1:
			driver.find_element(By.ID, "f9fb66f1-8dc7-4965-d44e-3fb217443872").send_keys("0")
			driver.find_element(By.ID, "9e218459-289e-4bed-80d6-f0a50d184f6b").send_keys("0")
			driver.find_element(By.ID, "a207e1f2-1024-4a3b-b4fb-ec41f94bb956").send_keys("0")
			driver.find_element(By.ID, "08049551-623d-48c4-89b9-34a6f6b3e02f").send_keys("0")
			driver.find_element(By.ID, "63295870-35da-47ef-e8e0-b741b80a8e8b").send_keys(str(credit_commitments2))
		
		driver.find_element(By.ID, "88e9c14f-3088-43ab-b116-004ec5bcab3e").send_keys("0")
		driver.find_element(By.ID, "3482df01-0c62-4a5d-8fff-9a286f2f028f").send_keys("0")
		driver.find_element(By.ID, "8ec77fec-8248-4907-bc97-334f8dc04fef").send_keys("0")
		driver.find_element(By.ID, "811e9021-7fc9-4866-8ed3-c7757f433bd6").send_keys("0")

		driver.find_element(By.CSS_SELECTOR, ".c-a-button__title").click()
	except Exception as e:
		print(e)

	amount1 = driver.find_element(By.CSS_SELECTOR, ".ammounts p strong").text
	#amount2 = driver.find_element(By.CSS_SELECTOR, ".ammounts.border p strong").text

	print("Max Assisting Borrowing Amount : ", amount1)
	#print("Max Affordable Amount : ", amount2)

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)