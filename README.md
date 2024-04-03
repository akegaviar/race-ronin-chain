
<img width="1200" alt="Labs" src="https://user-images.githubusercontent.com/99700157/213291931-5a822628-5b8a-4768-980d-65f324985d32.png">

<p align="center">
 <h3 align="center">Chainstack is the leading suite of services connecting developers with Web3 infrastructure</h3>
</p>

<p align="center">
  <a target="_blank" href="https://chainstack.com/build-better-with-ethereum/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/Ethereum.svg" /></a>&nbsp;  
  <a target="_blank" href="https://chainstack.com/build-better-with-bnb-smart-chain/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/BNB.svg" /></a>&nbsp;
  <a target="_blank" href="https://chainstack.com/build-better-with-polygon/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/Polygon.svg" /></a>&nbsp;
  <a target="_blank" href="https://chainstack.com/build-better-with-avalanche/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/Avalanche.svg" /></a>&nbsp;
  <a target="_blank" href="https://chainstack.com/build-better-with-solana/"><img src="https://github.com/soos3d/blockchain-badges/blob/main/protocols_badges/Solana.svg" /></a>&nbsp;
</p>

<p align="center">
  <a target="_blank" href="https://chainstack.com/protocols/">Supported protocols</a> •
  <a target="_blank" href="https://chainstack.com/blog/">Chainstack blog</a> •
  <a target="_blank" href="https://docs.chainstack.com/quickstart/">Chainstack docs</a> •
  <a target="_blank" href="https://docs.chainstack.com/quickstart/">Blockchain API reference</a> •
  <a target="_blank" href="https://console.chainstack.com/user/account/create">Start for free</a>
</p>

# Race Ronin Chain

An (almost) on-chain game where you race the Ronin chain based on block hashes using the Foundry framework.

See the full details in the Chainstack Developer Portal — [Ronin: On-Chain meta racing game](https://docs.chainstack.com/docs/ronin-on-chain-meta-racing-game)

## Prerequisites

Before you start, ensure you have the following:

- **Chainstack account**: Needed to deploy a Ronin node. [Start for free](https://chainstack.com/).
- **Foundry**: Used for compiling, testing, and deploying the contract. Follow the installation instructions [here](https://getfoundry.sh/).
- **web3.py**: Necessary for participation and winner calculation & submission scripts. Installation can be done via pip: `pip install web3`.

## Quick Start

1.  **Clone the repository**: Access all necessary files for the game.

    ```
    git clone https://github.com/Chainstacklabs/race-ronin-chain.git
    cd race-ronin-chain
    ```

2.  **Add your Chainstack RPC node**: Add your Chainstack RPC node URL to the `foundry.toml` file.

    ```
    [profile.default]
    version = "0.8.19"
    src = "src"
    out = "out"
    libs = ["lib"]
    eth_rpc_url = "CHAINSTACK_NODE_ENDPOINT"
    ```

3.  **Generate the contract ABI**: If you modify the contract, generate a new ABI with:

```

forge build --silent && jq '.abi' ./out/RaceRoninChain.sol/RaceRoninChain.json > ./abi/RaceRoninChain.abi

```

3. **Deploy the contract**: Ronin does not support EIP-1559, so use legacy transactions.

```

forge create src/RaceRoninChain.sol:RaceRoninChain --private-key YOUR_PRIVATE_KEY --constructor-args TREASURY_ADDRESS --legacy

```

Replace `YOUR_PRIVATE_KEY` with your deployer private key and `TREASURY_ADDRESS` with the address to receive the house fees.

4. **Interact with the contract**: Use the provided Python scripts to enter races and compute & submit winners.

- `enter_race.py`: For generating predictions and entering races.
- `compute_stats_and_submit_winner.py`: For calculating and submitting race winners.

Ensure to provide necessary variables like private keys, addresses, and Chainstack

endpoints within the scripts.

```

```
