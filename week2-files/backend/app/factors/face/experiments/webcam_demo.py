"""Live webcam demo: similarity to an enrolled photo + eye aspect ratio (EAR) + blinks.

Run (in a venv with experiments/requirements.txt):

    python backend/app/factors/face/experiments/webcam_demo.py my_photo.jpg
    python backend/app/factors/face/experiments/webcam_demo.py            # press E to enroll from the camera

Keys:  E = enroll the current camera face   Q or Esc = quit

On screen: similarity to the enrolled face, EAR, number of blinks, face brightness.
Nothing is saved to disk.

MediaPipe 1.x removed the old "solutions.face_mesh" API, so we use the newer
Tasks API (FaceLandmarker). It needs a small model file (about 4 MB), which is
downloaded on the first run to datasets/models/ (git-ignored).
"""

from __future__ import annotations

import argparse
import sys
import time
import urllib.request
from pathlib import Path

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks.python import BaseOptions, vision

from compare import DEMO_THRESHOLD, cosine_similarity, embedding_of, largest_face, load_model
from liveness import count_blinks, ear_from_landmarks

REPO_ROOT = Path(__file__).resolve().parents[5]
LANDMARKER_PATH = REPO_ROOT / "datasets" / "models" / "face_landmarker.task"
LANDMARKER_URL = (
    "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task"
)
EMBED_EVERY_N_FRAMES = 5  # ArcFace is slow on CPU (~0.1-0.3 s); MediaPipe runs on every frame
DIM_BRIGHTNESS = 70  # mean V (HSV) of the face box below this = "dim" (first guess, see DESIGN.md)


def load_landmarker() -> vision.FaceLandmarker:
    """Create a MediaPipe FaceLandmarker in VIDEO mode (uses tracking between frames)."""
    if not LANDMARKER_PATH.exists():
        print(f"Downloading MediaPipe face landmarker model to {LANDMARKER_PATH} ...")
        LANDMARKER_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(LANDMARKER_URL, LANDMARKER_PATH)
    options = vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(LANDMARKER_PATH)),
        running_mode=vision.RunningMode.VIDEO,
        num_faces=1,
    )
    return vision.FaceLandmarker.create_from_options(options)


def face_brightness(frame: np.ndarray, bbox) -> float:
    """Mean brightness (V channel of HSV, 0-255) inside the face box."""
    x1, y1, x2, y2 = [int(max(0, v)) for v in bbox]
    crop = frame[y1:y2, x1:x2]
    if crop.size == 0:
        return 0.0
    return float(cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)[:, :, 2].mean())


def main() -> None:
    parser = argparse.ArgumentParser(description="Live face similarity + blink demo.")
    parser.add_argument("enrolled", type=Path, nargs="?", help="photo of the enrolled person (optional)")
    parser.add_argument("--camera", type=int, default=0, help="camera index (default 0)")
    args = parser.parse_args()

    app = load_model()
    landmarker = load_landmarker()
    template = embedding_of(app, args.enrolled) if args.enrolled else None

    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        sys.exit("Cannot open the camera")

    ears: list[float] = []
    similarity, brightness, frame_index = None, None, 0
    started = time.monotonic()

    while True:
        ok, frame = camera.read()
        if not ok:
            break
        frame_index += 1
        height, width = frame.shape[:2]

        # 1. Landmarks + EAR on every frame (MediaPipe wants RGB; OpenCV gives BGR).
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        timestamp_ms = int((time.monotonic() - started) * 1000)
        result = landmarker.detect_for_video(image, timestamp_ms)
        ear = None
        if result.face_landmarks:
            ear = ear_from_landmarks(result.face_landmarks[0], width, height)
            ears.append(ear)
            ears = ears[-300:]  # keep the last ~10 s

        # 2. Face embedding + similarity on every Nth frame (slow part).
        face = None
        if frame_index % EMBED_EVERY_N_FRAMES == 0:
            face = largest_face(app, frame)
            if face is not None:
                brightness = face_brightness(frame, face.bbox)
                if template is not None:
                    similarity = cosine_similarity(template, face.normed_embedding)

        # 3. Draw the numbers.
        lines = [
            "enrolled: " + ("yes" if template is not None else "no (press E)"),
            f"similarity: {similarity:.3f} (demo threshold {DEMO_THRESHOLD})" if similarity is not None else "similarity: -",
            f"EAR: {ear:.3f}" if ear is not None else "EAR: no face",
            f"blinks (last 10 s): {count_blinks(ears)}",
            (f"brightness: {brightness:.0f} -> {'dim' if brightness < DIM_BRIGHTNESS else 'normal'}"
             if brightness is not None else "brightness: -"),
        ]
        for i, text in enumerate(lines):
            cv2.putText(frame, text, (10, 25 + 25 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        cv2.imshow("TrustAuth face demo (E = enroll, Q = quit)", frame)

        key = cv2.waitKey(1) & 0xFF
        if key in (ord("q"), 27):
            break
        if key == ord("e"):
            face = largest_face(app, frame)
            if face is None:
                print("No face found, try again")
            else:
                template = face.normed_embedding
                print("Enrolled from the camera")

    camera.release()
    cv2.destroyAllWindows()
    landmarker.close()


if __name__ == "__main__":
    main()
