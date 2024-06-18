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

helper.print_overview(positions)

# Set cost limit to each
trade_limit = {
    "ADBE": 30000,
    "INTU": 30000,
    "CRM": 30000,
    "LULU": 10000,
    "PYPL": 20000,
    "SOFI": 10000}

# helper.trade(account_id, positions, trade_limit)

# helper.cancel_all_open_orders(account_id)
