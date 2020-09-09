pragma solidity ^0.7.1;
// SPDX-License-Identifier: UNLICENSED
import "./BasicBridge.sol";

abstract contract IERC20 {
    function transferFrom(address _from, address _to, uint256 _amount) public virtual returns (bool);
    function transfer(address to, uint256 value) public virtual returns (bool);
}

contract LeftSide is BasicBridge {

    event TokenLocked(address indexed sender, uint256 amount);

    constructor (address _oracle, address _token) BasicBridge(_oracle) {
        tokenAddress = _token;
    }

    function actionOnRelay(uint256 _amount) internal override {
        IERC20(tokenAddress).transferFrom(msg.sender, address(this), _amount);

        emit TokenLocked(msg.sender, _amount);
    }

    function actionOnConfirmation(address _recipient, uint256 _amount) internal override {
        IERC20(tokenAddress).transfer(_recipient, _amount);
    }

}
