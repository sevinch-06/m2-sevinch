"""Tests for M2's mock factors: face and phone approval."""

import asyncio
import json

import pytest

from app.factors.base import Factor, LoginContext
from app.factors.face.mock import MockFace
from app.factors.phone_approval.mock import MockPhoneApproval


def ctx(**fields) -> LoginContext:
    return LoginContext(**({"login_id": "L1", "device_type": "laptop", "has_camera": True} | fields))


def run(coroutine):
    return asyncio.run(coroutine)


@pytest.mark.parametrize("cls", [MockFace, MockPhoneApproval])
def test_mocks_follow_the_factor_interface(cls):
    factor = cls()
    assert isinstance(factor, Factor)
    challenge = run(factor.start("u1", ctx()))
    assert json.loads(json.dumps(challenge)) == challenge  # JSON-serialisable


def test_face_needs_a_camera():
    face = MockFace()
    assert face.is_available(ctx(has_camera=True)) is True
    assert face.is_available(ctx(has_camera=False)) is False


def test_face_accept_reject_and_light():
    face = MockFace()
    ok = run(face.verify("u1", {"mock_accept": True}, ctx()))
    assert (ok.accepted, ok.score, ok.context) == (True, 0.9, {"light": "normal", "liveness_passed": True})

    dim = run(face.verify("u1", {"mock_accept": True, "mock_light": "dim"}, ctx()))
    assert dim.context["light"] == "dim"

    rejected = run(face.verify("u1", {"mock_accept": False}, ctx()))
    assert (rejected.accepted, rejected.score, rejected.error) == (False, 0.1, None)


def test_face_failed_liveness_and_no_face():
    face = MockFace()
    photo = run(face.verify("u1", {"mock_accept": False, "mock_liveness": False}, ctx()))
    assert photo.accepted is False and photo.context["liveness_passed"] is False

    no_face = run(face.verify("u1", {"mock_no_face": True}, ctx()))
    assert (no_face.accepted, no_face.error, no_face.context) == (False, "unavailable", {"reason": "no_face"})

    # A bad duration is reported as bad_payload, never raised.
    bad = run(face.verify("u1", {"mock_no_face": True, "mock_duration_ms": -1}, ctx()))
    assert bad.error == "bad_payload"


def test_face_settings_do_not_leak_between_calls():
    face = MockFace()
    run(face.verify("u1", {"mock_accept": True, "mock_light": "dim", "mock_liveness": False}, ctx()))
    again = run(face.verify("u1", {"mock_accept": True}, ctx()))
    assert again.context == {"light": "normal", "liveness_passed": True}


def test_phone_approval_laptop_only_and_qr():
    phone = MockPhoneApproval()
    assert phone.is_available(ctx(device_type="laptop")) is True
    assert phone.is_available(ctx(device_type="phone")) is False
    challenge = run(phone.start("u1", ctx()))
    assert challenge["expires_in"] == 60 and challenge["qr_url"].endswith("mock-L1")


def test_phone_approval_outcomes():
    phone = MockPhoneApproval()
    approved = run(phone.verify("u1", {"mock_accept": True}, ctx()))
    assert (approved.accepted, approved.score, approved.context) == (True, 1.0, {"scanned": True, "decision": "approved"})

    denied = run(phone.verify("u1", {"mock_accept": False}, ctx()))
    assert (denied.accepted, denied.error, denied.context["decision"]) == (False, "cancelled", "denied")

    expired = run(phone.verify("u1", {"mock_error": "timeout"}, ctx()))
    assert (expired.error, expired.context) == ("timeout", {"scanned": False, "decision": None})
