import requests
import json
from bs4 import BeautifulSoup

url = "https://www.newbury.co.uk/mortgages/affordability-calculator/"

def get_applicants(data):
	applicant_data = {}
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])

	for i, applicant in enumerate(applicant_details):
		num_of_dependants += len(applicant["dependants"])
		net_income = applicant["Employment Details"].get("Net Monthly Income", 0)

		applicant_data[f"gai{i+1}"] = applicant["Employment Details"].get("Basic Annual Income", 0)
		applicant_data[f"nmi{i+1}"] = 0 if net_income in ["null", None] else int(net_income)

	if i < 1:
		applicant_data['gai2'] = 0
		applicant_data['nmi2'] = 0

	return applicant_data, num_of_dependants

def get_mortgage_data(data):
	mortgage_data = {}
	applicants, num_of_dependants = get_applicants(data)
	Adults = data.get("No of Applicant")

	payment = data["Mortgage Requirement"].get("Payment Method")
	shared = data["Mortgage Requirement"].get("Mortgage Type")
	if shared == "Shared Ownership":
		shared_or_help = "shared ownership"
	elif shared == "Help To Buy":
		shared_or_help = "help to buy"
	else:
		shared_or_help = "no"

	mortgage_data["csrfmiddlewaretoken"] = "s2MIhwWrx6ZFvOuSxr2HH4XS23WZaiAt47vkBx3iiOQ74UiAV7JJn1cTj1SoQXXI"
	if num_of_dependants < 1 :
		mortgage_data["house"]=f"{Adults}A"
	else:
		if Adults>=3:
			mortgage_data["house"]="3AXC"
		elif num_of_dependants>3:
			mortgage_data["house"]=f"{Adults}A3C"
		else:
			mortgage_data["house"]=f"{Adults}A{num_of_dependants}C"

	mortgage_data["shared"]= shared_or_help
	mortgage_data["term"]=int(data["Mortgage Requirement"].get("Loan Term",0)/12)
	mortgage_data["repayment_type"]="capital-interest" if payment == "Repayment" else "interest-only"
	mortgage_data["submit"]="Calculate"

	return mortgage_data

def get_expenses(data):
	expenses = {}

	credit = data["Client Details"][0].get("Credit Commitments")

	expenses["lo"]=0
	expenses["iorv"]=0
	expenses["cc"]=0 if credit in ["null", None] else credit
	expenses["gr"]=0
	expenses["csf"]=0
	expenses["pen"]=0
	expenses["csa"]=0
	expenses["sor"]=0
	expenses["ete"]=data["Client Details"][0]["Outgoings"]["Living Costs"].get("Travel", 0)
	expenses["sel"]=0
	expenses["stu"]=0

	return expenses

def get_payload(data):
	applicants, num_of_dependants = get_applicants(data)
	mortgages = get_mortgage_data(data)
	expenses = get_expenses(data)

	payload = mortgages
	payload.update(applicants)
	payload.update(expenses)

	return payload

def main():
	with open(config) as file:
		data = json.load(file)
	payload = get_payload(data)

	headers = {
	  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
	  'Accept-Encoding': 'gzip, deflate, br, zstd',
	  'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
	  'Cache-Control': 'max-age=0',
	  'Content-Type': 'application/x-www-form-urlencoded',
	  'Cookie': 'django_language=en-gb; csrftoken=ZqetLj06IUSXlj2215LPXxTiffRZAPo8BvX55k7XtCJpUpQKpLsRDu8jwdNoguLn; whoson=105-1702045527681; OptanonAlertBoxClosed=2023-12-08T14:25:32.625Z; _gcl_au=1.1.1060437596.1702045533; _ga=GA1.1.538271243.1702045533; _fbp=fb.2.1702045533748.1024479092; sessionid=4b2l1zt5tqerftago431nqh8roiy40ic; _ga_JTNL51FL6R=GS1.1.1703701594.3.0.1703701594.0.0.0; OptanonConsent=isGpcEnabled=0&datestamp=Thu+Dec+28+2023+00%3A26%3A34+GMT%2B0600+(Bangladesh+Standard+Time)&version=6.19.0&isIABGlobal=false&hosts=&consentId=9cca6c63-03b7-4704-bfa2-da3c9d43f50f&interactionCount=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0004%3A1%2CC0003%3A1%2CC0002%3A1&geolocation=BD%3BB&AwaitingReconsent=false; csrftoken=ZqetLj06IUSXlj2215LPXxTiffRZAPo8BvX55k7XtCJpUpQKpLsRDu8jwdNoguLn; django_language=en-gb; sessionid=4b2l1zt5tqerftago431nqh8roiy40ic',
	  'Dnt': '1',
	  'Origin': 'https://www.newbury.co.uk',
	  'Referer': 'https://www.newbury.co.uk/',
	  'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
	  'Sec-Ch-Ua-Mobile': '?0',
	  'Sec-Ch-Ua-Platform': '"Windows"',
	  'Sec-Fetch-Dest': 'document',
	  'Sec-Fetch-Mode': 'navigate',
	  'Sec-Fetch-Site': 'same-origin',
	  'Sec-Fetch-User': '?1',
	  'Upgrade-Insecure-Requests': '1',
	  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
	}

	response = requests.post(url, headers=headers, data=payload)
	if response.status_code == 200:
		soup = BeautifulSoup(response.text, "html.parser")
		amount = soup.select_one(".mortgage-amount > .row > .col-sm-6 > div.amount")
		if amount:
		    print("You can borrow:", amount.text)
		else:
		    print("Amount element not found.")
	else:
		print(f"Request failed with status code: {response.status_code}")
		print(response.text)

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
    main()

