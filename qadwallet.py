import argparse

from eth_account import Account
from web3 import Web3, HTTPProvider

from units import get_scaled_amount


PRIVATE_KEY = 'b99ce93d31b3b904da617b86c9bc20ad6f4dca39815e9eaa9afc2f249027af44'

HTTP_PROVIDER_URL = 'https://sokol.poa.network'

messages = {
    'balance': 'Balance on "{address}" is {amount} {unit}',
}

w3 = Web3(HTTPProvider(HTTP_PROVIDER_URL))

parser = argparse.ArgumentParser(description='Some program')
parser.add_argument('--key', type=str, help='Insert here your wallet key')
parser.add_argument('--to', type=str, help='Insert wallet key to transfer')
parser.add_argument('--value', type=str, help='Insert value')
parser.add_argument('----tx', type=str, help='Get transaction info hash')

args = parser.parse_args()


def drop_hex_prefix(hex_str):
    return hex_str[2:]


def main():
    key = args.key
    account = Account.privateKeyToAccount(key)

    amount, unit = get_scaled_amount(w3.eth.getBalance(account.address))

    message = messages['balance'].format(
        address=drop_hex_prefix(account.address),
        amount=amount,
        unit=unit
    )
    print(message)


if __name__ == '__main__':
    main()
