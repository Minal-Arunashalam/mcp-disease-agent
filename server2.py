# server.py
import argparse
from mcp.server.fastmcp import FastMCP
from joblib import load
import sqlite3
from datetime import datetime
import os

# Load model and vectorizer
model = load("infection_model.pkl")
vectorizer = load("vectorizer.pkl")

# SQLite setup
conn = sqlite3.connect("infection_cases.db")
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    condition TEXT,
    location TEXT,
    date TEXT
)
""")
conn.commit()

# Init MCP
mcp = FastMCP()

@mcp.tool(name="diagnose_infection", description="Predict likely infectious diseases given symptoms and region.")
def diagnose_infection(symptoms: list[str], region: str) -> list[str]:
    text = region + " " + " ".join(symptoms)
    X = vectorizer.transform([text])
    probs = model.predict_proba(X)[0]
    top_indices = probs.argsort()[-3:][::-1]
    classes = model.classes_
    return [classes[i] for i in top_indices]

@mcp.tool(name="suggest_tests", description="Suggest lab tests for a suspected disease.")
def suggest_tests(condition: str) -> list[str]:
    test_map = {
        "Dengue": ["Dengue NS1 Antigen", "IgM ELISA"],
        "Flu": ["Influenza PCR", "Rapid Flu A/B Test"],
        "Chikungunya": ["RT-PCR", "IgM ELISA"],
        "Zika": ["Zika PCR", "IgM Serology"],
        "COVID-19": ["RT-PCR", "Rapid Antigen Test"]
    }
    return test_map.get(condition, ["Consult physician for test options."])

@mcp.tool(name="report_case", description="Log a confirmed case to the local disease tracking database.")
def report_case(condition: str, location: str, date: str = None) -> bool:
    date = date or datetime.now().strftime("%Y-%m-%d")
    cursor.execute("INSERT INTO cases (condition, location, date) VALUES (?, ?, ?)", (condition, location, date))
    conn.commit()
    return True

if __name__ == "__main__":
    print("🦠 Infectious Disease Diagnostic MCP Server starting...")
    parser = argparse.ArgumentParser()
    parser.add_argument("--server_type", type=str, default="sse", choices=["sse", "stdio"])
    args = parser.parse_args()
    mcp.run(args.server_type)
