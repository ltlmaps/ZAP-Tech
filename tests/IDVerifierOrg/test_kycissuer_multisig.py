#!/usr/bin/python3

import functools
import pytest

from brownie import accounts, rpc

id_ = "member1".encode()


@pytest.fixture(scope="module", autouse=True)
def setup(org, ikyc):
    org.addAuthorityAddresses(org.ownerID(), accounts[1:3], {"from": accounts[0]})
    org.addAuthority(accounts[3:6], [], 2000000000, 1, {"from": accounts[0]})


@pytest.fixture(scope="module")
def multisig(org):
    yield functools.partial(_multisig, org)


def test_addMember(multisig, ikyc):
    multisig(ikyc.addMember, "0x1234", 1, 1, 1, 9999999999, (accounts[7],))


def test_updateMember(multisig, ikyc):
    multisig(ikyc.updateMember, id_, 2, 4, 1234567890)


def test_setMemberRestriction(multisig, ikyc):
    multisig(ikyc.setMemberRestriction, id_, False)


def test_registerAddresses(multisig, ikyc):
    multisig(ikyc.registerAddresses, id_, (accounts[7],))


def test_restrictAddresses(multisig, ikyc):
    multisig(ikyc.restrictAddresses, id_, (accounts[1],))


def _multisig(org, fn, *args):
    auth_id = org.getID(accounts[3])
    args = list(args) + [{"from": accounts[3]}]
    # check for failed call, no permission
    with pytest.reverts("dev: not permitted"):
        fn(*args)
    # give permission and check for successful call
    org.setAuthoritySignatures(auth_id, [fn.signature], True, {"from": accounts[0]})
    assert "MultiSigCallApproved" in fn(*args).events
    rpc.revert()
    # give permission, threhold to 3, check for success and fails
    org.setAuthoritySignatures(auth_id, [fn.signature], True, {"from": accounts[0]})
    org.setAuthorityThreshold(auth_id, 3, {"from": accounts[0]})
    args[-1]["from"] = accounts[3]
    assert "MultiSigCallApproved" not in fn(*args).events
    with pytest.reverts("dev: repeat caller"):
        fn(*args)
    args[-1]["from"] = accounts[4]
    assert "MultiSigCallApproved" not in fn(*args).events
    with pytest.reverts("dev: repeat caller"):
        fn(*args)
    args[-1]["from"] = accounts[5]
    assert "MultiSigCallApproved" in fn(*args).events
