from web3 import Web3, HTTPProvider
import random
import string
from eth_account import Account
from web3.middleware import geth_poa_middleware
import os
import json

# Address of the deployed RaceRoninChain contract
contract_address = "CONTRACT_ADDRESS"
node_rpc = "CHAINSTACK_NODE_ENDPOINT"

# Players that will enter the race
player1_private_key = "PRIVATE_KEY"
player2_private_key = "PRIVATE_KEY"
player3_private_key = "PRIVATE_KEY"
player4_private_key = "PRIVATE_KEY"

# Initialize web3 connection and inject the PoA middleware to work on Ronin
w3 = Web3(HTTPProvider(node_rpc))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Correctly set the chain id of the network
chain_id = 2021  # Ronin mainnet is 2020; Ronin Saigon testnet is 2021.

# Generate random predictions — "I'm feeling lucky"
def generate_predictions():
    return [''.join(random.choices(string.ascii_lowercase + string.digits, k=3)) for _ in range(50)]

player1_predictions = generate_predictions()
player2_predictions = generate_predictions()
player3_predictions = generate_predictions()
player4_predictions = generate_predictions()

print("Player 1 Predictions:", player1_predictions)
print("Player 2 Predictions:", player2_predictions)
print("Player 3 Predictions:", player3_predictions)
print("Player 4 Predictions:", player4_predictions)

# Load the contract ABI
with open("../abi/RaceRoninChain.abi", "r") as abi_file:
    contract_abi = abi_file.read()

contract = w3.eth.contract(address=contract_address, abi=contract_abi)

def create_race(player_private_key, start_block_offset=20):
    account = Account.from_key(player_private_key)
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Create a race
    start_block = w3.eth.get_block('latest')['number'] + start_block_offset
    end_block = start_block + 50
    create_race_txn = contract.functions.createRace(start_block).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'chainId': chain_id,
        'value': 0,
        'gas': 1000000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })
    signed_create_race_txn = w3.eth.account.sign_transaction(create_race_txn, player_private_key)
    create_race_tx_hash = w3.eth.send_raw_transaction(signed_create_race_txn.rawTransaction)
    print(f"Creating race with tx hash: {create_race_tx_hash.hex()}")
    
    # Wait for the transaction to be mined
    create_race_receipt = w3.eth.wait_for_transaction_receipt(create_race_tx_hash)

    
    # The race ID is incremented and starts from 1, fetch the latest race ID
    race_id = contract.functions.nextRaceId().call() - 1
    print(f"Race created successfully! Race ID: {race_id}, Start Block: {start_block}, End Block: {end_block}")
    return race_id

def enter_race(player_private_key, race_id, predictions, player_number):
    account = Account.from_key(player_private_key)
    nonce = w3.eth.get_transaction_count(account.address)
    
    # Enter race
    enter_race_txn = contract.functions.enterRace(race_id, predictions).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'chainId': chain_id,
        'value': w3.to_wei(1, 'ether'),  # Entry fee is 1 RON
        'gas': 3000000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })
    signed_enter_race_txn = w3.eth.account.sign_transaction(enter_race_txn, player_private_key)
    enter_race_tx_hash = w3.eth.send_raw_transaction(signed_enter_race_txn.rawTransaction)
    print(f"Player {player_number} entering race with tx hash: {enter_race_tx_hash.hex()}")
    
    # Wait for the transaction to be mined
    enter_race_receipt = w3.eth.wait_for_transaction_receipt(enter_race_tx_hash)


# Create race with player 1
race_id = create_race(player1_private_key)

# Player 1 enters the race
enter_race(player1_private_key, race_id, player1_predictions, 1)

# Player 2 enters the race
enter_race(player2_private_key, race_id, player2_predictions, 2)

# Player 3 enters the race
enter_race(player3_private_key, race_id, player3_predictions, 3)

# Player 4 enters the race
enter_race(player4_private_key, race_id, player4_predictions, 4)
