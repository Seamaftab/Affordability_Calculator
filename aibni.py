import json
import math

def get_mortgage_data(data):
	mortAmount = data["Mortgage Requirement"].get("Loan Amount", 0)
	propValue = data["Mortgage Requirement"].get("Purchase Price", 0)
	mortTerm = int(data["Mortgage Requirement"].get("Loan Term", 0)/12)
	ltv = (mortAmount/propValue)*100
	product_term = int(data["Mortgage Requirement"].get("Product term", 24)/12)

	return mortAmount, propValue, mortTerm, ltv, product_term

def get_applicants(data):
	applicant_data = {}
	num_of_dependants = 0
	num_of_applicants = data.get("No of Applicant")
	applicant_details = data.get("Client Details", [])
	applicant_one = applicant_details[0]
	applicant_two = applicant_details[1] if len(applicant_details) > 1 else {}
	null = ["null", None]
	num_of_dependants += len(applicant_one.get("dependants", [])) + len(applicant_two.get("dependants", []))

	basic_annual_income1 = applicant_one.get("Employment Details", {}).get("Basic Annual Income", 0)
	basic_annual_income2 = applicant_two.get("Employment Details", {}).get("Basic Annual Income", 0)

	netmonthly_1 = int(basic_annual_income1*0.06704) if applicant_one.get("Employment Details", {}).get("Net Monthly Income") in null else int(applicant_one.get("Employment Details", {}).get("Net Monthly Income"))
	netmonthly_2 = int(basic_annual_income2*0.06704) if applicant_two.get("Employment Details", {}).get("Net Monthly Income") in null else int(applicant_two.get("Employment Details", {}).get("Net Monthly Income"))
	additional_1 = applicant_one.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0)
	additional_2 = applicant_two.get("Additional Income (Annual)", {}).get("Irregular Overtime", 0)
	rental_1 = applicant_one.get("Outgoings", {}).get("Household", {}).get("Mortgage / Rent", 0)
	rental_2 = applicant_two.get("Outgoings", {}).get("Household", {}).get("Mortgage / Rent", 0)

	applicant_data["netmonthly_1"] = netmonthly_1
	applicant_data["netmonthly_2"] = netmonthly_2
	applicant_data["additional_1"] = additional_1
	applicant_data["additional_2"] = additional_2
	applicant_data["rental_1"] = rental_1
	applicant_data["rental_2"] = rental_2

	remuneration = netmonthly_1 + netmonthly_2 + additional_1 + additional_2 + rental_1 + rental_2

	value_dependant1 = len(applicant_one.get("dependants"))
	value_dependant2 = len(applicant_two.get("dependants")) if applicant_two.get("dependants") else 0
	app_one_children = applicant_one.get("Outgoings", {}).get("Children", 0)
	app_two_children = applicant_two.get("Outgoings", {}).get("Children", 0)

	applicant_data["childcare"] = 0 if app_one_children in null else app_one_children + 0 if app_two_children in null else app_two_children
	applicant_data["insurance"] = 0
	applicant_data["tax"] = 0
	applicant_data["alimony"] = 0
	applicant_data["other"] = 0
	applicant_data["credit_card"] = 0 if applicant_one["Outgoings"].get("Credit Commitments") in null else applicant_one["Outgoings"].get("Credit Commitments")
	applicant_data["loan"] = 0
	applicant_data["payment"] = 0
	applicant_data["other_mort"] = 0
	applicant_data["monthly_other"] = 0
	applicant_data["value_older2"] = 0


	applicant_dependant = 0
	attributes = [
		{"dependents":0.0,"applicant1":621.0,"applicant2":959.0},
		{"dependents":1.0,"applicant1":771.0,"applicant2":1109.0},
		{"dependents":2.0,"applicant1":921.0,"applicant2":1259.0},
		{"dependents":3.0,"applicant1":1071.0,"applicant2":1409.0},
		{"dependents":4.0,"applicant1":1221.0,"applicant2":1559.0},
		{"dependents":5.0,"applicant1":1371.0,"applicant2":1709.0},
		{"dependents":6.0,"applicant1":1521.0,"applicant2":1859.0},
		{"dependents":7.0,"applicant1":1671.0,"applicant2":2009.0},
		{"dependents":8.0,"applicant1":1821.0,"applicant2":2159.0},
		{"dependents":9.0,"applicant1":1971.0,"applicant2":2309.0},
		{"dependents":10.0,"applicant1":2121.0,"applicant2":2459.0}
	]

	for attribute in attributes:
		current_dependents = float(attribute["dependents"])
		
		if num_of_applicants == 2 and current_dependents == float(num_of_dependants):
			applicant_dependant = attribute["applicant2"]
			break
		elif num_of_applicants == 1 and current_dependents == float(num_of_dependants):
			applicant_dependant = attribute["applicant1"]
			break
		elif current_dependents == 10.0:
			applicant_dependant = attribute["applicant1"]
			break
			
	min_net_disposable = applicant_dependant

	return applicant_data, num_of_dependants, remuneration, min_net_disposable

def council_tax(data):
	prop_tax = (data["Mortgage Requirement"].get("Purchase Price", 0) * 0.0075) / 12
	tax = 0

	if tax > prop_tax:
		council_tax_amount = tax
	else:
		council_tax_amount = prop_tax
		
	return council_tax_amount

def discretionary_spend_calc(remuneration):
	discretionary_spend_value = 0
	threshold = 2561.0
	less_threshold = 25.0
	greater_threshold = 15.0
	less_threshold_percent = less_threshold / 100
	greater_threshold_percent = greater_threshold / 100

	if remuneration <= threshold:
		discretionary_spend_value = remuneration * less_threshold_percent
	elif remuneration > threshold:
		discretionary_spend_value = (threshold * less_threshold_percent) + ((remuneration - threshold) * greater_threshold_percent)

	return discretionary_spend_value

