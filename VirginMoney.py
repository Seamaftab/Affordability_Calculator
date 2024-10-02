from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
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
	Product_Period = int(data["Mortgage Requirement"].get("Product term")/12)
	Loan_Type = data["Mortgage Requirement"].get("Loan Purpose")
	Purchase_Price = data["Mortgage Requirement"].get("Purchase Price", 0)
	loan_amount = data["Mortgage Requirement"].get("Loan Amount", 0)
	share = data["Mortgage Requirement"].get("Share of Value (%)")

	num_of_applicants = data.get("No of Applicant")
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])
	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details) > 1 else {}

	num_of_dependants += len(applicant_one.get("dependants", [])) + len(applicant_two.get("dependants", []))

	def calculate_age(birthdate):
		birth_date = datetime.strptime(birthdate, '%d/%m/%Y')
		current_date = datetime.now()
		age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
		return age

	applicant_one_age = calculate_age(applicant_one.get("Date of Birth", "01/01/1990"))
	applicant_two_age = calculate_age(applicant_two.get("Date of Birth", "01/01/1990"))

	applicant_one_empstatus = applicant_one.get("Employment Details", {}).get("Employment Status", "")
	applicant_two_empstatus = applicant_two.get("Employment Details", {}).get("Employment Status", "")
	basic_annual_income1 = applicant_one.get("Employment Details", {}).get("Basic Annual Income", 0)
	basic_annual_income2 = applicant_two.get("Employment Details", {}).get("Basic Annual Income", 0)
	overtime1 = applicant_one.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0) + applicant_one.get("Additional Income (Annual)", {}).get("Regular Bonus", 0)
	overtime2 = applicant_two.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0) + applicant_two.get("Additional Income (Annual)", {}).get("Regular Bonus", 0)
	total_income = basic_annual_income1 + basic_annual_income2 + overtime1 + overtime2

	self_income_last_year_1 = applicant_one.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	self_income_previous_year_1 = applicant_one.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	self_income_last_year_2 = applicant_two.get("Employment Details", {}).get("Previous Year's Net Profits", 0)
	self_income_previous_year_2 = applicant_two.get("Employment Details", {}).get("Previous Year's Net Profits", 0)

	location = data["Property Details"].get("Property Location")

	household_expenses = applicant_one["Outgoings"].get("Household")
	rent = household_expenses.get("Mortgage / Rent")
	serviceCharge = household_expenses.get("Service Charge", 0)
	sum_household_expenses = sum(household_expenses.values())

	credit = 0 if applicant_one.get("Outgoings", {}).get("Credit Commitments") in null else applicant_one.get("Outgoings", {}).get("Credit Commitments")

	service = Service(executable_path="chromedriver.exe")
	driver = webdriver.Chrome(service=service)
	if Mortgage_Type == "Shared Ownership" and share>75:
		print("Max Affordable : £ 0")
		print("Share in Shared Ownership and LTV cannot go over 75%")
	elif Payment_Method == "Interest Only" and total_income < 75000:
		print("Max Affordable : £ 0")
		print("They cannot offer a mortgage on an interest only basis if the total income is below £75,000")
	else:
		driver.get("https://intermediaries.virginmoney.com/vmtools/affordability-calculator/loan/38015d36-29b0-4dde-aae2-ae1c40bab9b2/")
		try:
			if Mortgage_Type == "Shared Ownership":
				ApplicationType = "#ApplicationTypeSharedOwnership"
			else:
				ApplicationType = "#ApplicationTypeResidential"
			driver.find_element(By.CSS_SELECTOR, ApplicationType).click()
			
			if ApplicationType == "#ApplicationTypeResidential":
				if Payment_Method == "Repayment":
					RepaymentMethod = "#RepaymentMethodRepayment"
				elif Payment_Method == "Interest Only":
					RepaymentMethod = "#RepaymentMethodInterestOnly"
				else:
					RepaymentMethod = "#RepaymentMethodPartAndPart"
				driver.find_element(By.CSS_SELECTOR, RepaymentMethod).click()

			driver.find_element(By.CSS_SELECTOR, "#LoanTerm").send_keys(str(Loan_Term))
			
			if Product_Period != 5:
				driver.find_element(By.CSS_SELECTOR, "#ProductPeriodNo").click()

			percentage = driver.find_element(By.CSS_SELECTOR, "#productPercentage")
			percentage.clear()
			percentage.send_keys("1")

			if ApplicationType == "#ApplicationTypeResidential":
				loantype = "#LoanTypePurchase" if Loan_Type == "Purchase" else "#LoanTypeRemortgage"
				driver.find_element(By.CSS_SELECTOR, loantype).click()

			propertyValue = driver.find_element(By.CSS_SELECTOR, "#PropertyValue")
			propertyValue.clear()
			propertyValue.send_keys(str(Purchase_Price))

			if ApplicationType == "#ApplicationTypeResidential":
				if RepaymentMethod == "#RepaymentMethodPartAndPart":
						LoanRequired = driver.find_element(By.CSS_SELECTOR, "#RepayLoanRequired")
						LoanRequired.clear()
						LoanRequired.send_keys(str(loan_amount))

						InterestOnlyAmount = driver.find_element(By.CSS_SELECTOR, "#IOLoanRequired")
						InterestOnlyAmount.clear()
						InterestOnlyAmount.send_keys(str(Purchase_Price - loan_amount))
				else:
					LoanRequired = driver.find_element(By.CSS_SELECTOR, "#LoanRequired")
					LoanRequired.clear()
					LoanRequired.send_keys(str(loan_amount))
			else:
				LoanRequired = driver.find_element(By.CSS_SELECTOR, "#LoanRequired")
				LoanRequired.clear()
				LoanRequired.send_keys(str(loan_amount))

				shared_percentage = driver.find_element(By.CSS_SELECTOR, "#PercentageShare")
				shared_percentage.clear()
				shared_percentage.send_keys(str(share))

			driver.find_element(By.CSS_SELECTOR, ".button.continuebtnXX input[type='submit']").click()
		except Exception as e:
			print(f"Error: {e}")

		try:
			if num_of_applicants == 1:
				driver.find_element(By.CSS_SELECTOR, "#NumberOfApplicants1").click()
			else:
				driver.find_element(By.CSS_SELECTOR, "#NumberOfApplicants2").click()
			
			dependents = driver.find_element(By.CSS_SELECTOR, "#Dependants")
			dependents.send_keys(str(num_of_dependants))

			driver.find_element(By.CSS_SELECTOR, "#Age0").send_keys(str(applicant_one_age))

			if location == "Northern Ireland":
				residency = "#NiResidency"
			elif location == "Wales":
				residency = "#WalesResidency"
			elif location == "Scotland":
				residency = "#ScotlandResidency"
			else:
				residency = "#EnglandResidency"

			driver.find_element(By.CSS_SELECTOR, residency+"0").click()

			if applicant_one_empstatus == "Employed":
				status = "Employed"
			elif applicant_one_empstatus == "Self Employed (Sole Trader/Partnership)":
				status = "Self-employed"
			elif applicant_one_empstatus == "Retired":
				status = "Retired"
			elif applicant_one_empstatus == "Not Working":
				status = "Not Employed"
			else:
				status = "On Contract"
			
			driver.find_element(By.CSS_SELECTOR, "#Employment0").send_keys(status)

			if status == "Self-employed":
				self_income_last_year = driver.find_element(By.CSS_SELECTOR, "#Applicant0_NetProfitMostRecent")
				self_income_last_year.clear()
				self_income_last_year.send_keys(str(self_income_last_year_1))

				self_income_previous_year = driver.find_element(By.CSS_SELECTOR, "#Applicant0_NetProfitNextMostRecent")
				self_income_previous_year.clear()
				self_income_previous_year.send_keys(str(self_income_previous_year_1))
			else:
				grossAnnual = driver.find_element(By.CSS_SELECTOR, "#Applicant0_GrossAnnual")
				grossAnnual.clear()
				grossAnnual.send_keys(str(basic_annual_income1))

				if status == "Employed":
					Overtime = driver.find_element(By.CSS_SELECTOR, "#Applicant0_OvertimeAnnual")
					Overtime.clear()
					Overtime.send_keys(overtime1)

			if num_of_applicants>1:
				driver.find_element(By.CSS_SELECTOR, "#Age1").send_keys(str(applicant_two_age))

				if applicant_two_empstatus == "Employed":
					status = "Employed"
				elif applicant_two_empstatus == "Self Employed (Sole Trader/Partnership)":
					status = "Self-employed"
				elif applicant_two_empstatus == "Retired":
					status = "Retired"
				elif applicant_two_empstatus == "Not Working":
					status = "Not Employed"
				else:
					status = "On Contract"
				
				emp_status2 = driver.find_element(By.CSS_SELECTOR, "#Employment1")
				emp_status2.send_keys(status)

				if status == "Self-employed":
					self_income_last_year = driver.find_element(By.CSS_SELECTOR, "#Applicant1_NetProfitMostRecent")
					self_income_last_year.clear()
					self_income_last_year.send_keys(str(self_income_last_year_2))

					self_income_previous_year = driver.find_element(By.CSS_SELECTOR, "#Applicant1_NetProfitNextMostRecent")
					self_income_previous_year.clear()
					self_income_previous_year.send_keys(str(self_income_previous_year_2))
				else:
					grossAnnual = driver.find_element(By.CSS_SELECTOR, "#Applicant1_GrossAnnual")
					grossAnnual.clear()
					grossAnnual.send_keys(str(basic_annual_income2))

					if status == "Employed":
						Overtime = driver.find_element(By.CSS_SELECTOR, "#Applicant1_OvertimeAnnual")
						Overtime.clear()
						Overtime.send_keys(overtime2)

			driver.find_element(By.CSS_SELECTOR, ".button.continuebtnXX input[type='submit']").click()
		except Exception as e:
			print(f"Error: {e}")

		try:
			driver.find_element(By.CSS_SELECTOR, "#detailedFormExpanded1").click()

			driver.find_element(By.CSS_SELECTOR, "#totalExpenditure").send_keys(str(sum_household_expenses))
			driver.find_element(By.CSS_SELECTOR, "#monthlyGroundRent").send_keys(str(rent))
			driver.find_element(By.CSS_SELECTOR, "#monthlyServiceCharge").send_keys(str(serviceCharge))
			driver.find_element(By.CSS_SELECTOR, "#childcareEducation").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#maintenanceCSA").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#currentCardDebt").send_keys(str(credit))
			driver.find_element(By.CSS_SELECTOR, "#cardDebtToRemain").send_keys(str(credit))
			driver.find_element(By.CSS_SELECTOR, "#currentMonthlyLoanPayments").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#monthlyLoanToRemain").send_keys("0")

			driver.find_element(By.CSS_SELECTOR, ".button.continuebtnXX input[type='submit']").click()
		except Exception as e:
			print(f"Error: {e}")

		try:
			max_affordable_element = WebDriverWait(driver, 10).until(
				EC.presence_of_element_located((By.XPATH, "//div[@class='results']//strong"))
			)
			max_affordable_value = max_affordable_element.text
			print(f"Max Affordable: {max_affordable_value}")
			driver.close()
		except Exception as e:
			print(f"Error: {e}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)