"""MediaPipe Pose landmark extraction for uploaded body photos.

Returns a dict of normalized landmarks per angle, or None if no person detected.
"""
from __future__ import annotations

import io
import logging
from typing import Any

import cv2
import numpy as np
from PIL import Image
import mediapipe as mp

log = logging.getLogger(__name__)

# MediaPipe Pose landmark indices we care about
LM = {
    "nose": 0,
    "left_shoulder": 11, "right_shoulder": 12,
    "left_elbow": 13, "right_elbow": 14,
    "left_wrist": 15, "right_wrist": 16,
    "left_hip": 23, "right_hip": 24,
    "left_knee": 25, "right_knee": 26,
    "left_ankle": 27, "right_ankle": 28,
}

# Lazy-init the pose model once per process
_pose = None


def _get_pose():
    global _pose
    if _pose is None:
        _pose = mp.solutions.pose.Pose(
            static_image_mode=True,
            model_complexity=1,
            enable_segmentation=True,
            min_detection_confidence=0.5,
        )
    return _pose


def _load_image(data: bytes) -> np.ndarray:
    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        # Fallback via PIL
        img_pil = Image.open(io.BytesIO(data)).convert("RGB")
        img = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
    return img


def extract_landmarks(image_bytes: bytes) -> dict[str, Any] | None:
    """Run MediaPipe Pose on a single image. Returns landmarks dict or None."""
    try:
        img = _load_image(image_bytes)
    except Exception as e:
        log.warning("Failed to load image: %s", e)
        return None

    h, w = img.shape[:2]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pose = _get_pose()
    result = pose.process(rgb)

    if not result.pose_landmarks:
        return None

    out: dict[str, Any] = {
        "image_w": w,
        "image_h": h,
        "points": {},
        "visibility": {},
    }
    for name, idx in LM.items():
        lm = result.pose_landmarks.landmark[idx]
        out["points"][name] = {"x": lm.x, "y": lm.y, "z": lm.z}
        out["visibility"][name] = lm.visibility

    if result.segmentation_mask is not None:
        mask = result.segmentation_mask.numpy()
        out["body_pixel_ratio"] = float(mask.mean())
    else:
        out["body_pixel_ratio"] = None

    return out


def extract_set(front: bytes, side: bytes, back: bytes) -> dict[str, dict | None]:
    """Extract landmarks for a 3-photo set. Each value is None if no person found."""
    return {
        "front": extract_landmarks(front),
        "side": extract_landmarks(side),
        "back": extract_landmarks(back),
    }
