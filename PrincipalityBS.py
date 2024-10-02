from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from datetime import datetime
import time
import json

#print(datetime.now().strftime("%m/%d/%Y, %H:%M:%S"))
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

	def calculate_age(birthdate):
		birth_date = datetime.strptime(birthdate, '%d/%m/%Y')
		current_date = datetime.now()
		age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
		return age

	location = data["Property Details"].get("Property Location")

	expenses = data["Client Details"][0].get("Outgoings", [])
	groceries = expenses.get("Living Costs", {}).get("Groceries", 0)
	council_tax = expenses.get("Household", {}).get("Council Tax", 0)
	transport = 0 if expenses.get("Transport") in null else expenses.get("Transport", 0)

	service = Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	driver.get("https://ac.principality.co.uk/AffordabilityCalculator.aspx")
	try:
		driver.find_element(By.CSS_SELECTOR, "#ddlTermYears").send_keys(str(Loan_Term))
		driver.find_element(By.CSS_SELECTOR, "#ddlMonths").send_keys(str(loan_term_months))
		
		applicants = Select(driver.find_element(By.NAME, "ddlApplicationType"))
		applicants.select_by_value(str(num_of_applicants))
		
		loan_purpose = "false" if Loan_Type == "Purchase" else "true"
		purpose = Select(driver.find_element(By.CSS_SELECTOR, "#ddlRemortgage"))
		purpose.select_by_value(loan_purpose)

		if loan_purpose == "true":
			additional_borrowing = "true" if existing_mortgage_amount>0 else "false"
			additional_mortgage = Select(driver.find_element(By.CSS_SELECTOR, "#ddlAdditional"))
			additional_mortgage.select_by_value(additional_borrowing)
			if additional_borrowing == "true":
				term = 60 if Product_Term==60 else 0
				product_term = Select(driver.find_element(By.CSS_SELECTOR, "#ddlLongTermFixed"))
				product_term.select_by_value(str(term))
		else:
			existing_mortgage = Select(driver.find_element(By.CSS_SELECTOR, "#ddlPorting"))
			existing_mortgage.select_by_value("false")
			term = 60 if Product_Term==60 else 0
			product_term = Select(driver.find_element(By.CSS_SELECTOR, "#ddlLongTermFixed"))
			product_term.select_by_value(str(term))

		#Applicants
		for i, applicant in enumerate(applicant_details):
			num_of_dependants += len(applicant.get("dependants", []))
			applicant_age = calculate_age(applicant.get("Date of Birth", "01/01/1990"))
			applicant_empstatus = applicant.get("Employment Details", {}).get("Employment Status", "")
			basic_annual_income = applicant.get("Employment Details", {}).get("Basic Annual Income", 0)
			overtime = applicant.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0)
			regular_bonus = applicant.get("Additional Income (Annual)", {}).get("Regular Bonus", 0)
			commission = applicant.get("Additional Income (Annual)", {}).get("Commission", 0)
			self_income_last_year = applicant.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
			self_income_previous_year = applicant.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
			credit = 0 if applicant.get("Outgoings", {}).get("Credit Commitments") in null else applicant.get("Outgoings", {}).get("Credit Commitments")

			salary = driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_AnnualSalary")
			salary.clear()
			salary.send_keys(basic_annual_income)

			irregular_overtime = driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_RegularOverTime")
			irregular_overtime.clear()
			irregular_overtime.send_keys(overtime)

			bonus = driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_RegularBonus")
			bonus.clear()
			bonus.send_keys(regular_bonus)

			regularCommision = driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_RegularCommission")
			regularCommision.clear()
			regularCommision.send_keys(commission)
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_ShiftAllowance").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_CarAllowance").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_LargeTownAllowance").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_SecondJob").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_MortgageAllowance").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_Pension").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtIncome_FamilyTaxCredits").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtDebt_MonthlyLoanPayment").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtDebt_MonthlyHirePurchase").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtDebt_MaintenancePayments").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_txtDebt_CreditCardBalance").send_keys(str(credit))
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_ddlStudentLoan").send_keys("false")
			driver.find_element(By.CSS_SELECTOR, f"#IncomeDebtinput{i+1}_ddlStudentLoanBeforeCutoff").send_keys("false")

		#applicants done
		number_of_adults = driver.find_element(By.CSS_SELECTOR, "#ONSInput_NumberOfAdultsTextBox")
		number_of_adults.clear()
		number_of_adults.send_keys(str(num_of_applicants))
		
		retired_adults = driver.find_element(By.CSS_SELECTOR, "#ONSInput_NumberOfRetiredAdultsTextBox")
		retired_adults.clear()
		retired_adults.send_keys("0")
		
		children = driver.find_element(By.CSS_SELECTOR, "#ONSInput_NumberOfChildrenTextBox")
		children.clear()
		children.send_keys(str(num_of_dependants))

		if location == "Northern Ireland":
			ONS_location = "North East"
		elif location == "England":
			ONS_location = "London"
		elif location == "Wales":
			ONS_location = "Wales"
		elif location == "Scotland":
			ONS_location = "North West"
		else:
			ONS_location = "East"

		driver.find_element(By.CSS_SELECTOR, "#ONSInput_RegionDropDownList").send_keys(ONS_location)

		food = driver.find_element(By.CSS_SELECTOR, "#ONSInput_FoodAndDrinkTextBox")
		food.clear()
		food.send_keys(str(groceries))

		bills = driver.find_element(By.CSS_SELECTOR, "#ONSInput_BillsTextBox")
		bills.clear()
		bills.send_keys(str(council_tax))
		
		transport_box = driver.find_element(By.CSS_SELECTOR, "#ONSInput_TransportTextBox")
		transport_box.clear()
		transport_box.send_keys(str(transport))

		communication = driver.find_element(By.CSS_SELECTOR, "#ONSInput_CommunicationsTextBox")
		communication.clear()
		communication.send_keys("0")

		health = driver.find_element(By.CSS_SELECTOR, "#ONSInput_HealthTextBox")
		health.clear()
		health.send_keys("0")

		clothing = driver.find_element(By.CSS_SELECTOR, "#ONSInput_ClothingAndFootwearTextBox")
		clothing.clear()
		clothing.send_keys("0")

		goods = driver.find_element(By.CSS_SELECTOR, "#ONSInput_GoodsAndServicesTextBox")
		goods.clear()
		goods.send_keys("0")

		recreation = driver.find_element(By.CSS_SELECTOR, "#ONSInput_RecreationTextBox")
		recreation.clear()
		recreation.send_keys("0")

		education = driver.find_element(By.CSS_SELECTOR, "#ONSInput_EducationTextBox")
		education.clear()
		education.send_keys("0")

		misc = driver.find_element(By.CSS_SELECTOR, "#ONSInput_MiscTextBox")
		misc.clear()
		misc.send_keys("0")

		driver.find_element(By.NAME, "btnCalculate").click()

		# time.sleep(20)
		max_affordable = driver.find_element(By.CSS_SELECTOR, "#txtTotalLoanAmount").get_attribute("value")

		print(f"max affordable : {max_affordable}\n")
	except Exception as e:
		print(f"Error: {e}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)