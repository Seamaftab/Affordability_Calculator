import json
import requests

url = 'https://calculator.foundationforintermediaries.co.uk/api/adp'

def get_mortgage_data(data):
    mortgage_data = []
    applicants, num_of_dependants = get_applicants(data)

    if data["Mortgage Requirement"].get("Payment Method") == "Repayment":
        Payment_Method = "Capital & Interest"
        InterestOnlyAmount = "0"
    elif data["Mortgage Requirement"].get("Payment Method") == "Interest Only":
        Payment_Method = "Interest Only"
        InterestOnlyAmount = "0"
    else:
        Payment_Method = "Part and Part"
        InterestOnlyAmount = data["Mortgage Requirement"].get("Loan Amount", 0)

    Location = data["Property Details"]["Property Details"].get("Property Location")

    if Location == "Wales":
        Region = "Wales"
    elif Location == "Scotland":
        Region = "Scotland"
    else:
        Region = "England"

    Loan_Term = data["Mortgage Requirement"].get("Loan Term")
    applicants = str(data.get("No of Applicant", 0))

    household = sum(int(value) for value in data["Client Details"][0]["Outgoings"]["Household"].values() if str(value).isdigit())
    living_costs = sum(int(value) for value in data["Client Details"][0]["Outgoings"]["Living Costs"].values() if str(value).isdigit())
    Expense = household + living_costs

    mortgage = [
        {"ID": "34411", "Value": str(InterestOnlyAmount)},
        {"ID": "34413", "Value": "0.12240000000000001"},
        {"ID": "31193", "Value": Loan_Term},
        {"ID": "31975", "Value": str(num_of_dependants)},
        {"ID": "34011", "Value": "0"},
        {"ID": "34021", "Value": "0"},
        {"ID": "34431", "Value": str(Expense)},
        {"ID": "34432", "Value": "0"},
        {"ID": "34438", "Value": "0"},
        {"ID": "34439", "Value": "0"},
        {"ID": "31191", "Value": 49999},
        {"ID": "34412", "Value": "Other"},
        {"ID": "34425", "Value": str(applicants)},
        {"ID": "34391", "Value": "WEB001"},
        {"ID": "34392", "Value": "WEB002"},
        {"ID": "34393", "Value": "WEB003"},
        {"ID": "34394", "Value": "WEB004"},
        {"ID": "34401", "Value": "WEB001"},
        {"ID": "34410", "Value": Payment_Method},
        {"ID": "31636", "Value": 0},
        {"ID": "31831", "Value": 0},
        {"ID": "31637", "Value": Region}
    ]

    mortgage_data += mortgage

    return mortgage_data

