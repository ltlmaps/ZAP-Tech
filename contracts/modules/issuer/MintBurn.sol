pragma solidity ^0.4.24;

import "../../open-zeppelin/SafeMath.sol";
import "../ModuleBase.sol";
import "../../SecurityToken.sol";


contract MintBurn is IssuerModuleBase {

	using SafeMath for uint256;

	constructor(address _issuer) IssuerModuleBase(_issuer) public { }

	function getBindings() external pure returns (bool, bool, bool) {
		return (false, false, false);
	}

	function mint(address _token, uint256 _value) external onlyIssuer returns (bool) {
		SecurityToken t = SecurityToken(_token);
		uint256 _new = t.balanceOf(address(issuer)).add(_value);
		require(t.modifyBalance(address(issuer), _new));
		return true;
	}

	function burn(address _token, uint256 _value) external onlyIssuer returns (bool) {
		SecurityToken t = SecurityToken(_token);
		uint256 _new = t.balanceOf(address(issuer)).sub(_value);
		require(t.modifyBalance(address(issuer), _new));
		return true;
	}
}
