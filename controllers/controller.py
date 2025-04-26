import psycopg2
from models.hospital import Hospital
from models.location import Location
from models.patient import Patient
import psycopg2.extras

class Controller:
    def __init__(self, view):
        self.view = view
        self.conn = psycopg2.connect(
            dbname="testdb", user="postgres", password="postgres", host="localhost", port="5432"
        )
        self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def get_all_patients(self):
        self.cursor.execute("SELECT * FROM patient LIMIT 10;")
        rows = self.cursor.fetchall()
        return [Patient(*row) for row in rows]
    
    def get_all_locations(self):
        self.cursor.execute("SELECT * FROM location LIMIT 10;")
        rows = self.cursor.fetchall()
        return[Location(*row) for row in rows]
    
    
    def get_coords(self,city,state,zip_code):
        self.cursor.execute(
            """
            SELECT LATITUDE,LONGITUDE FROM hospital_location WHERE UPPER(city) = %s AND UPPER(state) = %s AND zip = %s
            """,(city.upper(), state.upper(), zip_code))
        result = self.cursor.fetchone()
        if result:
            return float(result[0]), float(result[1])
        return None
    
    def get_hospital_on_location(self, city, state, zip_code):
        self.cursor.execute(
            """
            SELECT * FROM hospital_location WHERE UPPER(city) = %s AND UPPER(state) = %s AND zip = %s
            """,(city.upper(), state.upper(), zip_code))
        rows = self.cursor.fetchall()
        return [Hospital(*row) for row in rows]
    
    def get_nearest_hospital(self,city,state,zip_code):
        coords = self.get_coords(city,state,zip_code)
        if not coords:
            return []
        lat,lon = coords

        self.cursor.execute(
            """
            SELECT * FROM(
            SELECT name, address, city, state, zip, telephone, type, status,county, country, latitude, longitude, owner, helipad,
               (6371 * 2 * ASIN(SQRT(
                   POWER(SIN(RADIANS(%s - latitude) / 2), 2) +
                   COS(RADIANS(%s)) * COS(RADIANS(latitude)) *
                   POWER(SIN(RADIANS(%s - longitude) / 2), 2)
               ))) AS distance_km
            FROM hospital_location
            ) AS sub
            WHERE distance_km <= %s
            ORDER BY distance_km ASC
            """,(lat, lat, lon, 10))
        rows = self.cursor.fetchall()
        return [Hospital(*row) for row in rows]
    
    def get_hospital_by_disease(self, condition):
        self.cursor.execute(
        """
        SELECT hospital, COUNT(*) AS treatment_count
        FROM patient
        WHERE LOWER(medical_condition) = LOWER(%s)
        GROUP BY hospital
        ORDER BY treatment_count DESC
        """,
        (condition,))
        return self.cursor.fetchall()

    def get_hospital_by_history(self,patient_id,name):
        self.cursor.execute(
        """
        SELECT p2.hospital, COUNT(*) AS treated_count
        FROM patient p1
        INNER JOIN patient p2
        ON LOWER(p1.medical_condition) = LOWER(p2.medical_condition)
        WHERE p1.id = %s AND LOWER(p1.name) = LOWER(%s)
        GROUP BY p2.hospital
        ORDER BY treated_count DESC
        """,
        (patient_id, name))
        return self.cursor.fetchall()
    
    def get_hospitals_by_insurance(self,insurance,zip,condition):
        self.cursor.execute(
        """
        SELECT * 
        FROM hospital_location 
        WHERE 
            zip = %s
            AND name IN (
                SELECT mapping.name 
                FROM mapping
                JOIN patient
                  ON patient.hospital = mapping.hospital 
                WHERE LOWER(patient.insurance_provider) = %s
            AND LOWER(patient.medical_condition) = %s
        );
        """,
        (zip,insurance,condition))
        return self.cursor.fetchall()
    
    def get_hospitals_by_flexible_criteria(self, insurance, zip, condition):
        self.cursor.execute(
            """
            SELECT DISTINCT 
                hl.object_id,
                hl.name,
                hl.address,
                hl.city,
                hl.state,
                hl.zip,
                hl.telephone,
                hl.type,
                hl.status,
                hl.helipad,
                p.insurance_provider,
                p.medical_condition
            FROM hospital_location hl
            LEFT JOIN mapping m ON hl.name = m.name
            LEFT JOIN patient p ON p.hospital = m.hospital
            WHERE 
                (
                LOWER(p.insurance_provider) = LOWER(%s)
                OR LOWER(p.medical_condition) = LOWER(%s)
                AND hl.zip = %s
                );
            """,
            (insurance, condition, zip)
        )
        return self.cursor.fetchall()

        




