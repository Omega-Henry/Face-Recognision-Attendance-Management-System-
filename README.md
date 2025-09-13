# Face Recognition Attendance Management System

Simple, school-oriented attendance system. Students **enroll** with **Class ID + Name + Face**; later, attendance is **marked automatically** after **face verification**. Data is stored in a local **SQLite** database.

---

## ✨ Features
- **Face enrollment**: save student identity (Class ID, Name) + face embeddings
- **Real-time recognition**: webcam verifies the face and marks the student **Present**
- **SQLite storage**: classes, students, attendance logs (date/time)
- **CSV export**: optional export of daily attendance
- **Offline-friendly**: runs locally, no internet required

---

## 🧰 Tech Stack
- **Python 3.x**, **OpenCV**
- One of:
  - **face_recognition** (dlib) _or_ **Mediapipe** (depending on your code)
- **SQLite3** for the database

> If your code uses different libs, keep this section but adjust library names.

---

## ⚙️ Installation
Create and activate a virtual environment, then install requirements.

```bash
python -m venv .venv
# Linux/Mac:
source .venv/bin/activate
# Windows (PowerShell):
# .venv\Scripts\Activate.ps1

pip install --upgrade pip
pip install -r requirements.txt
