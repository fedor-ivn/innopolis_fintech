from web3 import Web3, HTTPProvider
import logging

from day_8.deploy_utils import get_json_data, deploy_contract, send_contract_transaction

ACCOUNT_FILE = 'account.json'
NETWORK_FILE = 'network.json'


def main():
    logging.basicConfig(level=logging.DEBUG)
    private_key = get_json_data(ACCOUNT_FILE)['account']

    network_data = get_json_data(NETWORK_FILE)

    w3_sokol = Web3(HTTPProvider(network_data['sokol']['rpcUrl']))
    w3_kovan = Web3(HTTPProvider(network_data['kovan']['rpcUrl']))

    account = w3_sokol.eth.account.privateKeyToAccount(private_key)

    left_side_token_kwargs = {
        'name': 'School Token',
        'symbol': 'STK',
        'decimals': 18,
        'total': 10 ** 6
    }
    left_side_token = deploy_contract(
        w3_kovan, account, 'src/erc20token.sol', 'ERC20', left_side_token_kwargs
    )

    left_side_bridge_kwargs = {
        '_oracle': account.address,
        '_token': left_side_token.contractAddress
    }
    left_side_bridge = deploy_contract(
        w3_kovan, account, 'src/LeftSide.sol', 'LeftSide', left_side_bridge_kwargs
    )

    right_side_bridge_kwargs = {
        '_oracle': account.address
    }
    right_side_bridge = deploy_contract(
        w3_sokol, account, 'src/RightSide.sol', 'RightSide', right_side_bridge_kwargs
    )

    right_side_token_kwargs = {
        'name': 'School Token',
        'symbol': 'STK',
        'decimals': 18,
        'minter': right_side_bridge.contractAddress
    }
    right_side_token = deploy_contract(
        w3_sokol, account, 'src/erc20minted.sol', 'MintToken', right_side_token_kwargs
    )

    abi = get_json_data(f'build/RightSide/RightSide.abi')
    contract = w3_sokol.eth.contract(address=right_side_bridge.contractAddress, abi=abi)
    send_contract_transaction(
        w3_sokol, account, contract.functions.setTokenAddress(right_side_token.contractAddress)
    )


if __name__ == '__main__':
    main()
