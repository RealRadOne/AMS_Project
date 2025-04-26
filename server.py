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

@app.route('/api/patients',methods=['GET'])
def get_patients():
    patients = controller.get_all_patients()
    return jsonify([vars(p) for p in patients])

@app.route('/api/locations',methods=['GET'])
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
    return jsonify([vars(h) for h in hospitals])

@app.route('/api/condition-hospitals',methods=['POST'])
def get_hospitals_by_condition():
    data = request.get_json()
    condition = data.get('condition','').strip().lower()

    results = controller.get_hospital_by_disease(condition)
    hospitals = [{"hospital": row[0], "treatment_count": row[1]} for row in results]
    return jsonify(hospitals)


@app.route('/api/patient-hospitals',methods=['POST'])
def get_hospitals_by_history():
    data = request.get_json()
    patient_id = int(data.get('patient_id',''))
    name       = data.get('name','').strip().lower()
    
    results    = controller.get_hospital_by_history(patient_id,name)
    hospitals = [{"hospital": row[0], "treatment_count": row[1]} for row in results]
    return jsonify(hospitals)

@app.route('/api/test',methods=['POST'])
def search_hospitals_insurance():
    data = request.get_json()

    zip  = data.get('zip','').strip()
    insurance = data.get('insurance','').strip().lower()
    condition = data.get('condition','').strip().lower()
    data =  controller.get_hospitals_by_insurance(insurance,zip,condition)
    return jsonify(data)


@app.route('/api/search',methods=['POST'])
def search_hospitals():
    data = request.get_json()

    zip = data.get('zip','').strip()
    insurance = data.get('insurance','').strip().lower()
    condition = data.get('condition','').strip().lower()
    age_group = data.get('age_group','').strip().lower()

    data =  controller.get_hospitals_by_flexible_criteria(insurance,zip,condition)
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
