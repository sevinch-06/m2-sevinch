# M2 (Sevinch): week 2 and week 3, how to upload

You have two weeks of work to upload. Do them **in order, as two separate pull requests**:

| Part | Folder in this zip | Branch | What it is |
|---|---|---|---|
| **1. Week 2** | `week2-files/` | `m2-face-prototype` | Face comparison demo, webcam demo, face + phone approval designs |
| **2. Week 3** | `week3-files/` | `m2-mock-factors` | Mock (fake) face and phone-approval factors for the login flow |

**Read every file before you upload it.** Grading is per person and you must be able to explain each
line at the defense. Change anything you disagree with.

Use **Git Bash** or **PowerShell**, in your `trustauth` folder (the one with `CLAUDE.md`). First unzip this
file **somewhere outside** the repository, e.g. your Desktop.

---

## Part 1: week 2 (face prototype and designs)

### What is inside `week2-files/`

| File | Task (team-plan §4.2) |
|---|---|
| `backend/app/factors/face/experiments/requirements.txt`, `README.md` | 1. Install InsightFace + MediaPipe (with Windows notes) |
| `backend/app/factors/face/experiments/compare.py` | 2. Face comparison: prints how similar two face photos are |
| `backend/app/factors/face/experiments/webcam_demo.py`, `liveness.py` | 3. Live camera demo: similarity, eye openness (EAR), blinks, brightness |
| `backend/app/factors/face/DESIGN.md` | 4. Enrollment, verification, threshold, liveness, light check; §7 = answer to open question 7 |
| `backend/app/factors/phone_approval/DESIGN.md` | 5. Phone approval design |

Good to know: MediaPipe 1.x removed the old `face_mesh` API that most tutorials use; the code uses the
newer `FaceLandmarker` (explained in the README). Face recognition uses **pretrained** models only
(ArcFace, MediaPipe); nothing is trained (`docs/decisions.md` D1).

### Steps

1. Create the branch:
   ```sh
   git switch main
   git pull
   git switch -c m2-face-prototype
   ```
2. Copy **the contents of `week2-files/`** (the `backend` folder inside it) into the repository root, merging
   with the existing `backend` folder.
3. Set up and try it (first run downloads ~280 MB of model files, once):
   ```sh
   python -m venv .venv-face
   .venv-face\Scripts\activate                # Git Bash / macOS: source .venv-face/Scripts/activate or bin/activate
   pip install -r backend/app/factors/face/experiments/requirements.txt
   python backend/app/factors/face/experiments/liveness.py
   python backend/app/factors/face/experiments/compare.py datasets/<photo1>.jpg datasets/<photo2>.jpg datasets/<photo3>.jpg
   python backend/app/factors/face/experiments/webcam_demo.py
   deactivate
   ```
   Put test photos in `datasets/` (git-ignored). **Never commit face images.**
4. **Your own test (required):** run `compare.py` on at least **3 same-person pairs** (two *different*
   photos of the same person) and **3 different-person pairs**, e.g. team members (with permission). Add
   the numbers to the "Results so far" section of `backend/app/factors/face/experiments/README.md`.
   Expected: same person roughly 0.4–0.8, different people roughly 0–0.3.
5. Check, then commit and push:
   ```sh
   git status            # only files under backend/app/factors/face and phone_approval; no photos, no .venv-face
   git add backend/app/factors/face backend/app/factors/phone_approval
   git commit -m "Add face comparison prototype and face/phone approval designs"
   git push -u origin m2-face-prototype
   ```
6. On GitHub: open a Pull Request `m2-face-prototype` → `main`, paste the description below, then
   **Squash and merge**.

### Pull request description (copy)

```markdown
## M2 week 1–2: face prototype and designs

- [x] 1. InsightFace + MediaPipe install: requirements.txt + README with Windows notes
- [x] 2. compare.py prints cosine similarity (results in experiments/README.md)
- [x] 3. webcam_demo.py: live similarity, EAR, blink count, brightness
- [x] 4. face/DESIGN.md: enrollment, verification, threshold method, liveness, light check, payloads, privacy
- [x] 5. phone_approval/DESIGN.md: sequence diagram, token rules, payloads, WebSocket messages, attack notes
- [x] 6. Interface review: answer to open question 7 in face/DESIGN.md §7

No datasets, face images, embeddings or secrets in this PR.
```

