# Face experiments (M2)

Prototype scripts for the face factor. They use heavy libraries (InsightFace, ONNX Runtime, MediaPipe)
that are not in the backend Docker image, so run them in a local virtual environment.

| File | What it does |
|---|---|
| `compare.py` | Prints the cosine similarity between the face in one photo and the faces in other photos |
| `webcam_demo.py` | Live camera: similarity to an enrolled face, eye aspect ratio (EAR), blink count, face brightness |
| `liveness.py` | Pure functions: EAR and blink counting (used by the webcam demo; reused in week 7) |

## 1. Setup

From the repository root:

```sh
python -m venv .venv-face
.venv-face\Scripts\activate          # Windows PowerShell;  source .venv-face/bin/activate on macOS/Linux
pip install -r backend/app/factors/face/experiments/requirements.txt
```

**Downloads on first run (not in git):**
- InsightFace model pack `buffalo_l` (~280 MB) → `C:\Users\<you>\.insightface\models\buffalo_l\`
- MediaPipe face landmarker model (~4 MB) → `datasets/models/face_landmarker.task` (webcam demo only)

### Windows notes

- With the versions in `requirements.txt`, pip installs **prebuilt wheels**, so no compiler is needed.
- Older InsightFace versions (0.7.x) have no Windows wheel and need **Microsoft C++ Build Tools**
  ("Desktop development with C++" workload). If pip prints `error: Microsoft Visual C++ 14.0 or greater
  is required`, either install the build tools or make sure you are using the pinned versions.
- **MediaPipe 1.x removed `mediapipe.solutions` (the old `face_mesh` API).** Tutorials that use
  `mp.solutions.face_mesh.FaceMesh` will fail with `AttributeError`. We use the Tasks API
  (`mediapipe.tasks.python.vision.FaceLandmarker`), which gives the same 468 landmark indices (+10 iris
  points).
- Webcam privacy: Windows may ask to allow camera access for Python (Settings → Privacy → Camera →
  "Let desktop apps access your camera").

## 2. compare.py

```sh
python backend/app/factors/face/experiments/compare.py person1_a.jpg person1_b.jpg person2.jpg
```

Expected output (the first image is compared with each of the others):

```
person1_a.jpg vs person1_b.jpg: similarity = 0.6xx  -> same person?
person1_a.jpg vs person2.jpg:   similarity = 0.0xx  -> different person?
```

Same person usually scores **0.4–0.8**, different people **0–0.3**. The threshold `0.35` in the script
is only a starting value; the real one is chosen on LFW in week 6 (see [`../DESIGN.md`](../DESIGN.md) §3).

Use photos of yourselves (team members, with consent) or LFW images. Put them in `datasets/` (git-ignored),
**never commit face images**.

### Results so far

LFW's website could not be reached when this was first tested (2026-11-20), so the first check used
the group photo bundled with InsightFace (`insightface.data.get_image("t1")`): six faces of different
people, plus altered copies of one face (mirror, darker, rotated, low-quality JPEG) as "same person".

| Comparison (reference = face 0) | Similarity | Demo verdict (0.35) |
|---|---|---|
| mirrored copy | 0.945 | same |
| darkened to 35% brightness | 0.958 | same |
| rotated 12° | 0.975 | same |
| JPEG quality 15 | 0.915 | same |
| 5 different people (faces 1–5) | −0.019 … 0.081 | different |

The code works and separates people clearly. **Caution:** altered copies of *one* photo score much higher
(> 0.9) than two *different* photos of the same person will (typically 0.4–0.8), so this does not test
the threshold yet. CPU run time: ~9 s for 10 images including model loading.

MediaPipe check on the same face: 1 face, 478 landmarks, EAR = 0.113. The person in that photo is looking
down with the eyelids almost closed, so a low value is correct. It also shows a design risk: **looking
down lowers the EAR**, so the blink detector needs the open → closed → open sequence, not just one low value.

**To do (task 2 "done when"):** run it on at least 3 real same-person pairs (two *different* photos of
the same person) and 3 different-person pairs, e.g. team members' photos or LFW, and add the numbers here.

## 3. webcam_demo.py

```sh
python backend/app/factors/face/experiments/webcam_demo.py my_photo.jpg   # compare with a photo
python backend/app/factors/face/experiments/webcam_demo.py                # press E to enroll from the camera
```

Keys: **E** enroll the current face, **Q** / **Esc** quit. The window shows:
- **similarity** to the enrolled face (updated every 5th frame, because ArcFace is slow on CPU);
- **EAR**: about 0.25–0.35 with open eyes, below 0.2 when closed. Blink and watch it drop;
- **blinks** in the last ~10 s (open → closed → open, see `liveness.py`);
- **brightness** of the face box and whether it counts as `dim` (< 70, first guess).

Things to try and note for the DESIGN.md: similarity in normal vs dim light, with glasses, at different
distances; whether every blink is counted; what a printed photo does (EAR should not change).

## 4. liveness.py

```sh
python backend/app/factors/face/experiments/liveness.py    # prints "liveness.py self-check passed"
```
