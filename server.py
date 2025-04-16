from flask import Flask, jsonify, send_from_directory,request
from controllers.controller import Controller
from views.view import View
from geo_utils import haversine
import os

app = Flask(__name__, static_folder='website')
controller = Controller(View())

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/website/<path:path>')
def serve_static_file(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/patients')
def get_patients():
    patients = controller.get_all_patients()
    return jsonify([vars(p) for p in patients])

@app.route('/api/locations')
def get_hospitals():
    locations = controller.get_all_locations()
    return jsonify([vars(l) for l in locations])

@app.route('/api/nearest-hospitals',methods=['POST'])
def get_nearest_by_location():
    data = request.get_json()
    city = data.get('city', '').strip().upper()
    state = data.get('state', '').strip().upper()
    zip_code = data.get('zip', '').strip()

    hospitals = controller.get_nearest_hospital(city,state,zip_code)
    print(city)
    print(hospitals)
    return jsonify([vars(h) for h in hospitals])

@app.route('/api/condition-hospitals',methods=['POST'])
def get_hospitals_by_condition():
    data = request.get_json()
    condition = data.get('condition','').strip().lower()

    results = controller.get_hospital_by_disease(condition)
    hospitals = [{"hospital": row[0], "treatment_count": row[1]} for row in results]
    return jsonify(hospitals)

if __name__ == '__main__':
    app.run(debug=True)
