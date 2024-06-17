import requests
import api_helper.ibkr_api as helper
import warnings
warnings.filterwarnings("ignore")


# Document : https://ibkrcampus.com/ibkr-api-page/cpapi-v1/#trades

# Calling this function is required
auth = helper.authenticate()

# Calling this function is required
accounts = helper.get_accounts()

account_id = helper.get_account_id()

positions_json_array = helper.get_positions(account_id)

positions = helper.extract_details_from_positions_json(positions_json_array)
if positions['positions'][0]['Market cap'] == '':
    print("Not getting market value yet, reload again")
    positions = helper.extract_details_from_positions_json(positions_json_array)

gain = positions['total_market_value'] - positions['total_cost']

print(f"Total My list market value: ${positions['total_market_value']}")
print(f"Total VOO market value: ${positions['VOO']['Market Value']}")

print("========================================================")
print(f"Total gain/loss: {round(gain, 2)} ({round(gain / positions['total_cost'], 2)}%)")
print(f"Market value ratio: {round(positions['total_market_value'] / positions['VOO']['Market Value'], 2)}")
