// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SecureVoting {
    struct Election {
        uint256 electionId;
        string[] candidates;
        mapping(uint256 => uint256) votes;
        mapping(address => bool) hasVoted;
        bool isActive;
        bool exists;
    }
    
    mapping(uint256 => Election) public elections;
    address public admin;
    
    event ElectionCreated(uint256 electionId, uint256 candidateCount);
    event ElectionActivated(uint256 electionId);
    event ElectionClosed(uint256 electionId);
    event VoteCast(uint256 electionId, address voter, uint256 candidateIndex);
    
    constructor() {
        admin = msg.sender;
    }
    
    modifier onlyAdmin() {
        require(msg.sender == admin, "Only admin");
        _;
    }
    
    function createElection(uint256 _electionId, string[] memory _candidates) public onlyAdmin {
        require(!elections[_electionId].exists, "Election exists");
        require(_candidates.length >= 2, "Need at least 2 candidates");
        
        Election storage e = elections[_electionId];
        e.electionId = _electionId;
        e.candidates = _candidates;
        e.isActive = false;
        e.exists = true;
        
        emit ElectionCreated(_electionId, _candidates.length);
    }
    
    function activateElection(uint256 _electionId) public onlyAdmin {
        require(elections[_electionId].exists, "Election not found");
        require(!elections[_electionId].isActive, "Already active");
        elections[_electionId].isActive = true;
        emit ElectionActivated(_electionId);
    }
    
    function closeElection(uint256 _electionId) public onlyAdmin {
        require(elections[_electionId].exists, "Election not found");
        require(elections[_electionId].isActive, "Not active");
        elections[_electionId].isActive = false;
        emit ElectionClosed(_electionId);
    }
    
    function castVote(uint256 _electionId, uint256 _candidateIndex) public {
        Election storage e = elections[_electionId];
        require(e.exists, "Election not found");
        require(e.isActive, "Election not active");
        require(!e.hasVoted[msg.sender], "Already voted");
        require(_candidateIndex < e.candidates.length, "Invalid candidate");
        
        e.votes[_candidateIndex]++;
        e.hasVoted[msg.sender] = true;
        
        emit VoteCast(_electionId, msg.sender, _candidateIndex);
    }
    
    function getResults(uint256 _electionId) public view returns (string[] memory, uint256[] memory, bool) {
        Election storage e = elections[_electionId];
        require(e.exists, "Election not found");
        
        uint256[] memory voteCounts = new uint256[](e.candidates.length);
        for (uint256 i = 0; i < e.candidates.length; i++) {
            voteCounts[i] = e.votes[i];
        }
        
        return (e.candidates, voteCounts, e.isActive);
    }
    
    function hasVotedInElection(uint256 _electionId, address _voter) public view returns (bool) {
        return elections[_electionId].hasVoted[_voter];
    }
}
