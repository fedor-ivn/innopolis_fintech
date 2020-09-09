import json
import time

from web3 import Web3, HTTPProvider
import logging


ACCOUNT_FILE = 'account.json'
NETWORK_FILE = 'network.json'
DATABASE_FILE = 'database.json'
CONTRACT_NAME = 'registrar'

TRANSACTION_GAS = 21000
GAS_PRICE = Web3.toWei(1, 'gwei')


def get_json_data(filename):
    with open(filename) as file:
        return json.load(file)


def transact_action(w3, account, action, nonce):
    gas = action.estimateGas({
        'from': account.address
    })
    tx = action.buildTransaction({
        'from': account.address,
        'gas': gas,
        'gasPrice': w3.toWei(1, 'Gwei'),
        'nonce': nonce
    })
    tx = account.signTransaction(tx)
    return w3.eth.sendRawTransaction(tx.rawTransaction)


private_key = get_json_data(ACCOUNT_FILE)['account']

network_data = get_json_data(NETWORK_FILE)

w3_sokol = Web3(HTTPProvider(network_data['sokol']['rpcUrl']))
w3_kovan = Web3(HTTPProvider(network_data['kovan']['rpcUrl']))

account = w3_sokol.eth.account.privateKeyToAccount(private_key)


def load_contract(w3, abi_path, address):
    abi = get_json_data(abi_path)
    return w3.eth.contract(abi=abi, address=address)


left_side_address, left_side_start_block = get_json_data('build/LeftSide/receipt.json').values()
left_side = load_contract(
    w3_kovan, 'build/LeftSide/LeftSide.abi', left_side_address
)

right_side_address, right_side_start_block = get_json_data('build/RightSide/receipt.json').values()
right_side = load_contract(
    w3_sokol, 'build/RightSide/RightSide.abi', right_side_address
)

print(left_side.functions.tokenAddress().call())
left_side_last_block = w3_sokol.eth.blockNumber
logs = left_side.events.TokenLocked.getLogs(fromBlock=left_side_start_block)
print(logs)

nonce_sokol = w3_sokol.eth.getTransactionCount(account.address)
nonce_kovan = w3_kovan.eth.getTransactionCount(account.address)


from_sokol = from_kovan = to_sokol = to_kovan = 0


while True:
    logging.debug('hello')
    to_sokol, to_kovan = w3_sokol.eth.blockNumber, w3_kovan.eth.blockNumber

    logs_sokol = right_side.events.TokenBurnt.getLogs(fromBlock=from_sokol)
    for log in logs_sokol:
        print(log)
        relay_confirmed = left_side.functions.relayConfirmed(
            log.args.sender, log.args.amount, log.transactionHash
        )
        try:
            tx_hash = transact_action(w3_kovan, account, relay_confirmed, nonce_kovan)
        except ValueError as e:
            print(e)
            continue
        nonce_kovan += 1

    logs_kovan = left_side.events.TokenLocked.getLogs(fromBlock=from_kovan)
    for log in logs_kovan:
        print(log)
        relay_confirmed = right_side.functions.relayConfirmed(
            log.args.sender, log.args.amount, log.transactionHash
        )
        try:
            tx_hash = transact_action(w3_sokol, account, relay_confirmed, nonce_sokol)
        except ValueError as e:
            print(e)
            continue
        nonce_sokol += 1

    from_sokol, from_kovan = to_sokol + 1, to_kovan + 1

    time.sleep(5)
