#!/usr/bin/env python3

# from os.path import expanduser
from web3 import Web3
from web3.middleware import geth_poa_middleware
from tests.deploy import deploy_contract
import json

# Deployment parameters
# PROVIDER_URI = expanduser('~/.ethereum/testnet/geth.ipc')
provider = Web3.HTTPProvider('http://127.0.0.1:8545')
POA = False
FUND_DEV = False
N_COINS = 3
SWAP_DEPLOY_ADDRESS = '0x17635F54E3daa7fD650032dD837caA9eFf75F5b0'
COINS_DEPLOY_ADDRESS = '0x08000dBD1b3990e410F1DA8f1720f958e177EcD9'

HELP = """coins = deploy_test_erc20() to deploy test coins
swap, token = deploy_swap(coins, A, fee) to deploy swap contract from the list
====================================================="""


w3 = Web3(provider)
if POA:
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
if FUND_DEV:
    txhash = w3.eth.sendTransaction({
        'from': w3.eth.accounts[0],
        'to': SWAP_DEPLOY_ADDRESS,
        'value': 10 ** 19})
    w3.eth.waitForTransactionReceipt(txhash)
    txhash = w3.eth.sendTransaction({
        'from': w3.eth.accounts[0],
        'to': COINS_DEPLOY_ADDRESS,
        'value': 10 ** 19})
    w3.eth.waitForTransactionReceipt(txhash)


def deploy_test_erc20():
    return [deploy_contract(
                w3, 'ERC20.vy', COINS_DEPLOY_ADDRESS,
                b'Coin ' + str(i).encode(), str(i).encode(), 18, 10 ** 9
                ).address
            for i in range(N_COINS)]


def deploy_swap(coins, A, fee):
    A = A * 2
    fee = int(fee * 10 ** 10)
    pool_token = deploy_contract(
        w3, 'ERC20.vy', SWAP_DEPLOY_ADDRESS, b'Stableswap', b'STBL', 18, 0)
    swap_contract = deploy_contract(
            w3, ['stableswap.vy', 'ERC20m.vy'], SWAP_DEPLOY_ADDRESS,
            coins, pool_token.address, A, fee)
    txhash = pool_token.functions.set_minter(swap_contract.address).transact(
        {'from': SWAP_DEPLOY_ADDRESS})
    w3.eth.waitForTransactionReceipt(txhash)

    abi = json.dumps(swap_contract.abi, indent=True)
    with open('swap.abi', 'w') as f:
        f.write(abi)
    print('---=== ABI ===---')
    print(abi)
    print('=================')

    return swap_contract, pool_token


if __name__ == '__main__':
    import IPython
    IPython.embed(header=HELP)
