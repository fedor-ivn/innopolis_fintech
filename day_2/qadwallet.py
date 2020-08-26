import argparse

from eth_account import Account
from web3 import Web3, HTTPProvider
from web3.exceptions import TransactionNotFound

from day_2.units import get_scaled_amount


TRANSACTION_GAS = 21000

HTTP_PROVIDER_URL = 'https://sokol.poa.network'

messages = {
    'balance': 'Balance on "{address}" is {amount} {unit}',

    'send': 'Payment of {amount} {unit} to "{address}" scheduled\n'
            'Transaction Hash: {transaction_hash}',
    'not_enough_funds': 'No enough funds for payment',

    'transaction_confirmed': 'Payment of {amount} {unit} to "{address}" confirmed',
    'transaction_not_confirmed': 'Delay in payment of {amount} {unit} to "{address}"',
    'transaction_does_not_exist': 'No such transaction in the chain',
}

w3 = Web3(HTTPProvider(HTTP_PROVIDER_URL))

parser = argparse.ArgumentParser(description='Some program')
parser.add_argument('--key', type=str, help='Insert here your wallet key')
parser.add_argument('--to', type=str, help='Insert wallet key to transfer')
parser.add_argument('--value', type=int, help='Insert value')
parser.add_argument('--tx', type=str, help='Get transaction info hash')

args = parser.parse_args()


def drop_hex_prefix(hex_str):
    return hex_str[2:]


def get_balance():
    key = args.key
    account = Account.privateKeyToAccount(key)

    amount, unit = get_scaled_amount(w3.eth.getBalance(account.address))

    message = messages['balance'].format(
        address=drop_hex_prefix(account.address),
        amount=amount,
        unit=unit
    )
    print(message)


def send_transaction(gas_price=Web3.toWei(10, 'gwei')):
    key = args.key
    to = args.to
    value = args.value

    account = Account.privateKeyToAccount(key)
    balance = w3.eth.getBalance(account.address)

    if value + TRANSACTION_GAS * gas_price > balance:
        print(messages['not_enough_funds'])
        return

    tx = {
        'to': to,
        'value': value,
        'gas': TRANSACTION_GAS,
        'gasPrice': gas_price,
        'nonce': w3.eth.getTransactionCount(account.address)
    }

    signed_tx = account.sign_transaction(tx)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    amount, unit = get_scaled_amount(value)

    if len(to) == 42:
        to = drop_hex_prefix(to)

    message = messages['send'].format(
        amount=amount,
        unit=unit,
        address=to,
        transaction_hash=tx_hash.hex()
    )
    print(message)


def get_transaction():
    tx_hash = args.tx
    try:
        tx = w3.eth.getTransaction(tx_hash)
    except TransactionNotFound:
        print(messages['transaction_does_not_exist'])
        return

    amount, unit = get_scaled_amount(tx.value)

    if tx.blockHash is not None:
        message_type = 'transaction_confirmed'
    else:
        message_type = 'transaction_not_confirmed'

    message = messages[message_type].format(
        amount=amount,
        unit=unit,
        address=drop_hex_prefix(tx.to)
    )
    print(message)


def main():
    """
    Основная ф-ция
    Выводит в командную строку информацию на базе агрументов вызова
    """
    if not args.key and not args.tx:
        parser.print_help()
    else:
        if args.key:
            if not args.to:
                get_balance()
            elif args.to and args.value:
                send_transaction()
        elif args.tx:
            get_transaction()


if __name__ == '__main__':
    main()
