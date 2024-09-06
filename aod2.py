import mysql.connector
import configparser
from datetime import datetime, timedelta
import os
import logging
import re

# Protokollierung einrichten
logging.basicConfig(filename='aod_data.log', level=logging.DEBUG, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

# Hinzufügen eines StreamHandlers, um Logs im Terminal auszugeben
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
logging.getLogger('').addHandler(console_handler)

# Funktion zum Lesen der Konfigurationsdatei
def read_db_config(filename='config.ini', section='mysql'):
    parser = configparser.ConfigParser()
    parser.read(filename)
    
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception(f'{section} not found in the {filename} file')
    
    return db

# Funktion zum Einlesen der AOD-Daten mit Regex
def read_aod_data(file_path):
    aod_data = []
    filename = os.path.basename(file_path)
    
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
    # Datum extrahieren
    date_line = lines[6]  # '%DATE =2024-08-29\n'
    current_date = date_line.split('=')[1].strip()
    current_date = datetime.strptime(current_date, '%Y-%m-%d').date()

    data_lines = lines[21:]  # Die tatsächlichen Datenzeilen beginnen nach Zeile 21

    # Regex zur Extraktion der Daten
    data_pattern = re.compile(r'\s*(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)')

    for line_number, line in enumerate(data_lines, start=22):
        match = data_pattern.match(line)
        if match:
            try:
                time_in_hours = float(match.group(1))
                hours = int(time_in_hours)
                minutes = int((time_in_hours - hours) * 60)
                datetime_value = datetime.combine(current_date, datetime.min.time()) + timedelta(hours=hours, minutes=minutes)
                
                aod = float(match.group(5))  # Annahme: Spalte 5 (Index 4) ist AOD-Wert bei 500.4 nm

                if aod < 0:
                    aod_flag = 'error'
                elif aod > 0.12:
                    aod_flag = 'flag'
                else:
                    aod_flag = 'ok'

                aod_data.append((datetime_value, aod, aod_flag, filename))
                logging.debug(f"Datensatz hinzugefügt: {datetime_value}, AOD: {aod}, Flag: {aod_flag}")
            except Exception as e:
                logging.error(f"Fehler in Zeile {line_number}: {e}")

    logging.info(f"{len(aod_data)} gültige Datensätze gefunden.")
    return aod_data

# Funktion zum Speichern der Daten in die Datenbank
def store_to_database(aod_data):
    # Lese die Konfigurationsdatei
    db_config = read_db_config()
    
    # Verbinde mit der MySQL-Datenbank
    db = mysql.connector.connect(
        host=db_config['host'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    cursor = db.cursor()

    for data in aod_data:
        datetime_value, aod, aod_flag, filename = data

        # Prüfen, ob der Datensatz bereits vorhanden ist
        cursor.execute("SELECT COUNT(*) FROM aod_measurements WHERE date_time = %s", (datetime_value,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            query = """
            INSERT INTO aod_measurements (date_time, aod, aod_flag, filename)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(query, data)
            logging.debug(f"Datensatz in die Datenbank eingefügt: {datetime_value}, AOD: {aod}, Flag: {aod_flag}")

    # Bestätige die Transaktion und schließe die Verbindung
    db.commit()
    cursor.close()
    db.close()

    logging.info(f"{len(aod_data)} Datensätze wurden in die Datenbank eingefügt.")

def main():
    directory_path = r'\\ad.pmodwrc.ch\Institute\Departments\WRC\SRS\ancillary_data\AOD\2024'
    date_threshold = datetime(2024, 8, 6).date()  # Datumsschwelle ab dem 06.08.2024
    
    # Liste aller Dateien ab dem 06.08.2024
    valid_files = []

    for file in os.listdir(directory_path):
        if file.startswith('DAV_N01_') and file.endswith('.003'):
            try:
                file_date_str = file.split('_')[2].split('.')[0]
                file_date = datetime.strptime(file_date_str, '%Y%m%d').date()
                if file_date >= date_threshold:
                    valid_files.append(os.path.join(directory_path, file))
                    logging.debug(f"Datei hinzugefügt: {file} mit Datum {file_date}")
            except Exception as e:
                logging.error(f"Fehler beim Verarbeiten der Datei {file}: {e}")

    if valid_files:
        for file in valid_files:
            logging.info(f"Verarbeite Datei: {file}")
            aod_data = read_aod_data(file)
            store_to_database(aod_data)
    else:
        logging.error("Keine geeigneten Dateien gefunden")

if __name__ == "__main__":
    main()
