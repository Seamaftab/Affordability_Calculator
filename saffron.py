import json
from bs4 import BeautifulSoup
import requests
import urllib.parse

url = "https://www.saffronforintermediaries.co.uk/form/affordability-calculator?ajax_form=1&_wrapper_format=drupal_ajax"

headers = {
    "Accept":"application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding":"gzip, deflate, br, zstd",
    "Accept-Language":"en-US,en;q=0.9,bn;q=0.8",
    "Content-Type":"application/x-www-form-urlencoded; charset=UTF-8",
    "Host":"www.saffronforintermediaries.co.uk",
    "Origin":"https://www.saffronforintermediaries.co.uk",
    "Referer":"https://www.saffronforintermediaries.co.uk/form/affordability-calculator",
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_applicants(data):
    applicant_info = {}
    num_of_dependants = 0
    applicant_details = data.get("Client Details", [])
    applicant_one = applicant_details[0]
    applicant_two = applicant_details[1] if len(applicant_details) > 1 else {}

    # for i, applicant in enumerate(applicant_details):
    num_of_dependants += len(applicant_one.get("dependants", [])) + len(applicant_two.get("dependants", []))
    if num_of_dependants == 0:
        num_of_dependants =  1
    applicant_one_empstatus= applicant_one["Employment Details"].get("Employment Status")
    applicant_one_credit = applicant_one["Outgoings"].get("Credit Commitments")
    
    applicant_two_empstatus= applicant_two.get("Employment Details", {}).get("Employment Status", 0)
    applicant_two_credit = applicant_two.get("Outgoings", {}).get("Credit Commitments", 0)

    
    applicants_data = { 
        "employment_type" : 0 if applicant_one_empstatus == "Employed" else 1,
        "base_salary" : applicant_one["Employment Details"].get("Basic Annual Income", 0),
        "base_salary_year_one" : 0,
        "base_salary_year_two" : 0,
        "base_salary_year_three" : 0,
        "pension" : 0,
        "overtime" : applicant_one["Additional Income (Annual)"].get("Irregular Overtime", 0),
        "bonus" : applicant_one["Additional Income (Annual)"].get("Regular Bonus", 0),
        "allowances" : 0,
        "other_income":0,
        "investment_or_rental":0,
        "student_loan":0,
        "credit_card_balance":0 if applicant_one_credit in ["null", None] else applicant_one_credit,
        "hire_purchase":0,
        "child_maintenance":0,
        "school_fees":0,
        "healthcare_costs":0,
        "other_costs":0,
        "employment_type_2": 0 if applicant_two_empstatus == "Employed" else 1,
        "base_salary_2": applicant_two.get("Employment Details", {}).get("Basic Annual Income", 0),
        "base_salary_year_one_2":0,
        "base_salary_year_two_2":0,
        "basic_salary_year_three_2":0,
        "pension_2":0,
        "overtime_2":0,
        "bonus_2":0,
        "allowances_2":0,
        "other_income_2":0,
        "investment_or_rental_2":0,
        "student_loan_2":0,
        "credit_card_balance_2":0 if applicant_two_credit in ["null", None] else applicant_two_credit ,
        "hire_purchase_2":0,
        "child_maintenance_2":0,
        "school_fees_2":0,
        "healthcare_costs_2":0,
        "other_costs_2":0
    }

    applicant_info.update(applicants_data)

    applicant_info["form_build_id"] = "form-OhsPTxpGPaLnDJ3OMFc6jt-6wBRliQYMQaqRCQslzhQ"
    applicant_info["form_id"] = "webform_submission_affordability_calculator_add_form"
    applicant_info["url"] = ""
    applicant_info["_triggering_element_name"] = "op"
    applicant_info["_triggering_element_value"] = "Submit"
    applicant_info["_drupal_ajax"] = 1
    applicant_info["ajax_page_state[theme]"] = "sbs"
    applicant_info["ajax_page_state[theme_token]"] = ""
    applicant_info["ajax_page_state[libraries]"] = "core/internal.jquery.formsbs/globalsbs/webform_printsystem/baseviews/views.modulewebform/webform.ajaxwebform/webform.element.details.savewebform/webform.element.details.togglewebform/webform.element.helpwebform/webform.element.messagewebform/webform.element.selectwebform/webform.form"

    return applicant_info, num_of_dependants


def get_mortgage_data(data, num_of_dependants):
    mortgage_data = {}

    mortgage_data["applicants"]=data.get("No of Applicant")
    mortgage_data["dependants"]=num_of_dependants

    if data["Mortgage Requirement"].get("Payment Method") == "Repayment":
        mortgage_data["repayment_type"] = "CR"
    elif data["Mortgage Requirement"].get("Payment Method") == "Interest Only":
        mortgage_data["repayment_type"] = "IO"
    else:
        mortgage_data["repayment_type"] = "PP"

    mortgage_data["loan_interest_only"] = 0
    mortgage_data["term_in_years"] = int(data["Mortgage Requirement"].get("Loan Term")/12)
    mortgage_data["loan_amount"] = data["Mortgage Requirement"].get("Loan Amount")
    mortgage_data["property_value"] = data["Mortgage Requirement"].get("Purchase Price", 0)
    mortgage_data["interest_rate"] = 1
    mortgage_data["fix"] = 1

    return mortgage_data

def get_payload(data):
    applicants, num_of_dependants = get_applicants(data)
    mortgages = get_mortgage_data(data, num_of_dependants)

    json_payload = mortgages
    json_payload.update(applicants)
    payload = urllib.parse.urlencode(json_payload)
    return payload

def main(config_file):
    with open(config_file) as file:
        data = json.load(file)
    payload = get_payload(data)

    response = requests.post(url, data=payload, headers=headers)

    data_to_return = {
        "result": None,
        "max_affordable_loan" : None,
        "remarks": ""
    }
   
    response_json = response.json()
    print(config_file, response_json)
    if response.status_code == 200:
        try:
            raw_html = [x for x in response_json if x["command"] == "insert"][0]["data"]
            soup = BeautifulSoup(raw_html, 'html.parser')
            maximum_affordable_loan_amount = soup.select_one('.webform-confirmation__message h2').text.split(': ')[-1]
            data_to_return["max_affordable_loan"] = maximum_affordable_loan_amount
            data_to_return["result"] = "Pass"
        except:
            data_to_return["remarks"] = "Something went wrong. Please try again"
    else:
        data_to_return["remarks"] = "Request failed, status: {}".format(response.status_code)
    
    return data_to_return

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
    print(main(config_file))
