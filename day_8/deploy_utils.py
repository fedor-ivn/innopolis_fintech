import logging
import errno
import json
import os
import re
from subprocess import check_output

from web3 import Web3, HTTPProvider

CONTRACT_TRANSACTION_GAS = 4 * 10 ** 6
GAS_PRICE = 10


def get_json_data(filename):
    with open(filename) as file:
        return json.load(file)


def save_json_data(data, filename):
    with open(filename, 'w') as file:
        return json.dump(data, file)


def send_transaction(w3, account, tx):
    tx_signed = account.signTransaction(tx)
    tx_hash = w3.eth.sendRawTransaction(tx_signed.rawTransaction)
    return w3.eth.waitForTransactionReceipt(tx_hash)


def send_contract_transaction(w3, account, contract_function, tx_extra=None):
    if tx_extra is None:
        tx_extra = dict()

    tx = contract_function.buildTransaction(
        {
            'from': account.address,
            'nonce': w3.eth.getTransactionCount(account.address),
            'gas': CONTRACT_TRANSACTION_GAS,
            'gasPrice': w3.toWei(GAS_PRICE, 'gwei'),
        }
    )
    tx.update(**tx_extra)
    return send_transaction(w3, account, tx)


def create_dirs(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


def deploy_contract(w3, account, filename, contract_name, contract_kwargs=None):
    if contract_kwargs is None:
        contract_kwargs = dict()

    name = os.path.splitext(os.path.basename(filename))[0]
    build_path = f'build/{name}'
    compiler_args = [
        "solc", "--optimize", "--bin", "--abi",
        '-o', build_path, filename
    ]
    logging.info('Running solc compiler...')
    solc_output = check_output(compiler_args).decode()
    logging.debug(solc_output)

    with open(os.path.join(build_path, f'{contract_name}.bin')) as file:
        bytecode = file.read()

    abi = get_json_data(os.path.join(build_path, f'{contract_name}.abi'))
    logging.info('Compiled successfully!')

    logging.info('Sending transaction...')
    contract = w3.eth.contract(bytecode=bytecode, abi=abi)
    tx_receipt = send_contract_transaction(
        w3, account, contract.constructor(**contract_kwargs)
    )
    logging.info(f'Transaction "{tx_receipt.transactionHash}" has been sent successfully!')

    logging.info('Saving transaction receipt...')
    base = f'build/{name}/'

    tx_data = {
        'contractAddress': tx_receipt.contractAddress,
        'blockNumber': tx_receipt.blockNumber
    }
    save_json_data(tx_data, os.path.join(base, 'receipt.json'))
    logging.info('Build results has been saved successfully!')

    return tx_receipt