def get_surplus_amount(ltv):
	surplus_amount = 0.0
	surplus_remuneration = 0.0

	surplus_data = [
		{"upperLimit": 95.0, "lowerLimit": 94.01, "surplusAmount": 400.0, "surplusRemuneration": 0.0},
		{"upperLimit": 94.0, "lowerLimit": 93.01, "surplusAmount": 360.0, "surplusRemuneration": 0.0},
		{"upperLimit": 93.0, "lowerLimit": 92.01, "surplusAmount": 320.0, "surplusRemuneration": 0.0},
		{"upperLimit": 92.0, "lowerLimit": 91.01, "surplusAmount": 280.0, "surplusRemuneration": 0.0},
		{"upperLimit": 91.0, "lowerLimit": 90.01, "surplusAmount": 240.0, "surplusRemuneration": 0.0},
		{"upperLimit": 90.0, "lowerLimit": 85.01, "surplusAmount": 100.0, "surplusRemuneration": 0.0},
		{"upperLimit": 85.0, "lowerLimit": 0.01, "surplusAmount": 0.0, "surplusRemuneration": 0.0}
	]

	for entry in surplus_data:
		if entry["lowerLimit"] <= ltv <= entry["upperLimit"]:
			surplus_amount = entry["surplusAmount"]
			surplus_remuneration = entry["surplusRemuneration"]
			break

	return surplus_amount, surplus_remuneration

def get_stress_rate(ltv, product_term):
	stress_rate = 0
	if product_term == 2 :
		product_type = "2 Year Fixed"
	elif product_term == 5:
		product_type = "5 Year Fixed"
	else:
		product_type = "Self-Build"

	tiers = [
		{"ltvTier": 60.0, "productType": "Self-Build|DSVR 2 Year|2 Year Fixed|5 Year Fixed|Green 5 Year Fixed|Green 2 Year DSVR",
		 "correspondingRates": "10.95|7.79|7.15|6.99|6.89|7.69"},
		{"ltvTier": 75.0, "productType": "Self-Build|DSVR 2 Year|2 Year Fixed|5 Year Fixed|Green 5 Year Fixed|Green 2 Year DSVR",
		 "correspondingRates": "10.95|7.96|7.19|6.99|6.89|7.86"},
		{"ltvTier": 80.0, "productType": "Self-Build|DSVR 2 Year|2 Year Fixed|5 Year Fixed|Green 5 Year Fixed|Green 2 Year DSVR",
		 "correspondingRates": "10.95|7.96|7.25|7.09|6.99|7.86"},
		{"ltvTier": 85.0, "productType": "Self-Build|DSVR 2 Year|2 Year Fixed|5 Year Fixed|Green 5 Year Fixed|Green 2 Year DSVR",
		 "correspondingRates": "10.95|8.44|7.29|7.25|7.15|8.34"},
		{"ltvTier": 90.0, "productType": "Self-Build|DSVR 2 Year|2 Year Fixed|5 Year Fixed|Green 5 Year Fixed|Green 2 Year DSVR",
		 "correspondingRates": "10.95|9.19|7.29|7.30|7.20|9.09"},
		{"ltvTier": 95.0, "productType": "Self-Build|DSVR 2 Year|2 Year Fixed|5 Year Fixed|Green 5 Year Fixed|Green 2 Year DSVR",
		 "correspondingRates": "10.95|9.75|8.49|8.49|8.39|9.75"}
	]

	for tier in tiers:
		if ltv <= tier["ltvTier"]:
			product_types = tier["productType"].split("|")
			corresponding_rates = tier["correspondingRates"].split("|")

			if product_type in product_types:
				stress_rate = float(corresponding_rates[product_types.index(product_type)])
				break

	return stress_rate

def get_result(data):
	mortAmount, propValue, mortTerm, ltv, product_term= get_mortgage_data(data)
	applicants, num_of_dependants, remuneration, min_net_disposable = get_applicants(data)
	surplus_amount, surplus_remuneration = get_surplus_amount(ltv)
	stress_rate = get_stress_rate(ltv, product_term)
	discretionary_spend = discretionary_spend_calc(remuneration)
	total_outgoings = sum(v for category in data.get("Outgoings", {}).values() if category is not None for v in category.values())

	livingCost_used = min_net_disposable
	co_ownership_value = 0
	tax = council_tax(data)
	monthly_outgoings = total_outgoings
	ltv_rate = ltv/100
	stress_repayment = round((mortAmount/((1-(math.pow((1/(1+(stress_rate/100))),mortTerm)))/(stress_rate/100))/12),2)
	net_disposable = (remuneration - livingCost_used - discretionary_spend - tax - monthly_outgoings - co_ownership_value - stress_repayment)
	#print("net_disposable : ",net_disposable)
	surplus_remuneration = ((surplus_remuneration / 100) * remuneration)
	#print("surplusRemuneration : ", surplus_remuneration)
	required_surplus = max(surplus_remuneration, surplus_amount)
	criteria = ""
	if net_disposable>=required_surplus:
		criteria = "Criteria Met"
	else:
		criteria = "Not Affordable or Criteria Not Met"

	result = net_disposable - required_surplus

	return ltv, stress_repayment, result, criteria

def main(config_file):
	with open(config_file) as file:
		data = json.load(file)

	ltv, stress_repayment, result, criteria = get_result(data)
	print("Loan to Value (LTV) : ",round(ltv, 2),"%")
	print("Stress Repayment Amount : £",stress_repayment)
	print("Affordability Result : ",criteria)
	# print(result)
	print("\n")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
	main(config_file)
