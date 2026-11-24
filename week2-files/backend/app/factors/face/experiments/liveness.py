"""Eye aspect ratio (EAR) and blink detection, Soukupova & Cech (2016).

Pure functions (no camera, no model), so they can be tested on their own and
reused by the real face factor in week 7.

    EAR = (|p2 - p6| + |p3 - p5|) / (2 * |p1 - p4|)

p1, p4 = eye corners; p2, p3 = upper lid; p6, p5 = lower lid (below p2, p3).
Open eye: about 0.25-0.35. Closed eye: below about 0.2.
"""

from __future__ import annotations

import numpy as np

# MediaPipe Face Mesh / Face Landmarker indices in the order p1..p6.
RIGHT_EYE = [33, 160, 158, 133, 153, 144]
LEFT_EYE = [362, 385, 387, 263, 373, 380]

BLINK_THRESHOLD = 0.20  # EAR below this = eye closed
OPEN_THRESHOLD = 0.25  # EAR above this = eye open


def eye_aspect_ratio(points: np.ndarray) -> float:
    """EAR of one eye from 6 (x, y) points in PIXELS, in the order p1..p6."""
    p1, p2, p3, p4, p5, p6 = np.asarray(points, dtype=float)
    vertical = np.linalg.norm(p2 - p6) + np.linalg.norm(p3 - p5)
    horizontal = np.linalg.norm(p1 - p4)
    if horizontal == 0:
        return 0.0
    return float(vertical / (2.0 * horizontal))


def ear_from_landmarks(landmarks, width: int, height: int) -> float:
    """Mean EAR of both eyes from MediaPipe landmarks (normalised x, y in 0..1).

    Landmarks are normalised separately for x and y, so we convert them to pixels
    first; otherwise the ratio would be wrong for non-square images.
    """

    def eye(indices):
        return np.array([[landmarks[i].x * width, landmarks[i].y * height] for i in indices])

    return (eye_aspect_ratio(eye(RIGHT_EYE)) + eye_aspect_ratio(eye(LEFT_EYE))) / 2.0


def count_blinks(ears: list[float], closed: float = BLINK_THRESHOLD, opened: float = OPEN_THRESHOLD) -> int:
    """Count blinks in a sequence of EAR values (one per frame).

    A blink = the eye was open, then closed (EAR < closed) for at least one frame,
    then open again (EAR > opened). Using two thresholds (hysteresis) stops noise
    around a single threshold from counting as many blinks.
    """
    blinks = 0
    state = "unknown"  # we need to see an open eye before a blink can start
    for ear in ears:
        if ear > opened:
            if state == "closed":
                blinks += 1
            state = "open"
        elif ear < closed and state == "open":
            state = "closed"
    return blinks


if __name__ == "__main__":
    # Quick self-check: python liveness.py
    open_eye = [(0, 0), (3, -1.5), (7, -1.5), (10, 0), (7, 1.5), (3, 1.5)]  # EAR 0.3
    closed_eye = [(0, 0), (3, -0.5), (7, -0.5), (10, 0), (7, 0.5), (3, 0.5)]  # EAR 0.1
    assert abs(eye_aspect_ratio(open_eye) - 0.3) < 1e-9
    assert abs(eye_aspect_ratio(closed_eye) - 0.1) < 1e-9
    assert count_blinks([0.3, 0.3, 0.1, 0.12, 0.3, 0.3]) == 1
    assert count_blinks([0.1, 0.3, 0.3]) == 0  # started closed: not a blink
    assert count_blinks([0.3, 0.22, 0.3]) == 0  # half-closed: not a blink
    assert count_blinks([0.3, 0.1, 0.3, 0.1, 0.3]) == 2
    print("liveness.py self-check passed")
