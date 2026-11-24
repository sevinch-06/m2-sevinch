"""Mock phone-approval factor (week 3). Stands in for the real QR + phone factor until weeks 8-11.

Same name, availability rule, start() shape and context keys as the real factor
(phone_approval/DESIGN.md §7). The outcome is chosen by the request:
    {"mock_accept": true}         -> phone approved
    {"mock_accept": false}        -> phone denied   (error "cancelled", decision "denied")
    {"mock_error": "timeout"}     -> nobody scanned / decided in time
The real verify() payload is empty and the decision comes from Redis; the mock
reads it from the payload instead, so the login flow can be tested without a phone.
"""

from app.factors.base import FactorResult, LoginContext, MockFactor


class MockPhoneApproval(MockFactor):
    name = "phone_approval"
    binary = True
    mock_context = {"scanned": True, "decision": "approved"}

    def is_available(self, ctx: LoginContext) -> bool:
        # v1: the QR must be scanned from another screen, so not when logging in on a phone.
        return self.available and ctx.device_type == "laptop"

    async def start(self, user_id: str, ctx: LoginContext) -> dict:
        # Same shape as the real start() (interface §6.2). The URL is fake.
        return {"qr_url": f"https://localhost/phone/approve/mock-{ctx.login_id}", "expires_in": 60, "mock": True}

    async def verify(self, user_id: str, payload: dict, ctx: LoginContext) -> FactorResult:
        result = await super().verify(user_id, payload, ctx)
        # A deny is the user's choice: error "cancelled" + decision "denied" (interface §11).
        if result.error is None and not result.accepted:
            return FactorResult(factor=self.name, accepted=False, score=0.0, duration_ms=result.duration_ms,
                                context={"scanned": True, "decision": "denied"}, error="cancelled")
        if result.error == "timeout":
            result.context = {"scanned": False, "decision": None}
        return result