---

## Part 2: week 3 (mock factors)

Start only **after Part 1 is merged**.

### What is inside `week3-files/`

| File | What it is |
|---|---|
| `backend/app/factors/face/mock.py` | `MockFace`: needs a camera; `start()` returns the frame settings from your DESIGN.md; result has `light` + `liveness_passed`; supports dim light, failed liveness (printed photo) and "no face" |
| `backend/app/factors/phone_approval/mock.py` | `MockPhoneApproval`: laptop only; fake QR URL, `expires_in: 60`; approve, deny and expiry |
| `backend/app/factors/face/__init__.py`, `phone_approval/__init__.py`, `backend/tests/factors/__init__.py` | Empty files that make the folders Python packages (the last one already exists on `main`; same empty content) |
| `backend/tests/factors/test_m2_mocks.py` | 8 tests |

**What a mock is:** a fake version of your factor that looks exactly like the real one from the outside
(same name, same `start()` data, same result details), but passes or fails on command. Alisher's login flow
uses it until your real face code is ready (weeks 4–7). Both classes build on `MockFactor` in
`backend/app/factors/base.py` (already on `main`).

**How the request controls the mock:**

| Payload | Face result | Phone result |
|---|---|---|
| `{"mock_accept": true}` | accepted, score 0.9 | approved, score 1.0 |
| `{"mock_accept": false}` | rejected, score 0.1 | denied → error `cancelled` |
| `{"mock_accept": true, "mock_light": "dim"}` | accepted, `light: dim` | — |
| `{"mock_accept": false, "mock_liveness": false}` | rejected, `liveness_passed: false` | — |
| `{"mock_no_face": true}` | error `unavailable`, `reason: no_face` | — |
| `{"mock_error": "timeout"}` | error `timeout` | error `timeout`, not scanned |

### Steps

1. Create the branch from the updated `main`:
   ```sh
   git switch main
   git pull
   git switch -c m2-mock-factors
   ```
2. Copy **the contents of `week3-files/`** into the repository root, merging with the existing folders.
3. Test (a separate environment for the backend, made once):
   ```sh
   python -m venv .venv
   .venv\Scripts\activate
   pip install -r backend/requirements.txt
   cd backend
   python -m pytest tests/factors/test_m2_mocks.py -q     # expected: 8 passed
   python -m pytest -q                                     # whole backend: all pass
   cd ..
   ```
4. Check, then commit and push:
   ```sh
   git status            # only the files listed above
   git add backend/app/factors/face backend/app/factors/phone_approval backend/tests/factors
   git commit -m "Add mock face and phone-approval factors"
   git push -u origin m2-mock-factors
   ```
5. On GitHub: open a Pull Request `m2-mock-factors` → `main`, paste the description below, then
   **Squash and merge**.

### Pull request description (copy)

```markdown
## M2 week 3: mock face and phone approval

- [x] MockFace: camera required; frame settings; light, liveness, no-face cases
- [x] MockPhoneApproval: laptop only; fake QR; approve / deny / expire
- [x] Both follow base.py (interface v0.2) and subclass MockFactor
- [x] Tests: 8 passed
```

---

## If something goes wrong

- **`pip install` fails on InsightFace** with "Microsoft Visual C++ 14.0 or greater is required": check
  that you are installing the pinned versions from `requirements.txt` (they need no compiler).
- **`AttributeError: module 'mediapipe' has no attribute 'solutions'`**: you are running an old tutorial's
  code; use the files from this zip.
- **`ModuleNotFoundError: No module named 'app.factors.base'`** in Part 2: run `git pull` on `main` first;
  `base.py` must be there.
- **`git push` is refused:** you are probably on `main`. Run `git branch` and make sure you are on your
  `m2-…` branch.
