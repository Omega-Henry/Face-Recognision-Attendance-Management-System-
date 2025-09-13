"""Reusable attendance logic + CLI. Import into GUI or run standalone."""

from __future__ import annotations

import pickle
from datetime import date
from pathlib import Path

import cv2
import face_recognition
import numpy as np
import sqlite3

DB_PATH = Path(__file__).with_name("school.db")
THRESHOLD = 0.45  # Euclidean distance threshold

# --------------------------- DATABASE ---------------------------------------

def init_db() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH)

# --------------------------- FACE HELPERS -----------------------------------

def _snap_encoding(prompt: str) -> np.ndarray | None:
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("[ERROR] Webcam not found")
        return None
    print(prompt)
    enc = None
    while True:
        ok, frame = cam.read()
        if not ok:
            break
        cv2.imshow("Attendance", frame)
        key = cv2.waitKey(1) & 0xFF
        if key == ord("s"):
            boxes = face_recognition.face_locations(frame[:, :, ::-1])
            if len(boxes) != 1:
                print("One face only …")
                continue
            enc = face_recognition.face_encodings(frame[:, :, ::-1], boxes)[0]
            break
        elif key == ord("q"):
            break
    cam.release()
    cv2.destroyAllWindows()
    return enc


def _match(known: np.ndarray, unknown: np.ndarray) -> bool:
    return np.linalg.norm(known - unknown) < THRESHOLD

# --------------------------- PUBLIC API -------------------------------------

def student_check_in(student_id: str) -> bool:
    """Return True if verified & marked present, False otherwise."""
    con = init_db()
    cur = con.cursor()
    cur.execute("SELECT encoding FROM students WHERE id=?", (student_id,))
    row = cur.fetchone()
    if not row:
        raise ValueError("ID not found")
    known = pickle.loads(row[0])
    unknown = _snap_encoding("Look at camera and press 's' to capture …")
    if unknown is None:
        raise RuntimeError("Face capture failed")
    status = "present" if _match(known, unknown) else "absent"
    today = str(date.today())
    con.execute("INSERT OR REPLACE INTO attendance VALUES (?,?,?)",
                (student_id, today, status))
    con.commit()
    return status == "present"


def get_today_records() -> list[tuple]:
    """Return list of (class, id, name, status) for today's attendance."""
    con = init_db()
    today = str(date.today())
    cur = con.cursor()
    cur.execute(
        "SELECT s.class, s.id, s.name, a.status FROM attendance a "
        "JOIN students s ON s.id=a.id WHERE a.date=? ORDER BY s.class, s.name",
        (today,),
    )
    return cur.fetchall()

# ----------------------------- CLI FALLBACK ---------------------------------

def _cli():
    user_id = input("Enter your ID: ").strip()
    if user_id.upper().startswith("T"):
        print("[TODO] Teacher CLI not implemented in this minimal edition")
    else:
        try:
            if student_check_in(user_id):
                print("[✓] Marked PRESENT.")
            else:
                print("[✗] Face mismatch – ABSENT recorded.")
        except Exception as e:
            print("[ERROR]", e)

if __name__ == "__main__":
    _cli()