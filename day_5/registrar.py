import argparse
import json

import requests
from eth_account.account import Account
from web3 import Web3, HTTPProvider

ACCOUNT_FILE = 'account.json'
NETWORK_FILE = 'network.json'
DATABASE_FILE = 'database.json'
CONTRACT_NAME = 'registrar'

TRANSACTION_GAS = 21000

GAS_PRICE_ORACLE_URL = 'https://gasprice.poa.network'


def get_json_data(filename):
    with open(filename) as file:
        return json.load(file)


private_key = get_json_data(ACCOUNT_FILE)['account']

network_data = get_json_data(NETWORK_FILE)
rpc_url = network_data['rpcUrl']
gas_price_url = network_data['gasPriceUrl']

w3 = Web3(HTTPProvider(rpc_url))

account = Account.privateKeyToAccount(private_key)


def create_parser():
    parser = argparse.ArgumentParser(
        description='Solution to registrar assignment'
    )

    parser.add_argument(
        '--deploy', required=False, action='store_true',
        help='Deploy a contract'
    )

    parser.add_argument(
        '--add', type=str, required=False, metavar='JSON',
        help='Creates connection with yor name and address'
    )

    parser.add_argument(
        '--del', required=False, action='store_true',
        help='Deletes connection with yor name and address'
    )

    parser.add_argument(
        '--getacc', type=str, required=False,
        help='Gets mapping of address to name'
    )

    parser.add_argument(
        '--getname', type=str, required=False,
        help='Get mapping of name to address'
    )

    parser.add_argument(
        '--list', required=False, action='store_true',
        help='Get list of all connections'
    )

    return parser


def get_fast_price():
    resp = requests.get(GAS_PRICE_ORACLE_URL)
    return json.loads(resp.text)['fast']


def deploy():
    bytecode = get_json_data(f'contracts/{CONTRACT_NAME}/bytecode.json')['object']
    abi = get_json_data(f'contracts/{CONTRACT_NAME}/abi.json')
    contract = w3.eth.contract(bytecode=bytecode, abi=abi)
    tx_receipt = send_contract_transaction(contract.constructor())

    data = {
        'registrar': tx_receipt.contractAddress,
        'startBlock': tx_receipt.blockNumber
    }
    with open(DATABASE_FILE, 'w') as file:
        json.dump(data, file)

    print(f'Contract address: {tx_receipt.contractAddress}')


def get_contract():
    address = get_json_data(DATABASE_FILE)['registrar']
    abi = get_json_data(f'contracts/{CONTRACT_NAME}/abi.json')
    contract = w3.eth.contract(address=address, abi=abi)
    return contract


def send_transaction(tx):
    tx_signed = account.signTransaction(tx)
    tx_hash = w3.eth.sendRawTransaction(tx_signed.rawTransaction)
    return w3.eth.waitForTransactionReceipt(tx_hash)


def send_contract_transaction(contract_function, tx_extra=None):
    if tx_extra is None:
        tx_extra = dict()

    tx = contract_function.buildTransaction(
        {
            'from': account.address,
            'nonce': w3.eth.getTransactionCount(account.address),
            'gas': 4 * 10 ** 6,
            'gasPrice': w3.toWei(get_fast_price(), 'gwei'),
        }
    )
    tx.update(**tx_extra)
    return send_transaction(tx)


def add(name):
    contract = get_contract()
    if contract.functions.getName(account.address).call() != '':
        print('One account must correspond one name')
        return

    contract_function = contract.functions.registerName(name)
    try:
        tx_receipt = send_contract_transaction(contract_function)
        print(f'Successfully added by {tx_receipt["from"]}')
    except ValueError:
        print('No enough funds to add name')


def delete():
    contract = get_contract()
    if contract.functions.getName(account.address).call() == '':
        print('No name found for your account')
        return

    contract_function = contract.functions.unregisterName()
    try:
        tx_receipt = send_contract_transaction(contract_function)
        print(f'Successfully deleted by {tx_receipt["from"]}')
    except ValueError:
        print('No enough funds to delete name')


def get_accounts(name):
    contract = get_contract()
    accounts_list = contract.functions.getAddresses(name).call()
    if len(accounts_list) > 1:
        print('Registered accounts are:', *accounts_list, sep='\n')

    elif len(accounts_list) == 1:
        print(f'Registered account is {accounts_list[0]}.')
    else:
        print('No account registered for this name')


def get_name(address):
    print(address)
    contract = get_contract()
    name = contract.functions.getName(address).call()
    if name == "":
        print("No name registered for this account")
    else:
        print("Registered account is \"{}\"".format(name))


def get_list():
    contract = get_contract()
    contract_start_block = get_json_data(DATABASE_FILE)['startBlock']
    reg_event_filter = contract.events.NameRegistered.createFilter(fromBlock=contract_start_block)
    reg_entries = reg_event_filter.get_all_entries()
    unreg_event_filter = contract.events.NameUnregistered.createFilter(fromBlock=contract_start_block)
    unreg_entries = unreg_event_filter.get_all_entries()

    sorted_entries = sorted(reg_entries + unreg_entries, key=lambda e: e.blockNumber)

    pairs = {}
    for entry in sorted_entries:
        if entry.event == 'NameRegistered':
            pairs[entry.args['_address']] = entry.args['_name']
        elif entry.event == 'NameUnregistered':
            del pairs[entry.args['_address']]

    print(*[f'"{name}": {address}' for address, name in pairs.items()], sep='\n')


if __name__ == '__main__':
    parser = create_parser()
    args = parser.parse_args()

    if args.deploy:
        deploy()

    if args.add:
        add(args.add)

    if vars(args)['del']:
        delete()

    if args.getacc:
        get_accounts(args.getacc)

    if args.getname:
        get_name(account.address)

    if args.list:
        get_list()
