# M2 (Sevinch): week 3, mock face and phone approval, how to upload

Your week 3 task: **mock face and mock phone-approval factors**. A mock looks exactly like your real factor
from the outside (same name, same `start()` data, same result details), but passes or fails on command, so
Alisher can build the login flow before the real face code exists. **Read every file before you upload it.**

## Before you start: two things must be on `main`

1. **Your week 1–2 work** (the `m2-face-prototype` zip from last week). Upload and merge it first if you
   have not yet.
2. **Alisher's PR `m4-week3-foundation`** (adds `backend/app/factors/base.py`). Your mocks import from it.
   Check with `git pull` and then `dir backend\app\factors\base.py` (Windows) or `ls backend/app/factors/base.py`.

## What is inside

| File | What it is |
|---|---|
| `backend/app/factors/face/mock.py` | `MockFace`: needs a camera (`has_camera`); `start()` returns the frame settings from your DESIGN.md; result context `light` + `liveness_passed`; supports dim light, failed liveness (printed photo) and "no face" (`unavailable` + `reason: no_face`) |
| `backend/app/factors/phone_approval/mock.py` | `MockPhoneApproval`: laptop only; `start()` returns a fake QR URL + `expires_in: 60`; approve, deny (`cancelled` + `decision: denied`) and expiry (`timeout`) |
| `backend/app/factors/face/__init__.py`, `phone_approval/__init__.py`, `backend/tests/factors/__init__.py` | Empty files that make the folders Python packages |
| `backend/tests/factors/test_m2_mocks.py` | 8 tests |

**How the request controls the mock** (also written at the top of each file):

| Payload | Face result | Phone result |
|---|---|---|
| `{"mock_accept": true}` | accepted, score 0.9 | approved, score 1.0 |
| `{"mock_accept": false}` | rejected, score 0.1 | denied → `cancelled` |
| `{"mock_accept": true, "mock_light": "dim"}` | accepted, `light: dim` | — |
| `{"mock_accept": false, "mock_liveness": false}` | rejected, `liveness_passed: false` | — |
| `{"mock_no_face": true}` | `unavailable`, `reason: no_face` | — |
| `{"mock_error": "timeout"}` | `timeout` | `timeout`, not scanned |

Both classes subclass `MockFactor` from `base.py`, which handles the shared parts (`mock_accept`,
`mock_error`, `mock_duration_ms`, not enrolled, bad payload).

## Steps

```sh
git switch main
git pull
git switch -c m2-mock-factors
```

1. Unzip **into the repository root**. Do not copy `UPLOAD.md`.
2. Test (needs the backend libraries once: `pip install -r backend/requirements.txt` in your `.venv`):
   ```sh
   cd backend
   python -m pytest tests/factors/test_m2_mocks.py -q     # expected: 8 passed
   python -m pytest -q                                     # whole backend: all pass
   cd ..
   ```
3. `git status`: only the files above.
4. Commit and push:
   ```sh
   git add backend/app/factors/face backend/app/factors/phone_approval backend/tests/factors
   git commit -m "Add mock face and phone-approval factors"
   git push -u origin m2-mock-factors
   ```
5. Open the PR, paste the description below, **Squash and merge**.

## Pull request description (copy)

```markdown
## M2 week 3: mock face and phone approval

- [x] MockFace: camera required; frame settings; light, liveness, no-face cases
- [x] MockPhoneApproval: laptop only; fake QR; approve / deny / expire
- [x] Both follow base.py (interface v0.2) and subclass MockFactor
- [x] Tests: 8 passed
```