def get_applicants(data):
    applicant_data = []
    num_of_dependants = 0
    applicant_details = data.get("Client Details", [])

    for i,applicant in enumerate(applicant_details):
      num_of_dependants += len(applicant.get("dependants"))
      ffi = []
          
      if i == 0:
        ffi += [
          {"ID": "33021", "Value": str(applicant["Employment Details"].get("Basic Annual Income", 0))},
          {"ID": "33031", "Value": str(applicant["Additional Income (Annual)"].get("Irregular Overtime", 0))},
          {"ID": "33381", "Value": "0"},
          {"ID": "33121", "Value": str(applicant["Employment Details"].get("Last Year's Salary", 0))},
          {"ID": "33131", "Value": "0"},
          {"ID": "33161", "Value": "0"},
          {"ID": "33181", "Value": str(applicant["Employment Details"].get("Last Year's Dividends", 0))},
          {"ID": "33201", "Value": "0"},
          {"ID": "33211", "Value": "0"},
          {"ID": "33231", "Value": "0"},
          {"ID": "33271", "Value": "0"},
          {"ID": "33261", "Value": "0"},
          {"ID": "33351", "Value": "0"},
          {"ID": "33421", "Value": "0"},
          {"ID": "33301", "Value": "0"},
          {"ID": "33361", "Value": "0"}
        ]
      elif i == 1:
        ffi += [
          {"ID": "33022", "Value": str(applicant["Employment Details"].get("Basic Annual Income", 0))},
          {"ID": "33032", "Value": str(applicant["Additional Income (Annual)"].get("Irregular Overtime", 0))},
          {"ID": "33382", "Value": "0"},
          {"ID": "33122", "Value": str(applicant["Employment Details"].get("Last Year's Salary", 0))},
          {"ID": "33132", "Value": "0"},
          {"ID": "33162", "Value": "0"},
          {"ID": "33182", "Value": str(applicant["Employment Details"].get("Last Year's Dividends", 0))},
          {"ID": "33202", "Value": "0"},
          {"ID": "33212", "Value": "0"},
          {"ID": "33232", "Value": "0"},
          {"ID": "33272", "Value": "0"},
          {"ID": "33262", "Value": "0"},
          {"ID": "33352", "Value": "0"},
          {"ID": "33422", "Value": "0"},
          {"ID": "33302", "Value": "0"},
          {"ID": "33362", "Value": "0"}
        ]
      elif i == 2:
        ffi += [
          {"ID": "33023", "Value": str(applicant["Employment Details"].get("Basic Annual Income", 0))},
          {"ID": "33033", "Value": str(applicant["Additional Income (Annual)"].get("Irregular Overtime", 0))},
          {"ID": "33383", "Value": "0"},
          {"ID": "33123", "Value": str(applicant["Employment Details"].get("Last Year's Salary", 0))},
          {"ID": "33133", "Value": "0"},
          {"ID": "33163", "Value": "0"},
          {"ID": "33183", "Value": str(applicant["Employment Details"].get("Last Year's Dividends", 0))},
          {"ID": "33203", "Value": "0"},
          {"ID": "33213", "Value": "0"},
          {"ID": "33233", "Value": "0"},
          {"ID": "33273", "Value": "0"},
          {"ID": "33263", "Value": "0"},
          {"ID": "33353", "Value": "0"},
          {"ID": "33423", "Value": "0"},
          {"ID": "33303", "Value": "0"},
          {"ID": "33363", "Value": "0"}
        ]
      else:
        ffi += [
          {"ID": "33024", "Value": str(applicant["Employment Details"].get("Basic Annual Income", 0))},
          {"ID": "33034", "Value": str(applicant["Additional Income (Annual)"].get("Irregular Overtime", 0))},
          {"ID": "33384", "Value": "0"},
          {"ID": "33124", "Value": str(applicant["Employment Details"].get("Last Year's Salary", 0))},
          {"ID": "33134", "Value": "0"},
          {"ID": "33164", "Value": "0"},
          {"ID": "33184", "Value": str(applicant["Employment Details"].get("Last Year's Dividends", 0))},
          {"ID": "33204", "Value": "0"},
          {"ID": "33214", "Value": "0"},
          {"ID": "33234", "Value": "0"},
          {"ID": "33274", "Value": "0"},
          {"ID": "33264", "Value": "0"},
          {"ID": "33354", "Value": "0"},
          {"ID": "33424", "Value": "0"},
          {"ID": "33304", "Value": "0"},
          {"ID": "33364", "Value": "0"}
        ]

      applicant_data += ffi

    return applicant_data, num_of_dependants

def get_payload(data):
  mortgages = get_mortgage_data(data)
  applicants, num_of_dependants = get_applicants(data)
  payload = {}

  payload["properties"] = mortgages + applicants

  return payload

def main():
    with open(config) as file:
        data = json.load(file)
    payload = get_payload(data)
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code==200:
        response_json = response.json()
        formatted_response = json.dumps(response_json, indent=4)
        print(f"Response : {formatted_response}\n")
    elif response.status_code==429:
        response = requests.post(url, json=payload)
        print(f"retrying...")
    else:
        print(f"Request failed, status code : {response.status_code}")
        print(f"Error : {response.text}")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
    main()

