pragma solidity ^0.7.1;

// SPDX-License-Identifier: UNLICENSED

contract Owned {
    address public owner;

    constructor () {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Unauthorized");
        _;
    }

}
