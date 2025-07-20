#file for interacting with the SQLite database

import sqlite3
from datetime import datetime

DB_PATH = "data/disease.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symptoms TEXT NOT NULL,
            disease TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def add_patient(symptoms: str, disease: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO patients (symptoms, disease, timestamp) VALUES (?, ?, ?)",
        (symptoms, disease, datetime.now())
    )
    conn.commit()
    conn.close()

def query_cases_by_symptom(symptom: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM patients WHERE symptoms LIKE ?",
        (f"%{symptom}%",)
    )
    results = cursor.fetchall()
    conn.close()
    return results

def print_all_patients():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients")
    rows = cursor.fetchall()
    conn.close()
    
    print("**All Patient Records:")
    for row in rows:
        print(row)