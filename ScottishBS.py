import json
import requests
import urllib
from datetime import datetime
from bs4 import BeautifulSoup

csrf_token = ""
request_cookies = None

headers = {
	"Accept": "application/json, text/javascript, */*; q=0.01",
	"Accept-Encoding": "gzip, deflate, br, zstd",
	"Accept-Language": "en-US,en;q=0.9,bn;q=0.8",
	"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
	"X-Requested-With": "XMLHttpRequest"
}

# Get CSRF Token
def get_csrf_token():
	global csrf_token, request_cookies
	url = "https://scottishbs.calc.affordabilityhub.co.uk/affordability"
	try:
		response = requests.get(url, headers=headers)
		soup = BeautifulSoup(response.content, "html.parser")
		csrf_token_tag = soup.find("meta", {"name": "csrf-token"})
		
		if csrf_token_tag:
			csrf_token = csrf_token_tag.get("content")
			request_cookies = response.cookies
			return csrf_token
		else:
			print("CSRF token meta tag not found.")
			return None
	except requests.RequestException as e:
		print(f"Error: {e}")
		return None

def calculate_age(birthdate):
	birth_date = datetime.strptime(birthdate, '%d/%m/%Y')
	current_date = datetime.now()
	age = current_date.year - birth_date.year - ((current_date.month, current_date.day) < (birth_date.month, birth_date.day))
	return age

def get_mortgage_data(data):
	global csrf_token
	mortgage_data = {}

	Loan_Purpose = data["Mortgage Requirement"].get("Loan Purpose")
	Purchase_Price = data["Mortgage Requirement"].get("Purchase Price", 0)
	Loan_Amount = data["Mortgage Requirement"].get("Loan Amount", 0)

	mortgage_data["_token"] = csrf_token
	mortgage_data["q-fff50dc9-57ed-4715-ad97-37ae6a5033ae"] = "Purchase" if Loan_Purpose == "Purchase" else "Remortgage"
	mortgage_data["q-8cbdfae3-9ed0-49cb-affa-287e550a1e06"] = str(Purchase_Price)

	payment_method = data["Mortgage Requirement"].get("Payment Method")
	if payment_method == "Repayment":
		mortgage_data["q-5a54a130-eb2f-44b5-bd36-25b6a8f4376e"] = "C"
	elif payment_method == "Interest Only":
		mortgage_data["q-5a54a130-eb2f-44b5-bd36-25b6a8f4376e"] = "I"
	else:
		mortgage_data["q-5a54a130-eb2f-44b5-bd36-25b6a8f4376e"] = "M"

	mortgage_data["q-1f0acfe3-ce65-402f-b5e3-813f5ae700e3"] = str(Loan_Amount)
	mortgage_data["deposit"] = str(Purchase_Price - Loan_Amount)
	mortgage_data["ltv"] = str(int((Loan_Amount / Purchase_Price) * 100))
	mortgage_data["q-f22b0020-65b5-4327-bccf-975c75fedf6b"] = str(int(data["Mortgage Requirement"].get("Loan Term", 0) / 12))
	mortgage_data["q-01501241-eeab-41d0-9089-af446be00c48"] = str(data.get("No of Applicant"))
	mortgage_data["q-f2166080-c39f-44fc-a950-2380a1bfa02d"] = "Y"
	mortgage_data["q-3f4f6385-ca1c-41d1-a87d-9caff00a005d"] = "Y"
	mortgage_data["q-ea608c6e-426d-4a09-9ef4-98d76f78cd4e"] = "0"
	mortgage_data["q-b64999ba-33b9-4757-bdde-b89fef560304"] = "0"
	mortgage_data["q-25cf9b87-3937-4f15-87c9-6c0720c78dbf"] = "0"
	mortgage_data["q-54d4be7e-5b09-4f32-834d-b7bbe2c39df0"] = "0"
	mortgage_data["q-ec8e1784-6bb7-4398-8e31-9439a4f490ab"] = "0"
	mortgage_data["q-604561ac-2457-4182-885e-ab0c4a24826a"] = "0"
	mortgage_data["q-3aa36885-9555-43d4-8240-894810c991e9"] = "5.14"
	mortgage_data["q-79ea8c40-1662-4804-9429-e37def59398c"] = "No"

	return mortgage_data

