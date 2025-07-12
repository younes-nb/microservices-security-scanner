import json
import os

def generate_json_output(components_data: dict, log_callback, file_path="output/discovered_components.json"):
    try:
        output_dir = os.path.dirname(file_path)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir) 
        with open(file_path, "w", encoding='utf-8') as f:
            json.dump(components_data, f, indent=4) 
        log_callback(f"SUCCESS: Component data saved to '{file_path}'")
    except Exception as e:
        log_callback(f"ERROR: Failed to generate JSON file: {e}")