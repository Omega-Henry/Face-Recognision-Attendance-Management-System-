"""Desktop dashboard matching the uploaded design.

Run with:
    $ python interface.py
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

import attendance
import registration

APP_BG = "#0d1117"      # dark navy
SIDEBAR_BG = "#111827"  # slightly lighter
CARD_BG = "#1f2937"
HIGHLIGHT = "#facc15"   # yellow
BTN_BG = "#2563eb"
BTN_BG_HOVER = "#1d4ed8"
FONT = ("Segoe UI", 11)


class Dashboard(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("AI‑Powered Face Recognition Attendance")
        self.geometry("1100x650")
        self.configure(bg=APP_BG)
        self.resizable(False, False)

        # Sidebar -----------------------------------------------------------
        sidebar = tk.Frame(self, bg=SIDEBAR_BG, width=220)
        sidebar.pack(side="left", fill="y")
        for text, cmd in [
            ("Student Registration", self.show_register),
            ("View / Authorize Students", self.show_authorize),
            ("Mark Attendance", self.show_mark_attendance),
            ("Attendance Details", self.show_details),
            ("Camera Configuration", self.show_camera_config),
        ]:
            b = tk.Button(sidebar, text=text, font=FONT, fg="white", bg=SIDEBAR_BG,
                        activebackground=CARD_BG, activeforeground="white", bd=0,
                        pady=12, anchor="w", command=cmd)
            b.pack(fill="x")

        # Main area ---------------------------------------------------------
        self.main = tk.Frame(self, bg=APP_BG)
        self.main.pack(fill="both", expand=True)
        self.show_dashboard()

    def _clear(self):
        for w in self.main.winfo_children():
            w.destroy()

    # ------------------ Dashboard ----------------------------------------
    def show_dashboard(self):
        self._clear()
        tk.Label(self.main, text="AI‑Powered Face Recognition Attendance", fg=HIGHLIGHT,
                bg=APP_BG, font=("Segoe UI", 24, "bold")).pack(pady=(40, 10))
        tk.Label(self.main, text="Register students, manage attendance, and integrate AI for seamless recognition.",
                fg="white", bg=APP_BG, font=("Segoe UI", 12)).pack()
        btns = [
            ("Register Students", self.show_register),
            ("Authorize Students", self.show_authorize),
            ("Mark Attendance", self.show_mark_attendance),
            ("View Attendance", self.show_details),
            ("Configure Camera", self.show_camera_config),
        ]
        grid = tk.Frame(self.main, bg=APP_BG)
        grid.pack(pady=40)
        for i, (text, cmd) in enumerate(btns):
            b = tk.Button(grid, text=text, width=20, height=3, command=cmd,
                        font=("Segoe UI", 11, "bold"), fg="white", bg=CARD_BG,
                        activebackground="#374151", bd=0)
            b.grid(row=i//2, column=i%2, padx=25, pady=25)

    # ------------------ Student Registration -----------------------------
    def show_register(self):
        self._clear()
        tk.Label(self.main, text="Register Student", fg=HIGHLIGHT, bg=APP_BG,
                font=("Segoe UI", 18, "bold")).pack(pady=20)
        form = tk.Frame(self.main, bg=APP_BG)
        form.pack()
        for i, label in enumerate(["ID:", "Name:", "Class:"]):
            tk.Label(form, text=label, fg="white", bg=APP_BG, font=FONT).grid(row=i, column=0, sticky="e", pady=5)
        id_entry = tk.Entry(form, width=30)
        name_entry = tk.Entry(form, width=30)
        class_var = tk.StringVar()
        class_cb = ttk.Combobox(form, textvariable=class_var, state="readonly",
                                values=registration.CAMEROON_CLASSES, width=27)
        id_entry.grid(row=0, column=1, padx=10, pady=5)
        name_entry.grid(row=1, column=1, padx=10, pady=5)
        class_cb.grid(row=2, column=1, padx=10, pady=5)

        def submit():
            try:
                registration.add_student(id_entry.get().strip(),
                                        name_entry.get().strip(),
                                        class_var.get())
                messagebox.showinfo("Success", "Student registered successfully.")
                self.show_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(self.main, text="Capture Face & Register", command=submit,
                fg="white", bg=BTN_BG, activebackground=BTN_BG_HOVER, bd=0,
                font=("Segoe UI", 11, "bold"), padx=20, pady=8).pack(pady=20)

    # ------------------ Authorize (placeholder) ---------------------------
    def show_authorize(self):
        self._clear()
        tk.Label(self.main, text="Authorize Students – coming soon…", fg="white", bg=APP_BG).pack(pady=50)

    # ------------------ Mark Attendance -----------------------------------
    def show_mark_attendance(self):
        self._clear()
        tk.Label(self.main, text="Mark Attendance", fg=HIGHLIGHT, bg=APP_BG,
                font=("Segoe UI", 18, "bold")).pack(pady=20)
        sid_entry = tk.Entry(self.main, width=30)
        sid_entry.pack(pady=8)
        sid_entry.insert(0, "Enter Student ID")

        def do_check():
            try:
                ok = attendance.student_check_in(sid_entry.get().strip())
                messagebox.showinfo("Result", "Marked PRESENT" if ok else "Face mismatch – ABSENT recorded")
                self.show_dashboard()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(self.main, text="Proceed", command=do_check, fg="white", bg=BTN_BG,
                activebackground=BTN_BG_HOVER, bd=0, font=("Segoe UI", 11, "bold"),
                padx=20, pady=8).pack(pady=10)

    # ------------------ Attendance Details --------------------------------
    def show_details(self):
        self._clear()
        records = attendance.get_today_records()
        tk.Label(self.main, text=f"Attendance Details – {date.today()}", fg=HIGHLIGHT, bg=APP_BG,
                font=("Segoe UI", 18, "bold")).pack(pady=20)
        if not records:
            tk.Label(self.main, text="No records yet.", fg="white", bg=APP_BG).pack()
            return
        table = tk.Frame(self.main, bg=APP_BG)
        table.pack()
        headers = ("Class", "ID", "Name", "Status")
        for c, h in enumerate(headers):
            tk.Label(table, text=h, bg=CARD_BG, fg="white", width=15, font=("Segoe UI", 10, "bold"),
                    borderwidth=1, relief="ridge").grid(row=0, column=c)
        for r, row in enumerate(records, start=1):
            for c, val in enumerate(row):
                tk.Label(table, text=val, bg=SIDEBAR_BG, fg="white", width=15,
                        borderwidth=1, relief="ridge").grid(row=r, column=c)

    # ------------------ Camera Config (placeholder) -----------------------
    def show_camera_config(self):
        self._clear()
        tk.Label(self.main, text="Camera Configuration – coming soon…", fg="white", bg=APP_BG).pack(pady=50)


if __name__ == "__main__":
    Dashboard().mainloop()