def get_applicants(data):
	applicant_data = {}
	num_of_dependants = 0
	applicant_details = data.get("Client Details", [])

	for i ,applicant in enumerate(applicant_details):
		num_of_dependants = applicant.get("dependants")
		for dep in num_of_dependants:
			age = calculate_age(dep.get("date of birth"))
			dep["age"] = age
		dob = applicant.get("Date of Birth")
		date_of_birth = datetime.strptime(dob, '%d/%m/%Y').strftime('%Y/%m/%d')

		e_stat = applicant["Employment Details"].get("Employment Status")
		income = applicant["Employment Details"].get("Basic Annual Income", 0)
		bonus = applicant["Additional Income (Annual)"].get("Regular Bonus", 0)
		net_income = applicant["Employment Details"].get("Last Year's Salary",0)
		net_ltd_income = applicant["Employment Details"].get("Last Year's Net Profits",0)
		net_ltd = applicant["Employment Details"].get("Last Year's Dividends",0)

		AdditionalIncome = applicant.get("Additional Income (Annual)", [])
		credit = 0 if applicant["Outgoings"].get("Credit Commitments", 0) in ["null", None] else applicant["Outgoings"].get("Credit Commitments", 0)

		Transport = 0 if applicant["Outgoings"].get("Transport", 0) in ["null", None] else applicant["Outgoings"].get("Transport", 0)
		household_expenses = sum(applicant["Outgoings"]["Household"].values())

		applicant = {
			f"app[{i+1}][q-baa87d1d-329b-4f3b-a5aa-c3184b12972a]":str(date_of_birth),
			f"app[{i+1}][q-ec011eab-434e-4087-a299-8497bcd16b1c]":"N" if e_stat != "Retired" else "Y",
			f"app[{i+1}][q-8d71905e-8b3e-4470-89d1-85c7ec8cf646]":str(applicant.get("expected retirement age")),
			f"app[{i+1}][q-fc8b37e0-3262-4dd9-bc83-23b14bd173d1]":str(len(num_of_dependants)),
			f"app[{i+1}][q-af0a849d-de8a-4dee-b891-2cd38735f950]":str(age) if len(num_of_dependants)>0 else "0",
			f"app[{i+1}][q-a75fce0d-a574-4468-bc8b-c6b121fecc1f]":"3", #Years of Job
			f"app[{i+1}][q-3ee7ef80-0df1-4bea-a0db-d109c24fbcd6]":str(income),
			f"app[{i+1}][q-3b23f5f2-7d3c-46b6-a4bf-4b529628defb]":str(bonus*12),
			f"app[{i+1}][q-feadc6f6-310b-4cb5-b125-9e6628cf07f2]":"0",
			f"app[{i+1}][q-d69abf5c-2b3a-4fbc-9591-e841e7ae1340]":str(bonus),
			f"app[{i+1}][q-e4f37c07-99d2-4246-9969-588419eeaa6f]":"0",
			f"app[{i+1}][q-b9af056f-78c8-44f9-970b-b8f22350b41b]":"0",
			f"app[{i+1}][q-9b845337-1b01-4b42-ba32-3547faaa488e]":"0",
			f"app[{i+1}][q-420938b2-a67d-41f1-8aca-6d8766888f05]":"0",
			f"app[{i+1}][q-25e210b7-f8be-4cb8-843d-89a567f4a653]":"0",
			f"app[{i+1}][q-29987ae2-45a8-4d32-9ba1-998f6e7b7349]":str(AdditionalIncome.get("Irregular Overtime", 0)),
			f"app[{i+1}][q-327d5c8e-2fb1-4deb-bfe2-eb95582ddfce]":"0",
			f"app[{i+1}][q-bab0fe84-876b-4110-a3e3-4324266a30aa]":"0",
			f"app[{i+1}][q-6fa8685d-0deb-480a-b38a-7ff2b235a8f8]":"0",
			f"app[{i+1}][q-22829a87-2e34-4360-988f-2e7e75fb953e]":"0",
			f"app[{i+1}][q-e57f0bd2-aa44-4cf0-b18d-3a643de56c4c]":"0",
			f"app[{i+1}][q-4035146f-bde6-4a70-9f3b-2d5b220becc8]":"0",
			f"app[{i+1}][q-16ec173b-33db-44bd-8d40-777972d343e2]":"0",
			f"app[{i+1}][q-4734d455-752b-4973-90d8-eca4227499e9]":"0",
			f"app[{i+1}][q-7fb5cafc-0874-4a6e-9525-5082aa5562a2]":"0", # DON'T HAVE VALUES IN REFERENCE
			f"app[{i+1}][q-94bbb704-65d2-41ab-ad3c-0b3ca0a202a0]":"0",
			f"app[{i+1}][q-42666981-9c80-49d1-826b-f0b0d48fc38b]":"0",
			f"app[{i+1}][q-1e3d5abe-a1aa-41e0-8047-c46ae80d119a]":"0",
			f"app[{i+1}][q-0bf9b12c-4327-4696-8fb9-4ccac266068a]":"0", # DON'T HAVE VALUES IN REFERENCE
			f"app[{i+1}][q-f0e4084c-4398-40c3-9b0c-1e22cd950171]":"0",
			f"app[{i+1}][q-25eeeabd-c650-4903-8fe6-2a8f7da7e10c]":"0",
			f"app[{i+1}][q-77b79a1d-bbf2-4102-aac2-f866e3aa8e45]":"0",
			f"app[{i+1}][q-e07b40e5-d94e-4870-9579-34375010e928]":"0",
			f"app[{i+1}][q-6eced849-d34d-418c-84da-066914dedfd6]":"0",
			f"app[{i+1}][q-6347ee57-54fb-4cf8-8857-7a9c0561ca1e]":"0",
			f"app[{i+1}][q-3303ca7c-da9f-4607-a48f-ce4a6dcebb0c]":"0",
			f"app[{i+1}][q-a8dcd411-b245-4fde-b3e3-3f89064fda98]":"0",
			f"app[{i+1}][q-a91cf466-4125-46e4-8e06-3c391ccbfba7]":"0",
			f"app[{i+1}][q-3ba07168-05ae-46b7-8020-cb798491f294]":"0",
			f"app[{i+1}][q-ea58af52-2de9-4d3d-963e-eddf440622d1]":"0",
			f"app[{i+1}][q-66dd8816-0879-4104-841a-73b394984b19]":"0",
			f"app[{i+1}][q-11f3bd0d-fb34-4754-ab2c-88963cf1a642]":"0",
			f"app[{i+1}][q-2121e7d5-86cd-4743-a436-d039c5e1a1cf]":"0",
			f"app[{i+1}][q-dfd02c7a-cffc-4ca8-b604-af774cae12c4]":"0",
			f"app[{i+1}][q-6f7e7b8b-be37-48fb-8cb4-dae2077b68f8]":"0",
			f"app[{i+1}][q-eb656938-6d14-4de4-ae4a-2afd8c0a6b62]":"0",
			f"app[{i+1}][q-d241c658-2585-4d57-bd78-9a487a268a05]":"0",
			f"app[{i+1}][q-0c284d2e-623e-4ca6-aa30-2bc8afdea87c]":"0",
			f"app[{i+1}][q-5523570f-796a-4ff4-a8ed-ac0edd421bf3]":"0",
			f"app[{i+1}][q-712b1523-a718-4645-9fae-7cc4b87a254b]":"0",
			f"app[{i+1}][q-9ab22092-276d-4e44-8074-fdd24e000561]":"0",
			f"app[{i+1}][q-812f5222-d5b0-4f1e-b5ee-e3721df0d5f5]":str(credit),
			f"app[{i+1}][q-989f9a1c-ce40-459d-9cb6-2d277b9326bf]":"0",
			f"app[{i+1}][q-f11d54b6-5782-4793-9dc3-039644558e89]":"0",
			f"app[{i+1}][q-e2735533-9d37-46dd-9dbb-f8e7d3424b02]":"0",
			f"app[{i+1}][q-bbc9f82a-5cc6-45c8-8592-c6f88f41d537]":"0",
			f"app[{i+1}][q-e988b624-6e07-474b-9a2b-37652d398e0b]":"0",
			f"app[{i+1}][q-6ddc7afe-a408-47a1-87d1-64987abe07f1]":"0",
			f"app[{i+1}][q-e37ef206-47a7-46c6-8848-d8ab93c82d93]":"0",
			f"app[{i+1}][q-673e308e-f2ef-4e89-b789-89ba6e3d6f25]":"0",
			f"app[{i+1}][q-b96968bb-9fcb-4f98-9ed5-5b09d4df5a7a]":str(household_expenses),
			f"app[{i+1}][q-a144fd87-2542-4184-8ba3-f4b6c97d2c68]":"0",
			f"app[{i+1}][q-cf2b6dd2-59eb-47e6-922f-d802142b6b9f]":str(Transport),
			f"app[{i+1}][q-9986ec78-5494-4dee-956c-66bf4c700c07]":str(applicant["Outgoings"]["Living Costs"].get("Mobile Phone", 0)),
			f"app[{i+1}][q-3888d3f1-a31a-4573-adf7-d2afbe994c4f]":"0",
			f"app[{i+1}][q-25c86b07-9513-474e-9df4-e97e88b42021]":"0",
			f"app[{i+1}][q-9684aa23-2430-4f80-8843-091c4f4819f6]":"0",
			f"app[{i+1}][q-19a1a4d1-2778-4df4-bfe4-b062dcb158b6]":"0",
			f"app[{i+1}][q-c3a08c22-f740-4a9c-9faa-b2faadf4d956]":"0",
			f"app[{i+1}][q-d06dc3a3-bcd1-4556-bc89-196eb52086cd]":"0",
			f"app[{i+1}][q-80ef8187-74d9-4a19-972a-a142d425fb27]":"0",
			f"app[{i+1}][q-5210f4b2-2d9c-4b99-a15e-9954834798f1]":"0",
			f"app[{i+1}][q-3d96d9cf-104a-43f8-a5e5-95f4de534115]":"0",
			f"app[{i+1}][q-bec6d293-e767-4de3-a5d0-083095c4cc5b]":"0",
			f"app[{i+1}][q-eb143064-d398-46bb-b5f3-cf615a8ba279]":"0",
			f"app[{i+1}][q-dd23d4f2-3fb6-4a72-88ea-6d517711be5a]":"0"
		}

		applicant_data.update(applicant)

	return applicant_data

def get_payload(data):
	global csrf_token
	mortgages= get_mortgage_data(data)
	applicants = get_applicants(data)
	inside_form = mortgages
	inside_form.update(applicants)

	payload = {
		"form" : urllib.parse.urlencode(inside_form),
		"affordabilityhub": False,
		"_token": csrf_token
	}

	return payload

def main():
	global csrf_token, request_cookies

	if not csrf_token: 
		#print("Setting CSRF Token")
		csrf_token = get_csrf_token()
		#print("Got CSRF token", csrf_token)
	
	for i in range(2):
		url = "https://scottishbs.calc.affordabilityhub.co.uk/calculate"
		with open('config_one.json') as file:
			data = json.load(file)
		payload = get_payload(data)

		res= requests.post(url, headers=headers, data=payload, cookies=request_cookies)
		return_data = res.json()
		if res.status_code == 200:
			print(f"Response : ACCEPTED\n{return_data}\n")
		elif res.status_code == 429:
			csrf_token = get_csrf_token()
			continue
		else:
			print(f"Request failed with status code: {res.status_code}")
			print(f"Error message: {res.text}")
		break

main()
# config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
# for config in config_files:
#    main()