pragma solidity ^0.7.1;
// SPDX-License-Identifier: UNLICENSED
import "./BasicBridge.sol";
import "./Owned.sol";

abstract contract IERC20Minted {
    function transferFrom(address _from, address _to, uint256 _amount) public virtual returns (bool);
    function mint(address _recipient, uint256 _amount) external virtual;
    function burn(uint256 _amount) external virtual;
}

contract RightSide is BasicBridge, Owned {

    event TokenBurnt(address indexed sender, uint256 amount);

    constructor (address _oracle) BasicBridge(_oracle) Owned() {
    }

    function setTokenAddress(address _token) onlyOwner() external {
        require(_token != address(0), "Zero address");
        tokenAddress = _token;
    }

    function actionOnRelay(uint256 _amount) internal override{
        IERC20Minted(tokenAddress).transferFrom(msg.sender, address(this), _amount);
        IERC20Minted(tokenAddress).burn(_amount);

        emit TokenBurnt(msg.sender, _amount);
    }

    function actionOnConfirmation(address _recipient, uint256 _amount) internal override{
        IERC20Minted(tokenAddress).mint(_recipient, _amount);
    }

}
