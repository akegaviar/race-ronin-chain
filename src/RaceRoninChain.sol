// SPDX-License-Identifier: MIT
pragma solidity 0.8.19;

contract RaceRoninChain {
    address public owner;
    struct Player {
        string[] predictions;
        uint256 progress;
    }

    struct Race {
        uint256 id;
        uint256 startBlock;
        uint256 endBlock;
        address[] players;
        uint256 totalEntryFees;
        mapping(address => Player) playerInfo;
        bool winnerSubmitted;
        address winner;
        string[] winnerPredictions;
    }

    uint256 public constant ENTRY_FEE = 1 ether; // Entry fee is 1 RON
    uint256 public constant FEE_PERCENTAGE = 1; // 1% fee
    address payable public treasuryAddress; // Address to receive the fee
    uint256 public nextRaceId = 1;
    mapping(uint256 => Race) private races;
    mapping(uint256 => bool) private startBlockUsed;

    event RaceCreated(uint256 indexed raceId, uint256 startBlock, uint256 endBlock);
    event PlayerEntered(uint256 indexed raceId, address indexed player, uint256 numberOfPredictions);
    event WinnerDeclared(uint256 indexed raceId, address winner, uint256 prize);
    event FeeDeducted(uint256 indexed raceId, uint256 fee);

    constructor(address payable _treasuryAddress) {
        treasuryAddress = _treasuryAddress;
        owner = msg.sender; // Set the contract deployer as the owner
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Caller is not the owner");
        _;
    }

    function createRace(uint256 _startBlock) external {
        require(_startBlock > block.number, "Start block must be in the future.");
        require(!startBlockUsed[_startBlock], "Start block already used."); // Check if the start block is already used

        Race storage race = races[nextRaceId];
        race.id = nextRaceId;
        race.startBlock = _startBlock;
        race.endBlock = _startBlock + 50; // Race length in blocks
        startBlockUsed[_startBlock] = true; // Mark the start block as used

        emit RaceCreated(nextRaceId, _startBlock, race.endBlock);
        nextRaceId++;
    }

    function enterRace(uint256 _raceId, string[] calldata _predictions) external payable {
        require(msg.value == ENTRY_FEE, "Entry fee is not correct.");
        Race storage race = races[_raceId];
        require(block.number < race.startBlock, "Race already started or registration closed.");
        require(_predictions.length <= 50, "Cannot submit more than 50 predictions."); // Limit predictions to 50

        // Check each prediction is exactly 3 characters long
        for (uint256 i = 0; i < _predictions.length; i++) {
            require(bytes(_predictions[i]).length == 3, "Each prediction must be exactly 3 characters.");
        }

        race.totalEntryFees += msg.value; // Update total entry fees for the race

        Player storage player = race.playerInfo[msg.sender];
        for (uint256 i = 0; i < _predictions.length; i++) {
            player.predictions.push(_predictions[i]);
        }
        race.players.push(msg.sender);

        emit PlayerEntered(_raceId, msg.sender, _predictions.length);
    }

    function submitWinner(uint256 raceId, address winner, string[] calldata winnerPredictions) external onlyOwner {
        Race storage race = races[raceId];
        require(block.number > race.endBlock, "Race not finished yet.");
        require(!race.winnerSubmitted, "Winner already submitted.");

        Player storage player = race.playerInfo[winner];
        require(player.predictions.length == winnerPredictions.length, "Prediction count mismatch.");

        for (uint256 i = 0; i < winnerPredictions.length; i++) {
            require(keccak256(abi.encodePacked(player.predictions[i])) == keccak256(abi.encodePacked(winnerPredictions[i])), "Prediction mismatch.");
        }

        race.winnerSubmitted = true;
        race.winner = winner;
        
        delete race.winnerPredictions;
        for (uint256 i = 0; i < winnerPredictions.length; i++) {
            race.winnerPredictions.push(winnerPredictions[i]);
        }

        // Calculate prize and fee
        uint256 fee = race.totalEntryFees * FEE_PERCENTAGE / 100;
        uint256 prize = race.totalEntryFees - fee;

        // Transfer prize to winner
        payable(winner).transfer(prize);

        // Transfer fee to treasury address
        treasuryAddress.transfer(fee);

        emit WinnerDeclared(raceId, winner, prize);
    }

    function transferOwnership(address newOwner) public onlyOwner {
        require(newOwner != address(0), "New owner is the zero address");
        owner = newOwner;
    }

    function getPlayerPredictions(uint256 raceId, address playerAddress) external view returns (string[] memory) {
        require(raceId < nextRaceId, "Race does not exist.");
        Race storage race = races[raceId];
        Player storage player = race.playerInfo[playerAddress];
        return player.predictions;
    }

    function getRaceDetails(uint256 _raceId) external view returns (
        uint256 id, 
        uint256 startBlock, 
        uint256 endBlock, 
        bool raceStarted, 
        uint256 totalEntryFees, 
        uint256 playerCount, 
        address[] memory playerAddresses, 
        bool winnerSubmitted, 
        address winner, 
        string[] memory winnerPredictions
    ) {
        Race storage race = races[_raceId];
        bool _raceStarted = block.number >= race.startBlock && block.number <= race.endBlock;
        return (
            race.id,
            race.startBlock,
            race.endBlock,
            _raceStarted,
            race.totalEntryFees,
            race.players.length,
            race.players,
            race.winnerSubmitted,
            race.winner,
            race.winnerPredictions
        );
    }
}
