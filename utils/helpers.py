import json
import os

def save_to_json(new_data):
    # Get project root folder
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Create path: project_root/data/resume_data.json
    filename = os.path.join(BASE_DIR, "data", "resume_data.json")

    # Create folder if not exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Load old data
    if os.path.exists(filename):
        with open(filename, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    # Add new data
    data.append(new_data)

    # Save file
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

    print("✅ Data saved at:", filename)