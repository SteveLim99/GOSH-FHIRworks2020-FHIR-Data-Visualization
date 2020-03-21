from flask import Flask, render_template
from fhir_parser import FHIR
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def index():
    fhir = FHIR()
    patients = fhir.get_all_patients()
    return render_template('main.html', patients=patients)

@app.route('/patientObs/<string:id>')
def general(id):
    fhir = FHIR()
    patient = fhir.get_patient(id)
    observations = fhir.get_patient_observations(id)
    spreadSheet = {
        'bodyWeight' : [],
        'BMI' : [],
        'dBP' : [],
        'sBP': [],
        'pain':[],
        'latestObs' : {
            'uuid': "",
            'latestDate': "",
            'type': "",
            'status': "",
            'weight': "",
            'sBP': "",
            'BMI': ""
        }
    }
    for i in observations:
        components = i.components
        for i2 in components: 
            value = i2.value
            if value == None: continue
            date = i.effective_datetime
            dateStr = str(date.day) + "/" + str(date.month) + "/" + str(date.year)
            display = i2.display
            if display == "Body Weight": spreadSheet['bodyWeight'].append((dateStr,value))
            elif display == "Diastolic Blood Pressure": spreadSheet['dBP'].append((dateStr,value)) 
            elif display == "Systolic Blood Pressure": spreadSheet['sBP'].append((dateStr,value))
            elif display == "Body Mass Index": spreadSheet['BMI'].append((dateStr,value))
            elif "Pain severity" in display: spreadSheet['pain'].append((dateStr,value))

    dictItemsToBeSorted = [spreadSheet['bodyWeight'], spreadSheet['BMI'], spreadSheet['dBP'], spreadSheet['sBP'], spreadSheet['pain']]
    sortTime(dictItemsToBeSorted)

    spreadSheet['latestObs']['uuid'] = observations[-1].uuid
    tmp = observations[-1].effective_datetime
    spreadSheet['latestObs']['latestDate'] = str(tmp.day) + "/" + str(tmp.month) + "/" + str(tmp.year)
    spreadSheet['latestObs']['type'] = observations[-1].type
    spreadSheet['latestObs']['status'] = observations[-1].status
    spreadSheet['latestObs']['weight'] = spreadSheet['bodyWeight'][-1][-1]
    spreadSheet['latestObs']['sBP'] = spreadSheet['sBP'][-1][-1]
    spreadSheet['latestObs']['BMI'] = spreadSheet['BMI'][-1][-1]
    return render_template("observations.html", obsData = spreadSheet, patient = patient)

@app.route('/demographics')
def averageBP():
    fhir=FHIR()
    patients = fhir.get_all_patients()
    statistics = {
        'age' : {'0 to 9':0,
                 '10 to 19':0,
                 '20 to 29':0,
                 '30 to 39':0,
                 '40 to 49':0,
                 '50 to 59':0,
                 '60 to 69':0,
                 '70 to 79':0,
                 '80 to 100':0,
                 '> 100':0},
        'marital' : {'Never Married':0,
                     "Single":0,
                     'Married':0},
        'gender' : {'male':0,
                    'female':0},
        'location' : {},
        'race' : {},
        'language': {}
    }
    for patient in patients: 
        age = abs(datetime.today().year - patient.birth_date.year)
        marital = str(patient.marital_status)
        gender = str(patient.gender)
        locations = [str(i.state) for i in patient.addresses]
        race = str(patient.get_extension('us-core-race'))
        languages = [str(i) for i in patient.communications.languages]
        
        if age <= 9: statistics['age']['0 to 9'] += 1 
        elif age >= 10 and age <= 19: statistics['age']['10 to 19'] += 1 
        elif age >= 20 and age <= 29: statistics['age']['20 to 29'] +=  1
        elif age >= 30 and age <= 39: statistics['age']['30 to 39'] += 1 
        elif age >= 40 and age <= 49: statistics['age']['40 to 49'] +=  1
        elif age >= 50 and age <= 59: statistics['age']['50 to 59'] += 1 
        elif age >= 60 and age <= 69: statistics['age']['60 to 69'] +=  1
        elif age >= 70 and age <= 79: statistics['age']['70 to 79'] += 1 
        elif age >= 80 and age <= 100: statistics['age']['80 to 100'] +=  1
        else: statistics['age']['> 100'] += 1

        statistics['marital'][marital] += 1
        statistics['gender'][gender] += 1
        for i in locations:
            if statistics['location'].get(i) == None: statistics['location'][i] = 1
            else: statistics['location'][i] += 1
        
        if statistics['race'].get(race) == None: statistics['race'][race] = 1 
        else: statistics['race'][race] += 1

        for i in languages:
            if statistics['language'].get(i) == None: statistics['language'][i] = 1
            else: statistics['language'][i] += 1
    statistics['age'] = statistics['age'].values()
    statistics['marital'] = statistics['marital'].values() 
    statistics['gender'] = statistics['gender'].values() 
    return render_template("demographic.html", stats = statistics)

def sortTime(inputList):
    for i in inputList:
        i.sort(key = lambda x : datetime.strptime(x[0], "%d/%m/%Y"))


if __name__ == "__main__":
    app.run(debug=True)