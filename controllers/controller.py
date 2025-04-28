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
    
    def get_hospitals_by_location(self, latitude, longitude, distance):
        self.cursor.execute(
        """
        SELECT *
        FROM (
            SELECT *, (
                3959 * acos(
                    cos(radians(%s)) * cos(radians(latitude)) *
                    cos(radians(longitude) - radians(%s)) +
                    sin(radians(%s)) * sin(radians(latitude))
                )
            ) AS distance_miles
            FROM hospital_location
        ) AS sub
        WHERE distance_miles <= %s
        ORDER BY distance_miles ASC
        """,
        (latitude, longitude, latitude, distance))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows]  # assuming RealDictCursor

    
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
    
    def get_hospitals_by_flexible_criteria(self, latitude, longitude, distance):
        self.cursor.execute(
        """
        SELECT 
        sub.name,
        sub.address, 
        sub.county,
        sub.distance_miles,
        sub.helipad,
        sub.telephone,
        sub.type,
        sub.zip,
        sub.status,
        patient.insurance_provider, 
        patient.medical_condition
        FROM (
            SELECT *, (
                3959 * acos(
                    cos(radians(%s)) * cos(radians(latitude)) *
                    cos(radians(longitude) - radians(%s)) +
                    sin(radians(%s)) * sin(radians(latitude)))
            ) AS distance_miles
            FROM hospital_location
        ) AS sub
        JOIN mapping ON mapping.name = sub.name
        JOIN patient ON patient.hospital = mapping.hospital
        WHERE distance_miles <= %s
        """,
        (latitude, longitude, latitude, distance))
        return self.cursor.fetchall()


        




