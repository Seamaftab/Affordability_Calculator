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

	current_credit_balance1 = 0
	current_credit_balance2 = 0

	location = data["Property Details"].get("Property Location")
	property_type = data["Property Details"].get("Property Type")
	property_age = data["Property Details"].get("Property Age", 0)

	expenses = data["Client Details"][0].get("Outgoings", [])
	groceries = expenses.get("Living Costs", {}).get("Groceries", 0)
	council_tax = expenses.get("Household", {}).get("Council Tax", 0)
	transport = 0 if expenses.get("Transport") in null else expenses.get("Transport", 0)

	if Payment_Method == "Interest Only":
		if num_of_applicants==1:
			if basic_annual_income1<75000:
				print("Max Affordable : £0.\n")
				print("Interest only mortgages require a minimum gross income of £75,000 for a single applicant or £100,000 for a joint application where no individual earns in excess of £75,000.\n")

		else:
			if basic_annual_income1+basic_annual_income2<100000:
				print("Max Affordable : £0.\n")
				print("Interest only mortgages require a minimum gross income of £75,000 for a single applicant or £100,000 for a joint application where no individual earns in excess of £75,000.\n")

	else:
		service = Service(executable_path="chromedriver.exe")
		driver = webdriver.Chrome(service=service)
		driver.get("https://resources.barclays.co.uk/mortgage-calculators/residential-affordability")

		try:
			ApplicationType = "NewHome" if Loan_Type == "Purchase" else "Remortgage"
			apptype = Select(driver.find_element(By.CSS_SELECTOR, "#ApplicationType"))
			apptype.select_by_value(ApplicationType)

			if Mortgage_Type == "Standard Residential":
				m_type = "SM"
			elif Mortgage_Type == "Shared Ownership":
				m_type = "SO"
			else:
				m_type = "HTB"
			
			mort_type = Select(driver.find_element(By.CSS_SELECTOR, "#MortgageType"))
			mort_type.select_by_value(m_type)

			if m_type == "HTB":
				if location == "England":
					HTBLocation = "England"
				elif location == "Scotland":
					HTBLocation = "Scotland"
				elif location == "Wales":
					HTBLocation = "Wales"
				else:
					HTBLocation = "London"

				HTB = Select(driver.find_element(By.CSS_SELECTOR, "#HelpToBuyScheme"))
				HTB.select_by_value(HTBLocation)

			# if ApplicationType == "Remortgage":
			# 	driver.find_element(By.CSS_SELECTOR, "#BorrowMoreMoney")
			# 	driver.find_element(By.CSS_SELECTOR, "#AdditionalBorrowingReason")
			# 	driver.find_element(By.CSS_SELECTOR, "#DebtConsolidation")

			proptype = "True" if property_type == "Flat" or property_type == "Maisonette" else "False" 
			flat = Select(driver.find_element(By.CSS_SELECTOR, "#IsFlatOrMaisonette"))
			flat.select_by_value(proptype)

			if location == "Northern Ireland":
				prop_loc = "Northern Ireland"
			elif location == "England":
				prop_loc = "England"
			elif location == "Wales":
				prop_loc = "Wales"
			else:
				prop_loc = "Scotland"

			if m_type != "HTB":
				property_place =Select(driver.find_element(By.CSS_SELECTOR, "#PropertyLocation"))
				property_place.select_by_value(prop_loc)
			else:
				driver.find_element(By.CSS_SELECTOR, "#NewBuild").click()
			if property_age <= 24:
				driver.find_element(By.CSS_SELECTOR, "#NewBuild").click()

			driver.find_element(By.CSS_SELECTOR, "#PropertyValue").send_keys(str(Purchase_Price))
			driver.find_element(By.CSS_SELECTOR, "#ProductFee").send_keys("0")
			if m_type == "SE" or m_type == "HTB":
				driver.find_element(By.CSS_SELECTOR, "#EquityLoanPercentage").send_keys("1")
				if m_type == "SE":
					selr = driver.find_element(By.CSS_SELECTOR, "#SharedEquityLoanRateIsHigher")
					if selr.click():
						driver.find_element(By.CSS_SELECTOR, "#SharedEquityLoanRatePc")
			if m_type == "SO":
				driver.find_element(By.CSS_SELECTOR, "#SharedOwnershipPercentage").send_keys(str(share))
			if m_type == "SM":
				parts_of_mortgage = Select(driver.find_element(By.CSS_SELECTOR, "#NoOfMortgageParts"))
				parts_of_mortgage.select_by_value("1")

				is_interest_only = "True" if Payment_Method == "Interest Only" else "False"
				repayment_type = Select(driver.find_element(By.CSS_SELECTOR, "#MortgageParts_0__InterestOnly"))
				repayment_type.select_by_value(is_interest_only)

			driver.find_element(By.CSS_SELECTOR, "#MortgageParts_0__Amount").send_keys(str(loan_amount))
			driver.find_element(By.CSS_SELECTOR, "#MortgageParts_0__Rate").send_keys("0")

			driver.find_element(By.CSS_SELECTOR, "#MortgageParts_0__TermYears").send_keys(str(Loan_Term))
			driver.find_element(By.CSS_SELECTOR, "#MortgageParts_0__TermMonths").send_keys(str(loan_term_months))

			applicant_number = Select(driver.find_element(By.CSS_SELECTOR, "#NoOfApplicants"))
			applicant_number.select_by_value(str(num_of_applicants))
			driver.find_element(By.CSS_SELECTOR, "#NoOfDependants").send_keys(str(num_of_dependants))

			# driver.find_element(By.CSS_SELECTOR, "#PremierOrWealthCustomer").click()
		except Exception as e:
			print(f"Error: {e}")

		try:
			if applicant_one_empstatus == "Not Working" or applicant_one_empstatus == "Retired":
				driver.find_element(By.CSS_SELECTOR, "#Applicants_0__IsEmployed").click()
			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__EmployedBasicIncome").send_keys(str(basic_annual_income1))
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__EmployedBonusCurrent").send_keys(str(bonus1))
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__EmployedBonusPrevious").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__EmployedMonthlySustainableAllowances").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__EmployedMonthlyOvertime").send_keys(str(overtime1))
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__EmployedMonthlyCommission").send_keys(str(commision1))
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__EmployedMonthlyBonus").send_keys(str(bonus1/12))
			
			if self_income_last_year_1 > 0:
				driver.find_element(By.CSS_SELECTOR, "#Applicants_0__IsSelfEmployed").click()
				driver.find_element(By.CSS_SELECTOR, "#Applicants_0__SelfEmployedIncomeCurrent").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_0__SelfEmployedIncomePrevious").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_0__NonTaxableIncome").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_0__PensionIncome").send_keys("0")

			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__CreditCardBalance").send_keys(str(current_credit_balance1))
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__OverdraftBalanceRemaining").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__OtherMonthlyCreditCommitments").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__ServiceCharges").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__ChildCare").send_keys("0")
			driver.find_element(By.CSS_SELECTOR, "#Applicants_0__OtherMonthlyCommitments").send_keys("0")

			if num_of_applicants>1:
				if applicant_two_empstatus == "Not Working" or applicant_two_empstatus == "Retired":
					driver.find_element(By.CSS_SELECTOR, "#Applicants_1__IsEmployed").click()

				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__EmployedBasicIncome").send_keys(str(basic_annual_income2))
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__EmployedBonusCurrent").send_keys(str(bonus2))
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__EmployedBonusPrevious").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__EmployedMonthlySustainableAllowances").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__EmployedMonthlyOvertime").send_keys(str(overtime2))
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__EmployedMonthlyCommission").send_keys(str(commision2))
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__EmployedMonthlyBonus").send_keys(str(bonus1/12))

				if self_income_last_year_2 > 0:
					driver.find_element(By.CSS_SELECTOR, "#Applicants_1__IsSelfEmployed").click()
					driver.find_element(By.CSS_SELECTOR, "#Applicants_1__SelfEmployedIncomeCurrent").send_keys("0")
					driver.find_element(By.CSS_SELECTOR, "#Applicants_1__SelfEmployedIncomePrevious").send_keys("0")
					driver.find_element(By.CSS_SELECTOR, "#Applicants_1__NonTaxableIncome").send_keys("0")
					driver.find_element(By.CSS_SELECTOR, "#Applicants_1__PensionIncome").send_keys("0")

				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__CreditCardBalance").send_keys(str(current_credit_balance2))
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__OverdraftBalanceRemaining").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__OtherMonthlyCreditCommitments").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__ServiceCharges").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__ChildCare").send_keys("0")
				driver.find_element(By.CSS_SELECTOR, "#Applicants_1__OtherMonthlyCommitments").send_keys("0")
		except Exception as e:
			print(f"Error: {e}")

		try:
			#Other Mortgages
			if existing_mortgage_amount>0:
				Residential_Mortgage = Select(driver.find_element(By.CSS_SELECTOR, "#NoOfResidentialMortgages"))
				Residential_Mortgage.select_by_value("1")

				driver.find_element(By.CSS_SELECTOR, "#ResidentialMortgages_0__Amount").send_keys(str(existing_mortgage_amount))
				driver.find_element(By.CSS_SELECTOR, "#ResidentialMortgages_0__Rate").send_keys("1")
				driver.find_element(By.CSS_SELECTOR, "#ResidentialMortgages_0__TermYears").send_keys("1")
				driver.find_element(By.CSS_SELECTOR, "#ResidentialMortgages_0__TermMonths").send_keys("1")
			else:
				Residential_Mortgage = Select(driver.find_element(By.CSS_SELECTOR, "#NoOfResidentialMortgages"))
				Residential_Mortgage.select_by_value("0")

			btl_Mortgage = Select(driver.find_element(By.CSS_SELECTOR, "#NoOfBtlMortgages"))
			btl_Mortgage.select_by_value("0")

			ptl_Mortgage = Select(driver.find_element(By.CSS_SELECTOR, "#NoOfPtlMortgages"))
			ptl_Mortgage.select_by_value("0")

			driver.find_element(By.CSS_SELECTOR ,"#BtlPtlMonthlyMortgagePayments").send_keys("0")

			time.sleep(1)
			driver.find_element(By.CSS_SELECTOR, "#btnCalculate").click()
			# time.sleep(10)
		except Exception as e:
			print(f"Error: {e}")

		try:
			max_affordable = driver.find_element(By.CSS_SELECTOR, ".row .col-md-12 p b").text
			print("Max Affordable : ",max_affordable)
		except Exception as e:
			print(f"Error: {e}")
			input("Press Any Key : ")
		driver.close()

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)
# main()
