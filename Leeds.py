import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup

url = "https://affordability-calculator.leedsbuildingsociety.co.uk/AffordabilityCalculatorOnline/"
req_cookies = None
request_verification_token = ""

def get_mortgage_data(data):
    global request_verification_token
    mortgage_data = {}
    applicants, num_of_dependants = get_applicants(data)
    num_of_dependants = 0

    mortgage_data["__RequestVerificationToken"] = request_verification_token 
    mortgage_data["Lending_Segment"] = "STDRES" if data["Mortgage Requirement"].get("Mortgage Type") == "Standard Residential" else "BTOLET"
    mortgage_data["Rio_Lending_Segment"] = False
    mortgage_data["LettingType"] = "" if data["Mortgage Requirement"].get("Mortgage Type") == "Standard Residential" else 1
    mortgage_data["AdditionalMoniesRequired"] = False if data["Mortgage Requirement"].get("Mortgage Type") == "Standard Residential" else True

    property_location = data["Property Details"].get("Property Location")
    if property_location == "England":
        mortgage_data["PropertyIn"] = "ENGLND"
    elif property_location == "Scotland":
        mortgage_data["PropertyIn"] = "SCTLND"
    elif property_location == "Northern Ireland":
        mortgage_data["PropertyIn"] = "NIRELD"
    else:
        mortgage_data["PropertyIn"] = "WALES"

    mortgage_data["Number_Of_Applicants"] = data.get("No of Applicant", 0)
    mortgage_data["FirstTimeBuyers"] = "Yes" if data["Client Details"][0].get("Applicant Type") == "First Time Buyer" else "No"
    mortgage_data["Financially_Dependant_Adults_18_And_Over"] = num_of_dependants
    mortgage_data["Number_Of_Children"] = 0

    MType = data["Mortgage Requirement"].get("Payment Method")
    if MType == "Repayment":
        mortgage_data["MortgageType"] = "repayment"
    elif MType == "Part and Part":
        mortgage_data["MortgageType"] = "part"
    else:
        mortgage_data["MortgageType"] = "interest"

    mortgage_data["SharedOwnership"] = "SHARE" if data["Mortgage Requirement"].get("Mortgage Type") == "Shared Ownership" else "q"
    mortgage_data["Borrowing_Amount_Repayment"] = data["Mortgage Requirement"].get("Loan Amount", 0)
    mortgage_data["Borrowing_Amount_Interest_Only"] = ""
    mortgage_data["Repayment_Period_Years"] = int(data["Mortgage Requirement"].get("Loan Term") / 12)
    mortgage_data["Repayment_Period_Months"] = int(data["Mortgage Requirement"].get("Loan Term") % 12)
    mortgage_data["Purchase_Price"] = data["Mortgage Requirement"].get("Purchase Price", 0)
    mortgage_data["PropertyType"] = 1

    if 0 < data["Property Details"].get("Property Age") <= 48:
        mortgage_data["PropertyAge"] = 2020
    elif data["Property Details"].get("Property Age") > 48:
        mortgage_data["PropertyAge"] = 2019
    else:
        mortgage_data["PropertyAge"] = 0

    mortgage_data["Expected_montly_rental_income"] = ""
    mortgage_data["Rental_Income_Tax_Band"] = ""
    mortgage_data["accordion-block-toggle"] = "on"
    mortgage_data["Equity_loan_provided_by_3rd_party"] = ""
    mortgage_data["Monthly_maintenance_charge"] = 0

    return mortgage_data


