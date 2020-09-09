pragma solidity ^0.7.1;
// SPDX-License-Identifier: UNLICENSED
import "./erc20token.sol";

contract MintToken is ERC20 {
  address public bridge;
  address public owner;

  constructor (string memory name, string memory symbol, uint8 decimals, address minter) ERC20(name, symbol, decimals, 0) {
      bridge = minter;
      owner = msg.sender;
  }

  function mint(address _recipient, uint256 _amount) external {
      require(msg.sender == bridge, "Unauthorized");
      _mint(_recipient, _amount);
  }

  function giveMePleaseSomeTokens() external pure override {
      revert();
  }

  function changeMinter(address _minter) external {
      require(owner == msg.sender, "Unauthorized");
      bridge = _minter;
  }

  function burn(uint256 amount) external {
      _burn(msg.sender, amount);
  }

}
