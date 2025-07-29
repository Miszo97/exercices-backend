import os
from datetime import datetime
from typing import List, Set

from flask import Flask, render_template, request, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
from requests import Response

from adding_exercise import add_exercise
from fetching_exercises import Exercise, fetch_exercises
from get_table_data import get_table_data

# Inicjalizacja aplikacji Firebase
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# pylint: disable=C0103
app = Flask(__name__)
db = firestore.client()


@app.route('/', methods=['GET', 'POST'])
def hello():
    """Return a friendly HTTP greeting."""
    message = "It's running!"

    """Get Cloud Run environment variables."""
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    request_json = request.get_json(silent=True)

    if request.method == 'GET':
        result = fetch_exercises(db)
        exercise_names, rows = get_table_data(exercises=result)
        return render_template('exercise_table.html', exercise_names=exercise_names, rows=rows)

    elif request.method == 'POST':
        if not request_json:
            return "Missing JSON body", 400

        name = request_json.get('name')
        reps = request_json.get('reps')
        duration = request_json.get('duration')
        unit = request_json.get('unit')

        if not name:
            return "Error: 'name' field is required", 400

        result = add_exercise(name=name, reps=reps, duration=duration, unit=unit, db=db)
        response_body = f"<html><body><h1>Exercise Added</h1><p>{result}</p></body></html>"

    else:
        return "Method Not Allowed", 405

    return response_body, 200, {'Content-Type': 'text/html'}

if __name__ == '__main__':
    server_port = os.environ.get('PORT', '8080')
    app.run(debug=False, port=server_port, host='0.0.0.0')