def get_applicants(data):
	applicant_data = {}
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])

	for i, applicant in enumerate(applicant_details):
		num_of_dependants += len(applicant.get("dependants"))
		e_details = applicant.get("Employment Details", [])
		leed = {
			f"Applicant{i+1}.Existing_Properties_For_Applicant.Exisiting_Property_1_Second_Home": "No",
			f"Applicant{i+1}.Existing_Properties_For_Applicant.Existing_Property_1_Property_to_be_retained_balance": "",
			f"Applicant{i+1}.Existing_Properties_For_Applicant.Existing_Property_1_Property_to_be_retained_Outstanding_term_years": "",
			f"Applicant{i+1}.Existing_Properties_For_Applicant.Existing_Property_1_Property_to_be_retained_Outstanding_term_months": "",
			f"Applicant{i+1}.Existing_Properties_For_Applicant.Total_value_of_finance_on_rental_properties": 0,
			f"Applicant{i+1}.Financial_Commitments.Outstanding_Debt_Balance": 0,
			f"Applicant{i+1}.Financial_Commitments.Fixed_Term_Accounts_Total_Monthly_Payment": 0,
			f"Applicant{i+1}.Expenditure_For_Applicant.Third_Party_Maintenance_Payments": 0,
			f"Applicant{i+1}.Expenditure_For_Applicant.School_Fees_Monthly_Payment": 0,
			f"Applicant{i+1}.Expenditure_For_Applicant.Total_Monthly_Cost_Other_Material_Expenditure": 0,
			f"Applicant{i+1}.Employed.Annual_Gross_Basic_Income": e_details.get("Basic Annual Income", 0),
			f"Applicant{i+1}.Employed.Annual_Bonus_Guaranteed": applicant["Additional Income (Annual)"].get("Regular Bonus", 0),
			f"Applicant{i+1}.Employed.Annual_Bonus_Non_Guaranteed": 0,
			f"Applicant{i+1}.Employed.Annual_Overtime_Guaranteed": applicant["Additional Income (Annual)"].get("Irregular Overtime", 0),
			f"Applicant{i+1}.Employed.Annual_Overtime_Non_Guaranteed": 0,
			f"Applicant{i+1}.Employed.Annual_Shift_Allowance_Guaranteed": 0,
			f"Applicant{i+1}.Employed.Annual_Shift_allowance_Non_Guaranteed": 0,
			f"Applicant{i+1}.Employed.Annual_Dividends": 0,
			f"Applicant{i+1}.Employed.Annual_Car_Allowance": 0,
			f"Applicant{i+1}.Employed.Gross_Annual_Commission": 0,
			f"Applicant{i+1}.Employed.Annual_Mortgage_Subsidy": 0,
			f"Applicant{i+1}.Employed.Annual_Rent_Allowance": 0,
			f"Applicant{i+1}.Employed.Annual_Town_Allowance": 0,
			"businessEstablishedMonthDD": 0,
			"business_established_yearsTB": 0,
			f"Applicant{i+1}.Self_Employed.Business_Established_Years": 0,
			f"Applicant{i+1}.Self_Employed.Personal_Profit_Latest_Year": 0,
			f"Applicant{i+1}.Self_Employed.Salary_Latest_Year": e_details.get("Last Year's Salary", 0),
			f"Applicant{i+1}.Self_Employed.Dividends_Latest_Year": e_details.get("Last Year's Dividends", 0),
			f"Applicant{i+1}.Self_Employed.Personal_Profit_Previous_Year": e_details.get("Last Year's Net Profits", 0),
			f"Applicant{i+1}.Self_Employed.Salary_Previous_Year": e_details.get("Previous Year's Salary", 0),
			f"Applicant{i+1}.Self_Employed.Dividends_Previous_Year": e_details.get("Previous Year's Dividends", 0),
			f"Applicant{i+1}.Self_Employed.Personal_Profit_2_Years_Ago": e_details.get("Previous Year's Net Profits", 0),
			f"Applicant{i+1}.Self_Employed.Salary_2_Years_Ago": e_details.get("3rd Year's Salary", 0),
			f"Applicant{i+1}.Self_Employed.Dividends_2_Years_Ago": e_details.get("3rd Year's Dividends", 0),
			f"Applicant{i+1}.Self_Employed_Contractor.Gross_Annual_Income_Contracted": 0,
			f"Applicant{i+1}.Other.Maintenance_Annual_Amount": 0,
			f"Applicant{i+1}.Other.Net_Property_Rental_Income": 0,
			f"Applicant{i+1}.Other.Extra_Income_Type_Working_Tax_Credit": 0,
			f"Applicant{i+1}.Other.Savings_Or_Investment": 0,
			f"Applicant{i+1}.Other.Annual_Pension": 0,
			f"Applicant{i+1}.Other.Disability_Allowance": 0,
			f"Applicant{i+1}.Other.Extra_Income_Amount": 0,
			f"Applicant{i+1}.Other.Extra_Income_Type_Child_Tax_Credit": 0
		}

		applicant_data.update(leed)
		
	return applicant_data, num_of_dependants		  

def get_payload(data):
	mortgages = get_mortgage_data(data)
	applicants, num_of_dependants = get_applicants(data)

	payload = mortgages
	payload.update(applicants)

	return payload

headers = {
	"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
	"Accept-Encoding": "gzip, deflate, br",
	"Accept-Language": "en-US,en;q=0.9,bn;q=0.8,mt;q=0.7",
	"Cache-Control": "max-age=0",
	"Connection": "keep-alive",
	"Content-Type": "application/x-www-form-urlencoded",
	"DNT": "1",
	"Host": "affordability-calculator.leedsbuildingsociety.co.uk",
	"Origin": "https://affordability-calculator.leedsbuildingsociety.co.uk",
	"Referer": "https://affordability-calculator.leedsbuildingsociety.co.uk/AffordabilityCalculatorOnline",
	"Sec-Fetch-Dest": "document",
	"Sec-Fetch-Mode": "navigate",
	"Sec-Fetch-Site": "same-origin",
	"Sec-Fetch-User": "?1",
	"Upgrade-Insecure-Requests": "1",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def get_request_verification_token():
    global req_cookies
    res = requests.get("https://affordability-calculator.leedsbuildingsociety.co.uk/AffordabilityCalculatorOnline/", headers=headers)
    req_cookies = res.cookies
    soup = BeautifulSoup(res.content, features="lxml")
    request_verification_token = soup.select_one('[name="__RequestVerificationToken"]')["value"]
    return request_verification_token

def main():
    global request_verification_token, req_cookies

    with open(config) as file:
        data = json.load(file)
    if not request_verification_token:
        request_verification_token = get_request_verification_token()

    payload = get_payload(data)
    
    response = requests.request("POST", url, headers=headers, data=payload, cookies=req_cookies)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features="lxml")
        max_borrowing_element = soup.select_one('#maxBorrowingMax')
        if max_borrowing_element:
            max_borrowing = max_borrowing_element.text
            print("Response : ACCEPTED\nmax_borrowing:", max_borrowing,"\n")
        else:
            print("Response : DECLINED\n")
    elif response.status_code == 429:
        response = requests.post(url, payload)
        print(f"429")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Error message: {response.text}")


config_files = [
    "config_one.json", "config_two.json", "config_three.json",
    "config_four.json", "config_five.json", "config_six.json",
    "config_seven.json"
]
for config in config_files:
    main()

