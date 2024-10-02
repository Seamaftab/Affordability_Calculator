import requests
import json
from datetime import datetime
from bs4 import BeautifulSoup
import urllib


csrf_token = ""
req_cookies = None

headers = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'Origin': 'https://harpenden-bs.calc.affordabilityhub.co.uk',
  'Referer': 'https://harpenden-bs.calc.affordabilityhub.co.uk/affordability',
  'DNT': '1',
  'Accept': 'application/json, text/javascript, */*; q=0.01',
  'Accept-Encoding': 'gzip, deflate, br, zstd',
  'Accept-Language': 'en-US,en;q=0.9,bn;q=0.8',
  'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
  'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'Sec-Ch-Ua-Mobile': '?0',
  'Sec-Ch-Ua-Platform': '"Windows"',
  'Sec-Fetch-Dest': 'empty',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Site': 'same-origin',
  'X-Requested-With': 'XMLHttpRequest'
}


# Get CSRF Token
def get_csrf_token():
	global csrf_token, req_cookies
	url = "https://harpenden-bs.calc.affordabilityhub.co.uk/affordability"
	response = requests.get(url, headers=headers)
	soup = BeautifulSoup(response.content, "html.parser")
	csrf_token_tag = soup.find("meta", {"name": "csrf-token"})
	if csrf_token_tag:
		csrf_token = csrf_token_tag.get("content")
		req_cookies = response.cookies
		return csrf_token
	else:
		print("CSRF token meta tag not found.")
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
	#print("The CSRF token is :",csrf_token)
	mortgage_data["_token"] = csrf_token
	mortgage_data["q-fff50dc9-57ed-4715-ad97-37ae6a5033ae"] = "Purchase" if Loan_Purpose == "Purchase" else ["Remortgage"]
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
	mortgage_data["q-dfc7200f-bbc2-49f5-b310-579bc1c17eaf"] = "Fr"

	Location = data["Property Details"].get("Property Location")
	Places = ["England", "Northern Ireland", "Scotland"]

	mortgage_data["q-5196874d-553e-43fd-bf9a-9daeec8abf54"] = "E" if Location in Places else "W"
	mortgage_data["q-ea608c6e-426d-4a09-9ef4-98d76f78cd4e"] = "0"
	mortgage_data["q-b64999ba-33b9-4757-bdde-b89fef560304"] = "0"
	mortgage_data["q-25cf9b87-3937-4f15-87c9-6c0720c78dbf"] = "0"
	mortgage_data["q-54d4be7e-5b09-4f32-834d-b7bbe2c39df0"] = "0"
	mortgage_data["q-ec8e1784-6bb7-4398-8e31-9439a4f490ab"] = "0"
	mortgage_data["q-604561ac-2457-4182-885e-ab0c4a24826a"] = "0"

	return mortgage_data


