import json
import requests

url = "https://www.teachersbuildingsociety.co.uk/mortgage-calculator/Calculate/"

def get_params(data):
	net_income = data["Client Details"][0]["Employment Details"].get("Net Monthly Income", 0)
	credit = data["Client Details"][0]["Outgoings"].get("Credit Commitments", 0)

	params = {
	    "applicants": data.get("No of Applicant", 0),
	    "dependants": len(data["Client Details"][0].get("dependants", [])),
	    "depositAmount": 1000,
	    "grossAnnualIncome": data["Client Details"][0]["Employment Details"].get("Basic Annual Income", 0),
	    "netMonthlyIncome": 0 if net_income in (None, "null") else net_income,
	    "creditCommitments": 0 if credit in (None, "null") else credit,
	    "mortgageTerm": int(data["Mortgage Requirement"].get("Loan Term", 0) / 12)
	}

	return params

def main():
	with open(config) as file:
		data = json.load(file)
	params = get_params(data)

	headers = {
	'Cookie': 'ASP.NET_SessionId=3z4zwcjc4dn1wexfdep52q0i; AWSALB=oE7KVJv3Tv3Asf5InTJBDYlgGcy1IE7Egsy7qfQ2WJCWUauCPpTxK+4En/3ulA8a8Q4eTwEyq1Poea9WRS4+K0orJqr+aV52dnhAGFnaYKVX1BFfdNAQeTdtfOod; AWSALBCORS=oE7KVJv3Tv3Asf5InTJBDYlgGcy1IE7Egsy7qfQ2WJCWUauCPpTxK+4En/3ulA8a8Q4eTwEyq1Poea9WRS4+K0orJqr+aV52dnhAGFnaYKVX1BFfdNAQeTdtfOod; sf-data-intell-subject=5bfe37c4-33e1-4a21-b965-f8385e257158'
	}

	# param_json = json.dumps(params, indent=4)
	# print(param_json)
	response = requests.get(url, headers=headers, params=params)

	if response.status_code == 200:
		response_json = response.json()
		formatted_response = json.dumps(response_json, indent=4)
		print(f"Response : {formatted_response}\n")
	else:
	    print(f"Request failed with status code: {response.status_code}")
	    print(response.text)

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
	main()