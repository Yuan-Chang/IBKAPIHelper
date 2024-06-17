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

    for position in position_json:

        name = position['contractDesc']
        cost = position['avgCost'] * position['position']
        market_value = position['mktValue']
        conid = position['conid']

        market_cap = get_market_cap(conid)

        my_dict = {'Name': position['contractDesc'], 'Market Value': market_value,
                   'Total cost': cost, 'conid': conid, 'Market cap': market_cap}

        # Separate out my VOO position result to an independent key
        if name == 'VOO':
            result['VOO'] = my_dict
            continue

        my_array.append(my_dict)

        total_cost = total_cost + cost
        total_market_value = total_market_value + market_value

    result['total_market_value'] = total_market_value
    result['total_cost'] = total_cost
    result['positions'] = my_array

    return result


def get_market_cap(conid):
    request_url = f"{baseUrl}/iserver/marketdata/snapshot?conids={conid}&fields=7289"
    result = requests.get(url=request_url, verify=False).json()
    result = result[0]

    if '7289' in result:
        market_cap = result['7289']
    else:
        return ""

    if not market_cap.endswith('B'):
        raise Exception("Not supporting market cap lower than 1B")

    market_cap = market_cap[:-1]

    return market_cap
