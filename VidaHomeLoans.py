import requests
import json

url = 'https://www.vidahomeloans.co.uk/fresihtbcalculator'

def get_mortgage_data(data):
   mortgage_data ={}
   property_location = data["Property Details"].get("Property Location")
   applicants, num_of_dependants = get_applicants(data)

   mortgage_data["calculatorTypeId"] = "1"
   mortgage_data["termsAccepted"] = True
   mortgage_data["applicantsCount"] = data.get("No of Applicant") if data.get("No of Applicant") in [1,2] else 1
   mortgage_data["financialDependantsCount"] = num_of_dependants + 1
   mortgage_data["existingMortgageBalance"] = ""
   mortgage_data["existingMortgageRepayments"] = ""
   mortgage_data["mortgageTermYears"] = int(data["Mortgage Requirement"].get("Loan Term")/12)
   mortgage_data["mortgageTermMonths"] =  int(data["Mortgage Requirement"].get("Loan Term")%12)
   mortgage_data["initialRateTypeId"] = 1
   mortgage_data["interestOnlyAmount"] = ""

   if property_location == "Northern Ireland":
      mortgage_data["propertyRegion"] = "11"
   elif property_location == "England":
      mortgage_data["propertyRegion"] = "6"
   elif property_location == "Wales":
      mortgage_data["propertyRegion"] = "10"
   elif property_location == "Scotland":
      mortgage_data["propertyRegion"] = "12"
   else:
      mortgage_data["propertyRegion"] = "1"

   mortgage_data["requestedLoanAmount"] = data["Mortgage Requirement"].get("Loan Amount", 0)
   mortgage_data["selectedProduct"] = 1
   if data["Mortgage Requirement"].get("Product term") == 60:
      mortgage_data["rateTerm"] = 2
   else:
      mortgage_data["rateTerm"] = 1
   mortgage_data["productSelectedInitialRate"] = 2
   mortgage_data["rentalTopUp"] = ""

   if data["Mortgage Requirement"].get("Payment Method") == "Repayment":
      mortgage_data["repaymentMethod"] = 1
   else:
      mortgage_data["repaymentMethod"] = 2

   return mortgage_data

def get_applicants(data):
    applicant_data = []
    num_of_dependants = 0

    for applicant in data.get("Client Details", []):
        num_of_dependants += len(applicant["dependants"])

        employment_status = applicant["Employment Details"].get("Employment Status")

        if employment_status == "Employed":
            employmentStatus = 1
            currently_retired = 1
            share_of_net_profits = 0
        elif employment_status in ["Self Employed (Sole Trader/Partnership)", "Self Employed (Ltd Company/Director)"]:
            employmentStatus = 2
            currently_retired = 1
            share_of_net_profits = applicant["Employment Details"].get("Last Year's Net Profits", 0)
        else:
            employmentStatus = 3
            share_of_net_profits = 0
            currently_retired = 2 if employment_status == "Retired" else 1

        household = sum(int(value) for value in applicant["Outgoings"]["Household"].values() if str(value).isdigit())
        living_costs = sum(int(value) for value in applicant["Outgoings"]["Living Costs"].values() if str(value).isdigit())

        vida = {
            "employmentStatus": employmentStatus,
            "income1": applicant["Employment Details"].get("Basic Annual Income"),
            "income2": applicant["Additional Income (Annual)"].get("Irregular Overtime", 0),
            "income3": 0,
            "shareOfNetProfits": share_of_net_profits,
            "monthlyExpenditure": household + living_costs,
            "monthlyCreditCommitments": 0 if applicant["Outgoings"].get("Credit Commitments") in ["null", None] else applicant["Outgoings"].get("Credit Commitments"),
            "postRetirementIncome": 0,
            "currentlyRetired": currently_retired
        }

        applicant_data.append(vida)

    return applicant_data, num_of_dependants

def get_payload(data):
   applicants, num_of_dependants = get_applicants(data)
   mortgages = get_mortgage_data(data)

   payload = {
      "applicantsCountOptions": [1, 2],
      "rateTermOptions": [
         { "id": 2, "name": "2" },
         { "id": 5, "name": "5 / 7" }
      ],
      "customerTypeOptions": [
         { "id": 1, "name": "Limited Company" },
         { "id": 2, "name": "Limited Liability Partnership" },
         { "id": 3, "name": "Partnership" },
         { "id": 4, "name": "Individual" },
         { "id": 5, "name": "Special Purpose Vehicle" }
      ],
      "financialDependantsCountOptions": [
         { "id": 1, "name": "0" },
         { "id": 2, "name": "1" },
         { "id": 3, "name": "2" },
         { "id": 4, "name": "3" },
         { "id": 5, "name": "4" },
         { "id": 6, "name": "5" },
         { "id": 7, "name": "6" }
      ],
      "currentlyRetiredOptions": [
         { "id": 2, "name": "Yes" },
         { "id": 1, "name": "No" }
      ],
      "htbApplicationOptions": [
         { "id": 2, "name": "Yes" },
         { "id": 1, "name": "No" }
      ],
      "repaymentMethodOptions": [
         { "id": 1, "name": "Repayment" },
         { "id": 2, "name": "Interest Only" }
      ],
      "propertyRegionOptions": [
         { "id": "", "name": "" },
         { "id": 1, "name": "Unknown" },
         { "id": 2, "name": "South East" },
         { "id": 3, "name": "North West" },
         { "id": 4, "name": "East Midlands" },
         { "id": 5, "name": "East" },
         { "id": 6, "name": "London" },
         { "id": 7, "name": "Yorkshire and The Humber" },
         { "id": 8, "name": "South West" },
         { "id": 9, "name": "West Midlands" },
         { "id": 10, "name": "Wales" },
         { "id": 11, "name": "North East" },
         { "id": 12, "name": "Scotland" }
      ],
      "rentalTopUpOptions": [
         { "id": 1, "name": "No" },
         { "id": 2, "name": "Yes" }
      ],
      "employmentStatusOptions": [
         { "id": 1, "name": "Employed" },
         { "id": 2, "name": "Self Employed" },
         { "id": 3, "name": "Not Employed" }
      ]
   }
   payload.update(mortgages)
   payload["applicant"] = applicants
   payload["outcome"] = {
      "result": "",
      "maxLoan": 0,
      "estimatedMonthlyRepayment": 0,
      "estimatedMonthlyRepaymentOnMaximumLoanAmount": 0,
      "btlPersonalRepaymentPercentage": 0
   }
   payload["uiState"] = {
      "activeTab": 1,
      "isValid": True,
      "showErrors": False,
      "messages": []
   }

   return payload

def main():
    with open(config) as file:
        data = json.load(file)
    payload = get_payload(data)

    response = requests.post(url, json=payload)

    if response.status_code == 200:
        response_json = response.json()
        formatted_response = json.dumps(response_json, indent=4)
        print(f"Response : {formatted_response}\n")
    elif response.status_code == 429:
        response = requests.post(url, payload)
        print(f"429")
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(f"Error message: {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
   main()