import json

def get_mortgage_amount(num_of_applicants, income1, income2):
	applicant_number = 2 if num_of_applicants>2 else num_of_applicants
	if applicant_number==1:
		max_borrowing = income1 * 4.5
	else:
		max_borrowing = (income1+income2)*4

	return max_borrowing

def get_monthly_repayment_amount(loan_amount, interest_rate, loan_term, repayment_type):
    try:
        B1 = float(loan_amount)
        interest_rate = float(interest_rate)
        B4 = int(loan_term)

        if repayment_type == "Repayment":
            B2 = interest_rate / 100
            B3 = B2 / 12
            B5 = B4 * 12
            temp1 = 1 + B3
            temp2 = temp1 ** B5
            mon_repayment = (B1 * (B3 * temp2)) / (temp2 - 1)
            return round(mon_repayment, 2)
        else:
            B2 = interest_rate / 100
            B3 = B2 / 12
            B5 = B4 * 12
            temp1 = 1 + B3
            temp2 = temp1 ** B5
            intrest_only = B1 * B3
            return round(intrest_only, 2)
    except Exception as e:
        return e

def main(config_file):
	with open(config_file) as file:
		data = json.load(file)

	loan_amount = data["Mortgage Requirement"].get("Loan Amount", 0)
	interest_rate = 1
	loan_term_years = int(data["Mortgage Requirement"].get("Loan Term", 0)/12)
	repayment_type = data["Mortgage Requirement"].get("Payment Method")

	num_of_applicants = data.get("No of Applicant")
	income1 = data["Client Details"][0]["Employment Details"].get("Basic Annual Income", 0)
	if num_of_applicants>1:
		income2 = data["Client Details"][1]["Employment Details"].get("Basic Annual Income", 0)
	else:
		income2 = 0

	max_affordable = get_mortgage_amount(num_of_applicants, income1, income2)
	print("Max Affordable : ", max_affordable)

	repay = get_monthly_repayment_amount(loan_amount, interest_rate, loan_term_years, repayment_type)
	print("Monthly Repayment : ", repay)
	print("\n")

config_files = ["config_one.json", "config_two.json", "config_three.json", "config_four.json", "config_five.json", "config_six.json", "config_seven.json"]
for config_file in config_files:
    main(config_file)