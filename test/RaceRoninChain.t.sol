// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "../src/RaceRoninChain.sol";

contract RaceRoninChainTest is Test {
    RaceRoninChain raceRoninChain;
    address payable treasury;
    address[] players = new address[](4);

    function setUp() public {
        treasury = payable(address(0));
        raceRoninChain = new RaceRoninChain(treasury);
        // Setup 4 players with 1 ether each
        for(uint i = 0; i < 4; i++) {
            players[i] = address(uint160(uint(keccak256(abi.encodePacked(i)))));
            vm.deal(players[i], 1 ether);
        }
    }

    function generatePredictions() internal pure returns (string[] memory) {
        string[] memory predictions = new string[](50);
        for(uint i = 0; i < 50; i++) {
            predictions[i] = "ABC"; // Simplified for this example.
        }
        return predictions;
    }

    function testRaceProcess() public {
        address owner = address(this); // Sets the owner to later call submitWinner
        // Player 1 creates a race
        vm.startPrank(players[0]);
        uint256 startBlock = block.number + 1;
        raceRoninChain.createRace(startBlock);
        uint256 raceId = raceRoninChain.nextRaceId() - 1;
        vm.stopPrank();

        // All players enter the race
        string[] memory predictions = generatePredictions();
        for(uint i = 0; i < 4; i++) {
            vm.startPrank(players[i]);
            raceRoninChain.enterRace{value: 1 ether}(raceId, predictions);
            vm.stopPrank();
        }

        // Advance to race end
        vm.roll(startBlock + 51);

        // Submit player 2 as the winner
        vm.startPrank(owner); // Start acting as the owner
        raceRoninChain.submitWinner(raceId, players[1], predictions);
        vm.stopPrank(); // Stop acting as the owner
    }
}