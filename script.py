import firebase_admin
from firebase_admin import credentials
from fetching_exercises import Exercise
from get_table_data import get_table_data

cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred)

# db = firestore.client()

# result = fetch_exercises(db)

# print(result)


from datetime import datetime

exercises = [
    Exercise(name='push-ups', reps=60, duration=None, unit=None, date=datetime(2025, 3, 31)),
    Exercise(name='push-ups', reps=60, duration=None, unit=None, date=datetime(2025, 3, 31)),
    Exercise(name='plank', reps=None, duration=60, unit='seconds', date=datetime(2025, 3, 31)),
    Exercise(name='plank', reps=None, duration=60, unit='seconds', date=datetime(2025, 4, 1)),
    Exercise(name='plank', reps=None, duration=60, unit='seconds', date=datetime(2025, 4, 1)),
    Exercise(name='standing', reps=None, duration=60, unit='seconds', date=datetime(2025, 4, 1))
]





# expected
# exercise_names = ["push-ups", "plank", "squats"]
# rows = [
#     ["2025-03-31", ["60", "30", "50"]],
#     ["2025-04-01", ["50", "40", "60"]]
# ]


results = get_table_data(exercises=exercises)
print(results)

