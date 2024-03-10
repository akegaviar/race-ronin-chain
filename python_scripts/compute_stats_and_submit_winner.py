from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware
from eth_account import Account
import argparse
import json

# Address of the deployed RaceRoninChain contract
contract_address = "CONTRACT_ADDRESS"
owner_private_key = "DEPLOYER_PRIVATE_KEY"
node_rpc = "CHAINSTACK_NODE_ENDPOINT"

print("Initializing Web3 connection...")
w3 = Web3(Web3.HTTPProvider(node_rpc))

print("Applying PoA middleware for Ronin...")
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

print("Loading contract...")
with open("../abi/RaceRoninChain.abi", 'r') as abi_definition:
    contract_abi = json.load(abi_definition)
contract = w3.eth.contract(address=contract_address, abi=contract_abi)

print("Initializing the submitWinner owner account from private key...")
account = Account.from_key(owner_private_key)

def get_race_details(race_id):
    print(f"Fetching details for race {race_id}...")
    return contract.functions.getRaceDetails(race_id).call()

def get_player_predictions(race_id):
    race_details = get_race_details(race_id)
    player_addresses = race_details[6]
    player_predictions = {}
    for player in player_addresses:
        predictions = contract.functions.getPlayerPredictions(race_id, player).call()
        player_predictions[player] = predictions
    print(f"Retrieved predictions for {len(player_predictions)} players.")
    return player_predictions

def fetch_block_hashes(start_block, end_block):
    print(f"Fetching block hashes from block {start_block} to {end_block}...")
    block_hashes = [(block_number, w3.eth.get_block(block_number).hash.hex()) for block_number in range(start_block, end_block + 1)]
    print(f"Fetched {len(block_hashes)} block hashes.")
    return block_hashes

def calculate_matches(predictions, block_hashes):
    print("Calculating matches...")
    matches_info = []
    for prediction in predictions:
        for block_number, block_hash in block_hashes:
            if prediction in block_hash:
                matches_info.append((prediction, block_number))
                break  # Move to the next prediction after the first match
    print(f"Total block hash matches found: {len(matches_info)}")
    return matches_info

def find_winner(player_predictions, block_hashes):
    print("Determining the winner and printing stats for all players...")
    scores = {}
    for player, predictions in player_predictions.items():
        matches_info = calculate_matches(predictions, block_hashes)
        scores[player] = len(matches_info)
        print(f"Player {player} stats:")
        for prediction, block_number in matches_info:
            print(f"  Matched prediction: {prediction} against Block Number: {block_number}")
        print(f"  Final score: {scores[player]}")
    winner = max(scores, key=scores.get)
    print(f"Winner found: {winner} with score {scores[winner]}")
    return winner, scores[winner]

def submit_winner(race_id, winner, winner_predictions):
    print(f"Submitting winner for race {race_id}...")
    nonce = w3.eth.get_transaction_count(account.address)
    submit_txn = contract.functions.submitWinner(race_id, winner, winner_predictions).build_transaction({
        'from': account.address,
        'nonce': nonce,
        'gas': 5000000,
        'gasPrice': w3.to_wei('50', 'gwei')
    })
    signed_txn = w3.eth.account.sign_transaction(submit_txn, owner_private_key)
    tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    print(f"Winner submitted for race {race_id}. Transaction receipt: {receipt}")

def main():
    print("Fetching the latest race ID...")
    # Subtract 1 from nextRaceId to get the latest race ID since nextRaceId is always pointing to the next to be created race ID
    latest_race_id = contract.functions.nextRaceId().call() - 1

    if latest_race_id == 0:
        print("No races have been created yet.")
        return

    print(f"Fetching details for the latest race ID: {latest_race_id}...")
    race_details = get_race_details(latest_race_id)

    # Fetch the latest block number from the chain
    latest_block = w3.eth.block_number
    if race_details[2] > latest_block:  # race_details[2] is endBlock
        blocks_remaining = race_details[2] - latest_block
        print(f"The race will complete at block {race_details[2]}, which is currently {blocks_remaining} blocks into the future.")
        return

    print("The race has completed. Proceeding to calculate and submit the winner...")

    player_predictions = get_player_predictions(latest_race_id)
    block_hashes = fetch_block_hashes(race_details[1], race_details[2])  # startBlock and endBlock
    winner, _ = find_winner(player_predictions, block_hashes)
    winner_predictions = player_predictions[winner]
    submit_winner(latest_race_id, winner, winner_predictions)

if __name__ == "__main__":
    main()