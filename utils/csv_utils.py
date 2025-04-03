import json
import csv
import os
import pandas as pd


def parse_response(response_text, filename):
    """Parses the response text and extracts structured data."""
    data = {"Reference": filename}

    try:
        # Attempt to parse as JSON
        response_json = json.loads(response_text.strip('<json>').strip('</json>'))
        data.update(response_json)
    except (ValueError, AttributeError):
        # If not JSON, parse as a regular string
        for line in response_text.strip().split('\n'):
            line = line.strip()
            if line:
                if ':' in line:
                    key, value = line.split(':', 1)
                    data[key.strip()] = value.strip().strip('"')
                else:
                    data[line] = None

    # Convert numerical values to appropriate types
    for key, value in data.items():
        if value is not None:
            try:
                data[key] = float(value)
            except ValueError:
                try:
                    data[key] = int(value)
                except ValueError:
                    data[key] = value

    return data


def write_data_to_csv(data, csv_file_path, fieldnames):
    """Writes extracted data into a CSV file."""
    os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

    with open(csv_file_path, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write the header if the file is empty
        if os.path.getsize(csv_file_path) == 0:
            writer.writeheader()

        writer.writerow({key: data.get(key, "") for key in fieldnames})


def create_csv(file_path):
    """Creates an empty CSV file."""
    with open(file_path, "w") as f:
        pass


def update_csv(file_path, updated_data):
    """Updates an existing CSV file using pandas."""
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)

        # Update the dataframe with new data
        for key, value in updated_data.items():
            if key in df.columns:
                df[key] = value

        df.to_csv(file_path, index=False)
        return f"File {file_path} updated successfully."
    return "File not found."


def delete_csv(file_path):
    """Deletes a CSV file."""
    if os.path.exists(file_path):
        os.remove(file_path)
        return f"File {file_path} deleted successfully."
    return "File not found."
