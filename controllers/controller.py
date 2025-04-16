import psycopg2
from models.hospital import Hospital
from models.location import Location
from models.patient import Patient

class Controller:
    def __init__(self, view):
        self.view = view
        self.conn = psycopg2.connect(
            dbname="testdb", user="postgres", password="postgres", host="localhost", port="5432"
        )
        self.cursor = self.conn.cursor()

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

        