def get_applicants(data):
	applicant_data = {}
	dependants = 0
	applicant_details = data.get("Client Details", [])

	for i, applicant in enumerate(applicant_details):
		dependants = applicant.get("dependants")
		for dep in dependants:
			age = calculate_age(dep.get("date of birth"))
			dep["age"] = age
		dob = applicant.get("Date of Birth")
		date_of_birth = datetime.strptime(dob, '%d/%m/%Y').strftime('%Y/%m/%d')
		income = applicant["Employment Details"].get("Basic Annual Income", 0)
		bonus = applicant["Additional Income (Annual)"].get("Regular Bonus", 0)
		net_income = applicant["Employment Details"].get("Last Year's Salary",0)
		net_ltd_income = applicant["Employment Details"].get("Last Year's Net Profits",0)
		net_ltd = applicant["Employment Details"].get("Last Year's Dividends",0)
		Transport = applicant["Outgoings"].get("Transport")
		household_expenses = sum(applicant["Outgoings"]["Household"].values())

		applicant = {
			f"app[{i+1}][q-ec011eab-434e-4087-a299-8497bcd16b1c]": "N", #retired?
			f"app[{i+1}][q-fc8b37e0-3262-4dd9-bc83-23b14bd173d1]": str(len(dependants)),
			f"app[{i+1}][q-af0a849d-de8a-4dee-b891-2cd38735f950]": str(age) if len(dependants)>0 else "0",
			f"app[{i+1}][q-ec2498d8-92b5-4c74-a98e-5be3da2c97e3]": "0",
			f"app[{i+1}][q-84b58cd6-c325-4277-819f-9cc0699cbe0a]": "0",
			f"app[{i+1}][q-377b5b30-15b4-439d-8b4a-0325a8487eba]": "0",
			f"app[{i+1}][q-f3d15f8e-0024-4edf-885f-b476bde4a96e]": "0",
			f"app[{i+1}][q-97926919-f7b3-42ee-9872-ddfb5736b122]": "0",
			f"app[{i+1}][q-52ab731f-788f-45e2-bd1c-c9d4805f895a]": "0",
			f"app[{i+1}][q-2ebaf6a3-2db0-4493-8535-527bd8dfb68d]": "0",
			f"app[{i+1}][q-2a2bc27f-3f13-4aad-ab7a-7b65aafdd3f5]": "0",
			f"app[{i+1}][q-c98d3c08-9f44-4855-a696-9e14c46be256]": "0",
			f"app[{i+1}][q-a8eaa370-044f-4e11-a60c-e2fba7a5f0a1]": str(date_of_birth),
			f"app[{i+1}][q-3ee7ef80-0df1-4bea-a0db-d109c24fbcd6]": str(income),
			f"app[{i+1}][q-3b23f5f2-7d3c-46b6-a4bf-4b529628defb]": str(bonus),
			f"app[{i+1}][q-6fa8685d-0deb-480a-b38a-7ff2b235a8f8]": "0",
			f"app[{i+1}][q-e57f0bd2-aa44-4cf0-b18d-3a643de56c4c]": "0",
			f"app[{i+1}][q-04782e03-292d-4eb3-a17b-b38cc362773c]": "2023-12-31" if net_income>0 else "0",
			f"app[{i+1}][q-94bbb704-65d2-41ab-ad3c-0b3ca0a202a0]": str(net_income),
			f"app[{i+1}][q-95e6138e-0e4e-4048-a432-661e5ac292d8]": "2023-12-31" if net_ltd>0 else "0",
			f"app[{i+1}][q-f0e4084c-4398-40c3-9b0c-1e22cd950171]": str(net_ltd_income),
			f"app[{i+1}][q-e07b40e5-d94e-4870-9579-34375010e928]": str(net_ltd),
			f"app[{i+1}][q-3303ca7c-da9f-4607-a48f-ce4a6dcebb0c]": "0",
			f"app[{i+1}][q-a8dcd411-b245-4fde-b3e3-3f89064fda98]": "0",
			f"app[{i+1}][q-a91cf466-4125-46e4-8e06-3c391ccbfba7]": "0",
			f"app[{i+1}][q-11f3bd0d-fb34-4754-ab2c-88963cf1a642]": "0",
			f"app[{i+1}][q-2121e7d5-86cd-4743-a436-d039c5e1a1cf]": "0",
			f"app[{i+1}][q-dfd02c7a-cffc-4ca8-b604-af774cae12c4]": "0",
			f"app[{i+1}][q-e7ec2261-ed5b-4afa-933b-7a576adcd256]": "0",
			f"app[{i+1}][q-eb656938-6d14-4de4-ae4a-2afd8c0a6b62]": "0",
			f"app[{i+1}][q-712b1523-a718-4645-9fae-7cc4b87a254b]": "0",
			f"app[{i+1}][q-db5bed0e-52f1-4445-bb02-a24075469208]": "0",
			f"app[{i+1}][q-9ab22092-276d-4e44-8074-fdd24e000561]": "0",
			f"app[{i+1}][q-f85e81d5-d3e6-4682-a671-f20b2c78dae9]": "0",
			f"app[{i+1}][q-56ab7c55-f307-41ec-9049-8c4db9e37b64]": "0",
			f"app[{i+1}][q-60d5d695-1686-447c-a3d4-f43ea58cbee2]": "0",
			f"app[{i+1}][q-7b29031e-c3d6-4cd7-b65b-2cd599e82416]": "0",
			f"app[{i+1}][q-f617bc75-c4cc-492f-b31d-d12b592d2741]": "0",
			f"app[{i+1}][q-2a5b7431-38d6-409b-96cc-f964cf5c352a]": "N",
			f"app[{i+1}][q-dcb0148e-e7a6-45b5-ade7-8e187cfd65d6]": "N",
			f"app[{i+1}][q-6ddc7afe-a408-47a1-87d1-64987abe07f1]": "0",
			f"app[{i+1}][q-e37ef206-47a7-46c6-8848-d8ab93c82d93]": "0",
			f"app[{i+1}][q-673e308e-f2ef-4e89-b789-89ba6e3d6f25]": "0",
			f"app[{i+1}][q-b96968bb-9fcb-4f98-9ed5-5b09d4df5a7a]": "0",
			f"app[{i+1}][q-a144fd87-2542-4184-8ba3-f4b6c97d2c68]": str(household_expenses),
			f"app[{i+1}][q-cf2b6dd2-59eb-47e6-922f-d802142b6b9f]": "0" if Transport in ["null", None] else str(Transport),
			f"app[{i+1}][q-9986ec78-5494-4dee-956c-66bf4c700c07]": "0",
			f"app[{i+1}][q-3888d3f1-a31a-4573-adf7-d2afbe994c4f]": "0",
			f"app[{i+1}][q-25c86b07-9513-474e-9df4-e97e88b42021]": "0",
			f"app[{i+1}][q-9684aa23-2430-4f80-8843-091c4f4819f6]": "0",
			f"app[{i+1}][q-19a1a4d1-2778-4df4-bfe4-b062dcb158b6]": "0",
			f"app[{i+1}][q-3d96d9cf-104a-43f8-a5e5-95f4de534115]": "0",
			f"app[{i+1}][q-94dbd1cc-fcc8-44bf-91b5-c6039f5fde47]": "0",
			f"app[{i+1}][q-bec6d293-e767-4de3-a5d0-083095c4cc5b]": "0",
			f"app[{i+1}][q-c3a08c22-f740-4a9c-9faa-b2faadf4d956]": "0",
			f"app[{i+1}][q-d06dc3a3-bcd1-4556-bc89-196eb52086cd]": "0",
			f"app[{i+1}][q-80ef8187-74d9-4a19-972a-a142d425fb27]": "0",
			f"app[{i+1}][q-5210f4b2-2d9c-4b99-a15e-9954834798f1]": "0",
			f"app[{i+1}][q-0ebf106a-4e7b-4b50-8246-f8a0aa9998da]": "0",
			f"app[{i+1}][q-dd23d4f2-3fb6-4a72-88ea-6d517711be5a]": "0",
			f"app[{i+1}][q-984715f9-fd2c-4014-9c0f-2b54b7fccb70]": "0"
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
	global csrf_token, req_cookies

	if not csrf_token: 
		#print("Setting CSRF Token")
		csrf_token = get_csrf_token()
		#print("Got CSRF token", csrf_token)
	
	for i in range(2):
		url = "https://harpenden-bs.calc.affordabilityhub.co.uk/calculate"
		with open(config) as file:
			data = json.load(file)
		payload = get_payload(data)

		res= requests.post(url, headers=headers, data=payload, cookies=req_cookies)
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

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config in config_files:
   main()
