import pandas as pd
import psycopg2

def load_patients_from_csv(cur, df):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS patient (
            id SERIAL PRIMARY KEY,
            name TEXT,
            age INTEGER,
            gender TEXT,
            blood_type TEXT,
            medical_condition TEXT,
            date_of_admission DATE,
            doctor TEXT,
            hospital TEXT,
            insurance_provider TEXT,
            billing_amount NUMERIC,
            admission_type TEXT,
            discharge_date DATE,
            medication TEXT,
            test_results TEXT
        );
    """)

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO patient (
                name, age, gender, blood_type, medical_condition,
                date_of_admission, doctor, hospital, insurance_provider,
                billing_amount, admission_type, discharge_date,
                medication, test_results
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            row['Patient Name'].title(),
            int(row['Age']),
            row['Gender'],
            row['Blood Type'],
            row['Medical Condition'],
            row['Date of Admission'],
            row['Doctor'],
            row['Hospital'],
            row['Insurance Provider'],
            float(row['Billing Amount']),
            row['Admission Type'],
            row['Discharge Date'],
            row['Medication'],
            row['Test Results']
        ))

def load_hospitals_from_csv(cur, df):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS hospital_location (
            object_id INTEGER PRIMARY KEY,
            name TEXT,
            address TEXT,
            city TEXT,
            state TEXT,
            zip TEXT,
            telephone TEXT,
            type TEXT,
            status TEXT,
            county TEXT,
            country TEXT,
            latitude NUMERIC,
            longitude NUMERIC,
            owner TEXT,
            helipad TEXT
        );
    """)

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO hospital_location (
                object_id, name, address, city, state, zip, telephone,
                type, status, county, country, latitude, longitude, owner, helipad
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (object_id) DO NOTHING;
        """, (
            int(row['OBJECTID']),
            row['NAME'],
            row['ADDRESS'],
            row['CITY'],
            row['STATE'],
            str(row['ZIP']),
            row['TELEPHONE'],
            row['TYPE'],
            row['STATUS'],
            row['COUNTY'],
            row['COUNTRY'],
            float(row['LATITUDE']),
            float(row['LONGITUDE']),
            row['OWNER'],
            row['HELIPAD']
        ))

def load_mapping_from_csv(cur,df):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS mapping (
            Hospital TEXT PRIMARY KEY,
            name TEXT
        );
    """)

    for _, row in df.iterrows():
        cur.execute("""
            INSERT INTO mapping 
            (
                Hospital,name
            )VALUES (%s, %s)
            ON CONFLICT (Hospital) DO NOTHING;
        """, (
            row['Hospital'],
            row['NAME']
            ))

def main():
    conn = psycopg2.connect(
        dbname="testdb", user="postgres", password="postgres", host="localhost", port="5432"
    )
    cur = conn.cursor()

    patient_df = pd.read_csv("patient_data.csv")
    load_patients_from_csv(cur, patient_df)

    hospital_df = pd.read_csv("hospital_location.csv")
    load_hospitals_from_csv(cur, hospital_df)

    mapping_df = pd.read_csv("mapping.csv")
    load_mapping_from_csv(cur, mapping_df)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ All CSV data loaded into PostgreSQL successfully.")

if __name__ == "__main__":
    main()
