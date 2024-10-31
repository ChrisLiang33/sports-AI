import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

# Get today's date
yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d")
today_date = datetime.now().strftime("%m-%d")
data_file_path = f'data/training_data/{yesterday_date}_training.json'

# Prepare data structure for aggregation
team_coverage = defaultdict(lambda: defaultdict(str))

# Load the data from the JSON file
with open(data_file_path, 'r') as data_file:
    data = json.load(data_file)

# Process the data
for game in data:
    game_date = game['game_date']
    for team in [game['home_team'], game['away_team']]:
        coverage = game[team]
        team_coverage[team][game_date] = coverage  # Store coverage rating for each team and date

# Prepare to update the CSV
csv_file_path = 'data/csv/main.csv'
csv_data = {}

# Check if the CSV file already exists
if os.path.exists(csv_file_path):
    with open(csv_file_path, 'r') as csvfile:
        existing_data = list(csv.reader(csvfile))
        # Read existing teams and their coverage
        header = existing_data[0]
        existing_dates = header[1:]  # Get existing dates (excluding the first column)

        # Store existing data in a dictionary
        for row in existing_data[1:]:
            team_name = row[0]
            csv_data[team_name] = row[1:]  # Store the coverage ratings for each team

# Check if the current date is new
if yesterday_date not in existing_dates:
    header.append(yesterday_date)  # Add new date to the header
    # Initialize existing teams with empty ratings for the new date
    for team in csv_data:
        csv_data[team].append('')  # Default to empty if no coverage exists for the new date

# Update coverage ratings for each team
for team in team_coverage:
    if team not in csv_data:
        # If team doesn't exist, create a new entry
        csv_data[team] = [''] * len(existing_dates)  # Initialize with empty strings for existing dates
        csv_data[team].append(team_coverage[team][yesterday_date])  # Add today's coverage for the new team
    else:
        # If the team exists, update its coverage for today's date
        csv_data[team][-1] = team_coverage[team][yesterday_date]  # Update the last entry which corresponds to today's date

# Prepare CSV data with updated coverage
csv_data_rows = []
for team, ratings in csv_data.items():
    csv_data_rows.append([team] + ratings)

# Create a backup of the existing CSV file
backup_file_path = f'data/csv/main_backup_{today_date}.csv'
if os.path.exists(csv_file_path):
    with open(csv_file_path, 'r') as existing_file:
        existing_data = existing_file.readlines()
    with open(backup_file_path, 'w') as backup_file:
        backup_file.writelines(existing_data)

# Write to the CSV file (overwrite mode to update entire content)
with open(csv_file_path, 'w', newline='') as csvfile:
    csv_writer = csv.writer(csvfile)
    # Write the header
    csv_writer.writerow(header)
    # Write the data
    csv_writer.writerows(csv_data_rows)

print(f"CSV file '{csv_file_path}' updated successfully.")
print(f"Backup of the previous CSV file created at '{backup_file_path}'.")
