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

	# with open('config_one.json') as file:
	# 	data = json.load(file)

	null = ["null", None]
	mortgage_type = data["Mortgage Requirement"].get("Mortgage Type")
	Payment_Method = data["Mortgage Requirement"].get("Payment Method")
	Loan_Term = int(data["Mortgage Requirement"].get("Loan Term")/12)
	loan_term_months = int(data["Mortgage Requirement"].get("Loan Term")%12)
	Product_Term = data["Mortgage Requirement"].get("Product term", 60)
	Loan_Type = data["Mortgage Requirement"].get("Loan Purpose")
	Purchase_Price = data["Mortgage Requirement"].get("Purchase Price", 0)
	loan_amount = data["Mortgage Requirement"].get("Loan Amount", 0)
	share = data["Mortgage Requirement"].get("Share of Value (%)")
	existing_mortgage_amount = data.get("Existing Mortgage Details", {}).get("current Mortgage Outstanding", 0)

	num_of_applicants = data.get("No of Applicant")
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])
	for applicant in applicant_details:
		num_of_dependants += len(applicant.get("dependants", []))

	def calculate_age(birthdate):
		birth_date = datetime.strptime(birthdate, '%d/%m/%Y')
		current_date = datetime.now()
		age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
		return age

	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details)>1 else {}

	location = data["Property Details"].get("Property Location")
	post_code =data["Property Details"].get("Property Details", {}).get("Post Code")
	property_type = data["Property Details"].get("Property Type")
	property_age = data["Property Details"].get("Property Age", 0)

	expenses = data["Client Details"][0].get("Outgoings", [])
	groceries = expenses.get("Living Costs", {}).get("Groceries", 0)
	council_tax = expenses.get("Household", {}).get("Council Tax", 0)
	transport = 0 if expenses.get("Transport") in null else expenses.get("Transport", 0)

	if Purchase_Price<200000:
		print("The resultant loan amount is not affordable.\nDeposite/Equity should be at least 200,000")
	else:
		service = Service(executable_path="chromedriver.exe")
		driver = webdriver.Chrome(service=service)
		driver.get("https://suffolkbs.calc.affordabilityhub.co.uk/affordability")

		try:
			purchase_or_remortgage = "Purchase" if Loan_Type == "Purchase" else "Remortgage"
			purchase_or_remortgage_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-fff50dc9-57ed-4715-ad97-37ae6a5033ae"))
			purchase_or_remortgage_dropdown.select_by_value(purchase_or_remortgage)

			driver.find_element(By.CSS_SELECTOR, "#q-8cbdfae3-9ed0-49cb-affa-287e550a1e06").clear()
			driver.find_element(By.CSS_SELECTOR, "#q-8cbdfae3-9ed0-49cb-affa-287e550a1e06").send_keys(str(Purchase_Price))
			if Payment_Method=="Repayment":
				repay = "C"
			elif Payment_Method=="Interest Only":
				repay = "I"
			else:
				repay = "M"
			repay_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-5a54a130-eb2f-44b5-bd36-25b6a8f4376e"))
			repay_dropdown.select_by_value(repay)

			if repay=="C":
				driver.find_element(By.CSS_SELECTOR, "#q-1f0acfe3-ce65-402f-b5e3-813f5ae700e3").send_keys(str(loan_amount))
			elif repay=="I":
				driver.find_element(By.CSS_SELECTOR, "#q-c870b754-1594-43da-bd14-04f17f88b801").send_keys(str(loan_amount))
			else:
				driver.find_element(By.CSS_SELECTOR, "#q-1f0acfe3-ce65-402f-b5e3-813f5ae700e3").send_keys(str(loan_amount))
				driver.find_element(By.CSS_SELECTOR, "#q-c870b754-1594-43da-bd14-04f17f88b801").send_keys("0")

			term_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-f22b0020-65b5-4327-bccf-975c75fedf6b"))
			term_dropdown.select_by_value(str(Loan_Term))
			applicants_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-01501241-eeab-41d0-9089-af446be00c48"))
			applicants_dropdown.select_by_value(str(num_of_applicants))
			five_year_product = "Y" if Product_Term == 60 else "N"
			five_year_product_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-3f4f6385-ca1c-41d1-a87d-9caff00a005d"))
			five_year_product_dropdown.select_by_value(five_year_product)
			shared_ownership = "Y" if mortgage_type == "Shared Ownership" else "N"
			shared_ownership_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-e097007b-7ff9-4c1c-ab19-d523953aeaf9"))
			shared_ownership_dropdown.select_by_value(str(shared_ownership))
		except Exception as e:
			print(e)

		try:
			country = "W" if location == "Wales" else "E"
			country_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-5196874d-553e-43fd-bf9a-9daeec8abf54"))
			country_dropdown.select_by_value(country)
			flat_or_house = "HB" if property_type == "House" else "FA"
			flat_or_house_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-b6897c05-fc2b-4ce2-9ffb-af3ace5ea96d"))
			flat_or_house_dropdown.select_by_value(flat_or_house)
			age_of_property = "Y" if property_age <= 24 else "N"
			age_of_property_dropdown = Select(driver.find_element(By.CSS_SELECTOR, "#q-3c9a84b9-3daf-4466-b5dc-533b53ed8043"))
			age_of_property_dropdown.select_by_value(age_of_property)
		except Exception as e:
			print(e)

		try:
			driver.find_element(By.CSS_SELECTOR, "#q-fd22aa24-4b50-4482-8847-12a14633e9cf").send_keys("1")
			driver.find_element(By.CSS_SELECTOR, "#q-604561ac-2457-4182-885e-ab0c4a24826a").send_keys("1")
			if shared_ownership == "Y":
				driver.find_element(By.CSS_SELECTOR, "#q-91d57477-8bca-4c29-84a8-c3edac1ed309").send_keys("1")
			else:
				driver.find_element(By.CSS_SELECTOR, "#q-91d57477-8bca-4c29-84a8-c3edac1ed309").send_keys("0")
		except Exception as e:
			print(e)

		try:
			for i,applicant in enumerate(applicant_details):
				applicant_empstatus = applicant.get("Employment Details", {}).get("Employment Status", "")
				basic_annual_income= applicant.get("Employment Details", {}).get("Basic Annual Income", 0)
				net_income= int(basic_annual_income*0.06704) if applicant.get("Employment Details", {}).get("Net Monthly Income") in null else applicant.get("Employment Details", {}).get("Net Monthly Income")
				overtime= applicant.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0)
				bonus= applicant.get("Additional Income (Annual)", {}).get("Regular Bonus", 0)
				commision= applicant.get("Additional Income (Annual)", {}).get("Commission", 0)

				date_of_birth = '-'.join(reversed(applicant.get("Date of Birth").split('/')))
				title = applicant.get("Title", "Mr")
				retirement_age= applicant.get("expected retirement age", 70)

				self_income_last_year = applicant.get("Employment Details", {}).get("Last Year's Salary", 0)
				self_income_previous_year = applicant.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
				net_profit = applicant.get("Employment Details", {}).get("Last Year's Net Profits", 0)
				dividend = applicant.get("Employment Details", {}).get("Last Year's Dividends", 0)

				household_expenses= applicant.get("Outgoings", {}).get("Household")
				total_outgoings = sum(int(value) for value in applicant.get("Outgoings", {}).get("Household").values())
				rent = household_expenses.get("Mortgage / Rent")
				serviceCharge = household_expenses.get("Service Charge", 0)
				credit_commitments= 0 if applicant.get("Outgoings", {}).get("Credit Commitments") in null else applicant.get("Outgoings", {}).get("Credit Commitments")
				dependants = applicant["dependants"]
				if len(dependants) > 0:
					dependant_age = calculate_age(dependants[0]["date of birth"])
				else:
					pass

				driver.find_element(By.CSS_SELECTOR, f'[data-target="#collapseApp{i+1}"]').click()
				time.sleep(1)
				driver.execute_script(f"arguments[0].value='{date_of_birth}';", driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-baa87d1d-329b-4f3b-a5aa-c3184b12972a"))

				if applicant["Employment Details"].get("Employment Status")=="Retired":
					retired_dropdown = Select(driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-ec011eab-434e-4087-a299-8497bcd16b1c"))
					retired_dropdown.select_by_value("Y")
				else:
					retired_age_dropdown = Select(driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-8d71905e-8b3e-4470-89d1-85c7ec8cf646"))
					retired_age_dropdown.select_by_value(str(retirement_age))

				dependant_num = "1" if len(dependants)>0 else "0"
				dependants_dropdown = Select(driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-fc8b37e0-3262-4dd9-bc83-23b14bd173d1"))
				dependants_dropdown.select_by_index(dependant_num)
				if len(dependants)>0:
					dependant_age_dropdown = Select(driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-af0a849d-de8a-4dee-b891-2cd38735f950"))
					dependant_age_dropdown.select_by_value(str(dependant_age))

				driver.find_element(By.CSS_SELECTOR, f'[data-target="#collapseIncomeEmployed{i+1}"]').click()
				time.sleep(1)
				driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-3ee7ef80-0df1-4bea-a0db-d109c24fbcd6").send_keys(str(basic_annual_income))
				driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-3b23f5f2-7d3c-46b6-a4bf-4b529628defb").send_keys(str(bonus))
				driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-29987ae2-45a8-4d32-9ba1-998f6e7b7349").send_keys(str(overtime))

				driver.find_element(By.CSS_SELECTOR, f'[data-target="#collapseExBasic{i+1}"]').click()
				time.sleep(1)
				driver.find_element(By.CSS_SELECTOR, f"#app-{i+1}-q-6ddc7afe-a408-47a1-87d1-64987abe07f1").send_keys(total_outgoings)

			driver.find_element(By.CSS_SELECTOR, "#submit button").click()
		except Exception as e:
		    print(f"Error: {e}")

		time.sleep(3)
		mortgage_result_text = driver.find_element(By.CSS_SELECTOR, "#mortgage_result p").text
		print(mortgage_result_text)
		max_affordable = driver.find_element(By.ID, "mortgage_loan").text
		print("Max Affordable : ",max_affordable)

		driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)