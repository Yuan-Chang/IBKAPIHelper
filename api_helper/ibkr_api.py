import requests

baseUrl = "https://localhost:4999/v1/api"


def authenticate():
    request_url = f"{baseUrl}/sso/validate"
    return requests.get(url=request_url, verify=False).content


def get_accounts():
    request_url = f"{baseUrl}/iserver/accounts"
    return requests.get(url=request_url, verify=False).content


def get_account_id():
    request_url = f"{baseUrl}/portfolio/accounts"
    result = requests.get(url=request_url, verify=False).json()
    return result[0]['accountId']


# Get all my positions in json
def get_positions(account_id):
    request_url = f"{baseUrl}/portfolio/{account_id}/positions/0?direction=a&period=1W&sort=position&model=MyModel"
    return requests.get(url=request_url, verify=False).json()


def extract_details_from_positions_json(position_json):
    result = {}
    my_array = []
    total_market_value = 0.0
    total_cost = 0.0
    total_open_market_value = 0.0

    for position in position_json:
        name = position['contractDesc']
        cost = position['avgCost'] * position['position']
        market_value = position['mktValue']
        conid = position['conid']

        market_data = get_market_data(conid)
        market_cap = market_data['marketCap']
        prior_close = market_data['priorClose']
        open_market_value = float(prior_close) * float(position['position'])

        my_dict = {'Name': position['contractDesc'], 'Market Value': market_value,
                   'Total cost': cost, 'conid': conid, 'Market cap': market_cap,
                   'Prior close': prior_close}

        # Separate out my VOO position result to an independent key
        if name == 'VOO':
            result['VOO'] = my_dict
            continue

        my_array.append(my_dict)

        total_cost = total_cost + cost
        total_market_value = total_market_value + market_value
        total_open_market_value = total_open_market_value + open_market_value

    result['total_market_value'] = total_market_value
    result['total_cost'] = total_cost
    result['total_open_market_value'] = total_open_market_value
    result['positions'] = my_array

    return result


def get_market_data(conid):
    request_url = f"{baseUrl}/iserver/marketdata/snapshot?conids={conid}&fields=7289,7741"
    result = requests.get(url=request_url, verify=False).json()
    result = result[0]

    if '7289' in result:
        market_cap = result['7289']

        if not market_cap.endswith('B'):
            raise Exception("Not supporting market cap lower than 1B")

        market_cap = market_cap[:-1]
    else:
        market_cap = 0

    if '7741' in result:
        prior_close = result['7741']
    else:
        prior_close = 0

    result['marketCap'] = market_cap
    result['priorClose'] = prior_close

    return result


def print_overview(positions):
    gain = positions['total_market_value'] - positions['total_cost']
    daily_gain = positions['total_market_value'] - positions['total_open_market_value']

    print(f"Total My list market value: ${positions['total_market_value']}")
    print(f"Total VOO market value: ${positions['VOO']['Market Value']}")

    print("========================================================")
    print(f"Total gain/loss: {round(gain, 2)} ({round(gain / positions['total_cost'], 2)}%)")
    print(f"Daily gain/loss: {round(daily_gain, 2)} ({round(daily_gain / positions['total_open_market_value'], 2)}%)")
    print(f"Market value ratio: {round(positions['total_market_value'] / positions['VOO']['Market Value'], 2)}")


def trade(account_id, positions, trade_limit):
    position_list = positions['positions']

    for position in position_list:
        conid = position['conid']
        ticker = position['Name']
        limit = trade_limit[ticker]
        cost = position['Total cost']

        if cost <= limit:
            request_url = f"{baseUrl}/iserver/account/{account_id}/orders"
            json_content = {
                "orders": [
                    {
                        "acctId": f"{account_id}",
                        "conid": conid,
                        "orderType": "MKT",
                        "side": "BUY",
                        "ticker": ticker,
                        "tif": "DAY",
                        "cashQty": 500
                    }
                ]
            }
            response = requests.post(url=request_url, json=json_content, verify=False).json()
            print(ticker)
            while "order_status" not in response[0]:
                id = response[0]['id']
                request_url = f"{baseUrl}/iserver/reply/{id}"
                json_content = {"confirmed": True}
                response = requests.post(url=request_url, json=json_content, verify=False).json()
            print(f"reply trading order:{response}")


def cancel_order(account_id, order_id):
    request_url = f"{baseUrl}/iserver/account/{account_id}/order/{order_id}"
    result = requests.delete(url=request_url, verify=False).json()
    print(result)


def cancel_all_open_orders(account_id):
    request_url = f"{baseUrl}/iserver/account/{account_id}/order/{-1}"
    result = requests.delete(url=request_url, verify=False).json()
    print(result)