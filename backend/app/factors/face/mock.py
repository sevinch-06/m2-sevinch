"""Mock face factor (week 3). Stands in for the real ArcFace + blink factor until weeks 4-7.

Same name, availability rule, start() shape and context keys as the real factor
(face/DESIGN.md §5). The outcome is chosen by the request:
    {"mock_accept": true}                         -> face matches, blink seen
    {"mock_accept": false}                        -> face does not match
    {"mock_accept": true, "mock_light": "dim"}    -> as above, in dim light
    {"mock_accept": false, "mock_liveness": false} -> face matches but no blink (e.g. printed photo)
    {"mock_no_face": true}                        -> no usable face in any frame
See MockFactor in app/factors/base.py for mock_error and mock_duration_ms.
"""

from app.factors.base import FactorResult, LoginContext, MockFactor


class MockFace(MockFactor):
    name = "face"
    binary = False  # biometric: score 0.9 accepted / 0.1 rejected
    mock_context = {"light": "normal", "liveness_passed": True}

    def is_available(self, ctx: LoginContext) -> bool:
        # The real factor needs a camera (interface §3 has_camera).
        return self.available and ctx.has_camera

    async def start(self, user_id: str, ctx: LoginContext) -> dict:
        # Same shape as the real start() (interface §6.1).
        return {"frames_needed": 15, "fps": 5, "blink_required": True, "timeout_s": 10, "mock": True}

    async def verify(self, user_id: str, payload: dict, ctx: LoginContext) -> FactorResult:
        # The shared checks run first (bad payload, not enrolled, mock_error), so verify() never raises.
        result = await super().verify(user_id, payload, ctx)
        if result.error is None and payload.get("mock_no_face") is True:
            # "No face found" = unavailable with context.reason (interface §5, change 9).
            return FactorResult(factor=self.name, accepted=False, score=0.0, duration_ms=result.duration_ms,
                                context={"reason": "no_face"}, error="unavailable")
        if result.error is None:
            light = payload.get("mock_light", "normal")
            result.context["light"] = light if light in ("normal", "dim") else "normal"
            if payload.get("mock_liveness") is False:
                result.context["liveness_passed"] = False
        return result
