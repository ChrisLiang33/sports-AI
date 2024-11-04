import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timedelta

# traning_data -> adding to main.csv

async def compile_data():
    yesterday_date = (datetime.now() - timedelta(days=1)).strftime("%m-%d")
    today_date = datetime.now().strftime("%m-%d")
    data_file_path = f'data/training_data/{yesterday_date}_training.json'

    team_coverage = defaultdict(lambda: defaultdict(str))

    with open(data_file_path, 'r') as data_file:
        data = json.load(data_file)

    for game in data:
        game_date = game['game_date']
        for team in [game['home_team'], game['away_team']]:
            coverage = game[team]
            team_coverage[team][game_date] = coverage  

    csv_file_path = 'data/csv/live/main.csv'
    csv_data = {}

    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as csvfile:
            existing_data = list(csv.reader(csvfile))
            header = existing_data[0]
            existing_dates = header[1:]  

            for row in existing_data[1:]:
                team_name = row[0]
                csv_data[team_name] = row[1:]

    if yesterday_date not in existing_dates:
        header.append(yesterday_date)  
        for team in csv_data:
            csv_data[team].append('')

    for team in team_coverage:
        if team not in csv_data:
            csv_data[team] = [''] * len(existing_dates)
            csv_data[team].append(team_coverage[team][yesterday_date])
        else:
            csv_data[team][-1] = team_coverage[team][yesterday_date] 

    csv_data_rows = []
    for team, ratings in csv_data.items():
        csv_data_rows.append([team] + ratings)

    backup_file_path = f'data/csv/backup/main_backup_{yesterday_date}.csv'
    if os.path.exists(csv_file_path):
        with open(csv_file_path, 'r') as existing_file:
            existing_data = existing_file.readlines()
        with open(backup_file_path, 'w') as backup_file:
            backup_file.writelines(existing_data)

    with open(csv_file_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(header)
        csv_writer.writerows(csv_data_rows)

    print(f"CSV file '{csv_file_path}' updated successfully.")
    print(f"Backup of the previous CSV file created at '{backup_file_path}'.")
