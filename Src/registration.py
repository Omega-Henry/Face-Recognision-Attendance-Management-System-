from __future__ import annotations

import pickle
from pathlib import Path

import cv2
import face_recognition
import numpy as np
import sqlite3

# ------------------------------ CONFIG --------------------------------------
DB_PATH = Path(__file__).with_name("school.db")
CAMEROON_CLASSES = [
    "Form One", "Form Two", "Form Three", "Form Four", "Form Five",
    "Lower Sixth", "Upper Sixth",
]

# --------------------------- DB INITIALISATION -----------------------------

def init_db() -> sqlite3.Connection:
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS students (
                id       TEXT PRIMARY KEY,
                name     TEXT NOT NULL,
                class    TEXT NOT NULL,
                encoding BLOB NOT NULL
            )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS teachers (
                id       TEXT PRIMARY KEY,
                name     TEXT NOT NULL,
                encoding BLOB NOT NULL
            )"""
    )
    cur.execute(
        """CREATE TABLE IF NOT EXISTS attendance (
                id     TEXT,
                date   TEXT,
                status TEXT,
                PRIMARY KEY(id, date)
            )"""
    )
    con.commit()
    return con

# --------------------------- CAMERA / ENCODING ------------------------------

def capture_face_encoding() -> np.ndarray:
    """Open webcam, wait for 's' key, return single‑face encoding."""
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        raise RuntimeError("Cannot open webcam – check permissions / device index")
    print("[INFO] Show face and press 's' to capture – 'q' to cancel …")
    enc: np.ndarray | None = None
    while True:
        ok, frame = cam.read()
        if not ok:
            print("[ERROR] Webcam frame failure")
            break
        cv2.imshow("Face Capture", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            boxes = face_recognition.face_locations(frame[:, :, ::-1])
            if len(boxes) != 1:
                print("[WARN] Ensure exactly one face is visible …")
                continue
            enc = face_recognition.face_encodings(frame[:, :, ::-1], boxes)[0]
            break
        elif key == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()
    if enc is None:
        raise RuntimeError("Capture aborted or no face detected")
    return enc

# ---------------------------- PUBLIC HELPERS --------------------------------

def add_student(id_num: str, name: str, school_class: str) -> None:
    """Register a student programmatically (used by GUI)."""
    if school_class not in CAMEROON_CLASSES:
        raise ValueError("Invalid class selection")
    con = init_db()
    enc_blob = pickle.dumps(capture_face_encoding())
    try:
        con.execute("INSERT INTO students VALUES (?,?,?,?)",
                    (id_num, name, school_class, enc_blob))
        con.commit()
    except sqlite3.IntegrityError as e:
        raise ValueError("ID already exists") from e


def add_teacher(id_num: str, name: str) -> None:
    con = init_db()
    enc_blob = pickle.dumps(capture_face_encoding())
    try:
        con.execute("INSERT INTO teachers VALUES (?,?,?)", (id_num, name, enc_blob))
        con.commit()
    except sqlite3.IntegrityError as e:
        raise ValueError("ID already exists") from e

# ----------------------------- CLI FALLBACK ---------------------------------

def _cli():
    con = init_db()
    role = input("Register as (S)tudent or (T)eacher? [S/T]: ").strip().upper()
    if role not in {"S", "T"}:
        print("[ERROR] Invalid choice – exiting …")
        return
    id_num = input("Enter unique ID: ").strip()
    name = input("Enter full name: ").strip()
    if role == "S":
        print("Select class:")
        for i, cls in enumerate(CAMEROON_CLASSES, 1):
            print(f" {i}. {cls}")
        try:
            school_class = CAMEROON_CLASSES[int(input("Number 1‑7: ")) - 1]
        except Exception:
            print("Bad selection – abort.")
            return
        add_student(id_num, name, school_class)
    else:
        add_teacher(id_num, name)
    print("[✓] Registration successful!")

if __name__ == "__main__":
    _cli()
