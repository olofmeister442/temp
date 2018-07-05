from engine.apis import *
from engine.parsers import *

mobile_number = "7032770360"
account_number = "000401000013"
creditcard_number = "4375510921335003"
creditcard_number_2 = "5000"

#get_user_id(mobile_number)
print("get_user_id working")

#get_account_numbers_original(mobile_number)
print("account numbers fetched with original and is working")

#get_account_numbers(mobile_number)
print("account numbers fetched with ending with and is working")

#get_credit_card_numbers_original(mobile_number)
print("credit card numbers fetched with original and is working")

#get_credit_card_numbers(mobile_number)
print("credit card numbers fetched with ending with and is working")

#recharge_mobile(mobile_number, "10")
print("recharge mobile api, to still check once more, input money is in paise")

#get_balance(account_number)
print("get_balance api, working, available balance is in paise")

#get_credit_card_details(creditcard_number_2)
print("get_credit_card_details, working, due date in yyyymmdd, due amount in ")
print("cust_id from response")

pay_credit_card_bill(mobile_number, creditcard_number_2)
print("pay credit card bill working")

#get_payees(mobile_number)
print("get_payees")
