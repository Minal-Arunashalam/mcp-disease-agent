from utils.db import init_db, add_patient, query_cases_by_symptom, print_all_patients

if __name__ == "__main__":
    init_db()
    add_patient("fever, cough", "flu")
    add_patient("headache, nausea", "malaria")

    print("Sample query for 'fever':")
    print_all_patients()
