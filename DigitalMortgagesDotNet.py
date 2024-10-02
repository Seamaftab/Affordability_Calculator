import requests
import json

url = 'https://www.digitalmortgages.net/affordability/'

def get_mortgage_data(data):
    mortgage_data = {}
    mortgage_data["property_value"] =  data["Mortgage Requirement"].get("Purchase Price", 0)
    mortgage_data["loan_amount"] = data["Mortgage Requirement"].get("Loan Amount", 0)
    mortgage_data["loan_term_years"] = int(data["Mortgage Requirement"].get("Loan Term") / 12)
    mortgage_data["loan_term_months"] = int(data["Mortgage Requirement"].get("Loan Term") % 12)
    mortgage_data["loan_term"] = data["Mortgage Requirement"].get("Loan Term", 0)
    mortgage_data["current_postcode"] = data["Property Details"]["Property Details"].get("Post Code", 0)
    return mortgage_data

def get_applicants_data(data):
    client_info = []
    num_of_dependants = 0
    client_details = data.get("Client Details", [])
    for client in client_details:
        num_of_dependants += len(client["dependants"])
        _data = {
            "income": [
                {
                    "employment_status": client["Employment Details"]['Employment Status'],
                    "is_main_job": "Yes",
                    "guaranteed_bonus": client["Additional Income (Annual)"]['Regular Bonus'],
                    "non_guaranteed_bonus": client["Additional Income (Annual)"]['Irregular Overtime'],
                    "allowances": 0,
                    "employment_start_date": "01/01/2022",
                    "gross_basic_income": client["Employment Details"]['Basic Annual Income']
                }
            ],
            "date_of_birth": client['Date of Birth'],
            "expected_retirement_age": client['expected retirement age']
        }
        client_info.append(_data)
    return client_info, num_of_dependants

def construct_payload(data):
    mortgage_data = get_mortgage_data(data)
    applicant_data, num_of_dependants = get_applicants_data(data)

    payload = {
        "number_of_adult_dependents": 0,
        "number_of_child_dependents": num_of_dependants,
        "monthly_expenditures": {
            "credit_cards": {
                "current_balance": sum([x.get("Credit Commitments", 0) for x in applicant_data]),
                "current_monthly_payment": 0
            },
            "personal_loans": {
                "current_monthly_payment": 0
            },
            "secured_loans_monthly_payment": 0,
            "child_maintenance": 0,
            "student_loans": 0,
            "other_mortgages": 0
        },
        "household_expenditures": {
            "property": 0,
            "council_tax": 0,
            "ground_rent": 0,
            "buildings_insurance": 0,
            "utilities": 0
        },
        "other_expenditures": {
            "childcare": 0,
            "school_fees": 0,
            "essential_travel": 100,
            "housekeeping": 0,
            "mobile_and_broadband": 200,
            "other_insurance": 0,
            "other_outgoings": 0
        },
        "loan_term": mortgage_data["loan_term"]
    }

    payload.update(mortgage_data)
    payload["applicants"] = applicant_data
    return payload

def main():
    with open(config) as file:
        data = json.load(file)
    payload = construct_payload(data)

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        response_json = response.json()
        print(f"Response : {response_json}")
    elif response.status_code == 429:
        response = requests.post(url, payload)
        print(f"429")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Error message: {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
	main()