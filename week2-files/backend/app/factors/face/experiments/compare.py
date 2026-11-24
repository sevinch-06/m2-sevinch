"""Face comparison demo: how similar are the faces in two photos?

Uses InsightFace's "buffalo_l" model pack (RetinaFace detector + ArcFace
recognition model, Deng et al. 2019). Nothing is trained by us.

Run (in a venv with experiments/requirements.txt):

    python backend/app/factors/face/experiments/compare.py a.jpg b.jpg
    python backend/app/factors/face/experiments/compare.py a.jpg b.jpg c.jpg   # a vs b, a vs c

The first run downloads the model pack (about 280 MB) to ~/.insightface/models/.

Output: cosine similarity of the two face embeddings, -1..1. Same person is
typically 0.4-0.8, different people 0-0.3. The threshold here (0.35) is only a
starting value; the real one is chosen on LFW in week 6 (see ../DESIGN.md).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import cv2
import numpy as np
from insightface.app import FaceAnalysis

DEMO_THRESHOLD = 0.35  # starting value only, tuned on LFW in week 6


def load_model() -> FaceAnalysis:
    """Load detector + ArcFace on the CPU.

    ctx_id=-1 means CPU (no GPU needed). det_size is the size the image is
    scaled to for face detection; 640x640 is the model's standard size.
    allowed_modules skips the age/gender/landmark models we do not need.
    """
    app = FaceAnalysis(name="buffalo_l", allowed_modules=["detection", "recognition"])
    app.prepare(ctx_id=-1, det_size=(640, 640))
    return app


def largest_face(app: FaceAnalysis, image: np.ndarray):
    """Detect faces and return the biggest one (by box area), or None if there is no face."""
    faces = app.get(image)
    if not faces:
        return None
    # bbox = [x1, y1, x2, y2]; the biggest face is usually the person in front of the camera.
    return max(faces, key=lambda f: (f.bbox[2] - f.bbox[0]) * (f.bbox[3] - f.bbox[1]))


def embedding_of(app: FaceAnalysis, path: Path) -> np.ndarray:
    """Read an image file and return the normalised 512-d embedding of its largest face."""
    image = cv2.imread(str(path))  # OpenCV loads as BGR, which is what InsightFace expects
    if image is None:
        sys.exit(f"Cannot read image: {path}")
    face = largest_face(app, image)
    if face is None:
        sys.exit(f"No face found in: {path}")
    # normed_embedding has length 1, so the dot product of two of them is the cosine similarity.
    return face.normed_embedding


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity of two vectors that are already normalised = their dot product."""
    return float(np.dot(a, b))


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare the face in the first image with the others.")
    parser.add_argument("reference", type=Path, help="image of the enrolled person")
    parser.add_argument("others", type=Path, nargs="+", help="one or more images to compare with it")
    args = parser.parse_args()

    app = load_model()
    reference = embedding_of(app, args.reference)
    for other in args.others:
        similarity = cosine_similarity(reference, embedding_of(app, other))
        verdict = "same person?" if similarity >= DEMO_THRESHOLD else "different person?"
        print(f"{args.reference.name} vs {other.name}: similarity = {similarity:.3f}  -> {verdict}")


if __name__ == "__main__":
    main()
