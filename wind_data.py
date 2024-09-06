import mysql.connector
import configparser
from datetime import datetime, timedelta
import os
import logging

# Protokollierung einrichten
logging.basicConfig(filename='wind_data.log', level=logging.INFO, 
                    format='%(asctime)s:%(levelname)s:%(message)s')

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

# Funktion zum Einlesen der Daten
def read_wind_data(file_path):
    wind_data = []
    current_date = datetime.now().date()  # Das aktuelle Datum

    with open(file_path, 'r') as file:
        for line_number, line in enumerate(file, start=1):
            parts = line.split(',')
            if len(parts) < 27:
                if len(parts) > 1:
                    logging.warning(f"Zeile {line_number}: Zu wenige Teile ({len(parts)})")
                continue

            try:
                # Annahme: Spalte 2 ist das Jahr, Spalte 3 ist der Julianische Tag, Spalte 4 ist die Zeit in Minuten ab 00:00
                year = int(parts[1])
                julian_day = int(parts[2])
                time_in_minutes = int(parts[3])
                
                # Erstelle das Datum aus Jahr und Julianischem Tag
                day = f"{year}{julian_day:03d}"
                date = datetime.strptime(day, '%Y%j').date()
                
                if date != current_date:
                    continue  # Überspringe Daten, die nicht vom aktuellen Tag sind

                # Berechnung der Zeit aus Minuten
                if time_in_minutes < 100:
                    hours = 0
                    minutes = time_in_minutes
                else:
                    hours = time_in_minutes // 100
                    minutes = time_in_minutes % 100
                datetime_value = datetime.combine(date, datetime.min.time()) + timedelta(hours=hours, minutes=minutes)

                windspeed = float(parts[23].strip())  # Spalte 24 (Index 23) ist Windgeschwindigkeit in m/s
                winddirection_degrees = float(parts[26].strip())  # Spalte 27 (Index 26) ist Windrichtung in Grad

                if windspeed < 0.0 or windspeed is None:
                    wind_flag = 'error'
                elif windspeed < 2.5:
                    wind_flag = 'ok'
                else:
                    wind_flag = 'flag'

                winddirection = convert_wind_direction(winddirection_degrees)

                filename = os.path.basename(file_path)

                wind_data.append((datetime_value, windspeed, winddirection, wind_flag, filename))
            except Exception as e:
                logging.error(f"Fehler in Zeile {line_number}: {e}")

            # Ausgabe der ersten paar Zeilen zur Überprüfung des Formats
            if line_number <= 10:
                logging.info(f"Zeile {line_number}: {parts}")

    logging.info(f"{len(wind_data)} gültige Datensätze gefunden.")
    return wind_data

# Funktion zum Umrechnen der Windrichtung in Himmelsrichtungen
def convert_wind_direction(degrees):
    directions = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = int((degrees / 22.5) + 0.5) % 16
    return directions[idx]

# Funktion zum Speichern der Daten in die Datenbank
def store_to_database(wind_data):
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

    for data in wind_data:
        datetime_value, windspeed, winddirection, wind_flag, filename = data

        # Prüfen, ob der Datensatz bereits vorhanden ist
        cursor.execute("SELECT COUNT(*) FROM wind_measurements WHERE date_time = %s", (datetime_value,))
        count = cursor.fetchone()[0]
        
        if count == 0:
            query = """
            INSERT INTO wind_measurements (date_time, windspeed, winddirection, wind_flag, filename)
            VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, data)

    # Bestätige die Transaktion und schließe die Verbindung
    db.commit()
    cursor.close()
    db.close()

    logging.info(f"{len(wind_data)} Datensätze wurden in die Datenbank eingefügt.")

def main():
    file_path = r'\\ad.pmodwrc.ch\Institute\Departments\WRC\SRS\ancillary_data\WIND\CR7X1.DAT'
    
    wind_data = read_wind_data(file_path)
    store_to_database(wind_data)

if __name__ == "__main__":
    main()
