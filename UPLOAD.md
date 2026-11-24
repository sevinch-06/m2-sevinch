# M2 (Sevinch): week 1–2 face and phone approval files, how to upload

This zip contains your week 1–2 deliverables from `docs/team-plan.md` §4.2. **Read every file before you
upload it.** You must be able to explain each line at the defense. Change anything you disagree with.

## What is inside

| File | Task (team-plan §4.2) |
|---|---|
| `backend/app/factors/face/experiments/requirements.txt`, `README.md` | 1. Install InsightFace + MediaPipe (with Windows notes) |
| `backend/app/factors/face/experiments/compare.py` | 2. Face-comparison demo |
| `backend/app/factors/face/experiments/webcam_demo.py`, `liveness.py` | 3. *Nice to have:* webcam demo with similarity, EAR, blinks, brightness |
| `backend/app/factors/face/DESIGN.md` | 4. Enrollment / verification / threshold design; §7 = answer to open question **7** (task 6) |
| `backend/app/factors/phone_approval/DESIGN.md` | 5. Phone approval design |

**Still to do by you (task 2 "done when"):** run `compare.py` on at least 3 *real* same-person pairs (two
different photos of the same person) and 3 different-person pairs, e.g. photos of team members (with
consent) or LFW, and add the numbers to the "Results so far" section of `experiments/README.md`. The
first test only used one group photo (see README) because the LFW website was down.

Also try `webcam_demo.py` yourself (needs a camera) and note what you see in DESIGN.md.

## Steps (Git Bash or PowerShell, in your `trustauth` folder)

```sh
git switch main
git pull
git switch -c m2-face-prototype
```

1. Unzip this file **into the repository root** (the folder with `CLAUDE.md`), so the files land in
   `backend/app/factors/face/` and `backend/app/factors/phone_approval/`. Do not copy `UPLOAD.md` into the repo.
2. Set up and test (first run downloads ~280 MB of model files):
   ```sh
   python -m venv .venv-face
   .venv-face\Scripts\activate             # macOS/Linux: source .venv-face/bin/activate
   pip install -r backend/app/factors/face/experiments/requirements.txt
   python backend/app/factors/face/experiments/liveness.py
   python backend/app/factors/face/experiments/compare.py datasets/<photo1>.jpg datasets/<photo2>.jpg datasets/<photo3>.jpg
   python backend/app/factors/face/experiments/webcam_demo.py
   ```
   Keep test photos in `datasets/`. That folder is git-ignored. **Never commit face images.**
3. Check that **only** your files changed (no photos, no `.venv-face`, no `datasets/`):
   ```sh
   git status
   ```
4. Commit and push:
   ```sh
   git add backend/app/factors/face backend/app/factors/phone_approval
   git commit -m "Add face comparison prototype and face/phone approval designs"
   git push -u origin m2-face-prototype
   ```
5. On GitHub, open a Pull Request from `m2-face-prototype` to `main`, paste the description below, and
   squash-merge it.

## Pull request description (copy)

```markdown
## M2 week 1–2: face prototype and designs

- [x] 1. InsightFace + MediaPipe install: requirements.txt + README with Windows notes
- [x] 2. compare.py prints cosine similarity (results table in experiments/README.md)
- [x] 3. webcam_demo.py: live similarity, EAR, blink count, brightness
- [x] 4. face/DESIGN.md: enrollment, verification, threshold method, liveness, light check, payloads, privacy
- [x] 5. phone_approval/DESIGN.md: sequence diagram, token rules, payloads, WebSocket messages, attack notes
- [x] 6. Interface review: answer to open question 7 in face/DESIGN.md §7; face context keys confirmed

No datasets, face images, embeddings or secrets in this PR.

Proposals for interface v0.2: face/DESIGN.md §8 (`no_face` error code, `light_hint`), phone_approval/DESIGN.md §9.
```
