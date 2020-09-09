pragma solidity ^0.7.1;
// SPDX-License-Identifier: UNLICENSED
abstract contract BasicBridge {
    address public tokenAddress;
    address public oracle;

    mapping (bytes32 => bool) public usedMessages;

    constructor (address _oracle) {
        oracle = _oracle;
    }

    function relay(uint256 _amount) external {
        require(tokenAddress != address(0), "Not initialized");
        actionOnRelay(_amount);
    }

    function relayConfirmed(address _recipient, uint256 _amount, bytes32 _msgId) external {
        require(msg.sender == oracle, "Unauthorized");
        require(! usedMessages[_msgId], "Already used");
        require(tokenAddress != address(0), "Not initialized");

        usedMessages[_msgId] = true;
        actionOnConfirmation(_recipient, _amount);
    }

    function actionOnRelay(uint256 _amount) internal virtual;
    function actionOnConfirmation(address _recipient, uint256 _amount) internal virtual;
}
