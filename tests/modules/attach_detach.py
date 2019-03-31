#!/usr/bin/python3

from brownie import *
from scripts.deployment import main 

module_source = """
pragma solidity 0.4.25;

contract TestModule {

    address owner;

    constructor(address _owner) public { owner = _owner; }
    function getOwner() external view returns (address) { return owner; }

    function getPermissions()
        external
        pure
        returns
    (
        bytes4[] permissions,
        bytes4[] hooks,
        uint256 hookBools
    )
    {
        return (permissions, hooks, 0);
    }
    
}"""


def setup():
    main(SecurityToken)
    global token, issuer, TestModule, module_token, module_issuer
    token = SecurityToken[0]
    issuer = IssuingEntity[0]
    TestModule = compile_source(module_source)[0]
    module_token = TestModule.deploy(a[0], token)
    module_issuer = TestModule.deploy(a[0], issuer)

def attach_token():
    '''attach a token module'''
    check.false(token.isActiveModule(module_token))
    check.false(issuer.isActiveModule(module_token))
    issuer.attachModule(token, module_token, {'from': a[0]})
    check.true(token.isActiveModule(module_token))
    check.false(issuer.isActiveModule(module_token))

def detach_token():
    '''detach a token module'''
    issuer.attachModule(token, module_token, {'from': a[0]})
    issuer.detachModule(token, module_token, {'from': a[0]})
    check.false(token.isActiveModule(module_token))
    check.false(issuer.isActiveModule(module_token))

def attach_via_token():
    '''cannot attach directly via token'''
    check.reverts(token.attachModule, (module_token, {'from': a[0]}), "dev: only issuer")

def detach_via_token():
    '''cannot detach directly via token'''
    issuer.attachModule(token, module_token, {'from': a[0]})
    check.reverts(token.detachModule, (module_token, {'from': a[0]}), "dev: only issuer")

def attach_issuer():
    '''attach an issuer module'''
    check.false(token.isActiveModule(module_issuer))
    check.false(issuer.isActiveModule(module_issuer))
    issuer.attachModule(issuer, module_issuer, {'from': a[0]})
    check.true(token.isActiveModule(module_issuer))
    check.true(issuer.isActiveModule(module_issuer))

def detach_issuer():
    '''detach an issuer module'''
    issuer.attachModule(issuer, module_issuer, {'from': a[0]})
    issuer.detachModule(issuer, module_issuer, {'from': a[0]})
    check.false(token.isActiveModule(module_issuer))
    check.false(issuer.isActiveModule(module_issuer))

def wrong_owner():
    '''attach with wrong owner'''
    check.reverts(
        issuer.attachModule,
        (issuer, module_token, {'from': a[0]}),
        "dev: wrong owner"
    )
    check.reverts(
        issuer.attachModule,
        (token, module_issuer, {'from': a[0]}),
        "dev: wrong owner"
    )

def already_active():
    '''attach already active module'''
    issuer.attachModule(issuer, module_issuer, {'from': a[0]})
    check.reverts(
        issuer.attachModule,
        (issuer, module_issuer, {'from': a[0]}),
        "dev: already active"
    )
    issuer.attachModule(token, module_token, {'from': a[0]})
    check.reverts(
        issuer.attachModule,
        (token, module_token, {'from': a[0]}),
        "dev: already active"
    )
