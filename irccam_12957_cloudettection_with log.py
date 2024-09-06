import os
import cv2
import numpy as np
import mysql.connector
from scipy.io import loadmat
from datetime import datetime, timezone, timedelta
from configparser import ConfigParser
import re

# Funktion zur Wolkenerkennung basierend auf einem Schwellenwert
def detect_cloud_clusters(image_data):
    gray_image = cv2.normalize(image_data, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    _, binary_image = cv2.threshold(gray_image, 200, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(binary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    clusters = []
    for contour in contours:
        M = cv2.moments(contour)
        if M['m00'] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])
            clusters.append((cx, cy))
    
    return clusters

# Funktion zur Berechnung der Sonnenposition
def calculate_sun_position(timestamp, latitude, longitude, altitude=0):
    from pysolar.solar import get_altitude, get_azimuth
    elevation = get_altitude(latitude, longitude, timestamp)
    azimuth = get_azimuth(latitude, longitude, timestamp)
    return azimuth, elevation

# Datenbankverbindung herstellen
def connect_to_database(config_file):
    config = ConfigParser()
    config.read(config_file)
    
    try:
        connection = mysql.connector.connect(
            host=config.get('mysql', 'host'),
            user=config.get('mysql', 'user'),
            password=config.get('mysql', 'password'),
            database=config.get('mysql', 'database')
        )
        return connection
    except mysql.connector.Error as e:
        print(f"Fehler bei der Verbindung zur Datenbank: {e}")
        return None

# Funktion zur Schlüsselsuche: höchsten gültigen Schlüssel finden
def find_highest_key(mat_data):
    available_keys = list(mat_data.keys())
    print(f"Verfügbare Schlüssel: {available_keys}")
    
    # Extrahiere alle 'img_' Schlüssel und sortiere sie
    key_pattern = re.compile(r'img_\d{6}')
    possible_keys = [key for key in available_keys if key_pattern.match(key)]
    
    if possible_keys:
        # Den höchsten Schlüssel nehmen (Sortierung alphabetisch führt zum höchsten Schlüssel)
        highest_key = sorted(possible_keys)[-1]
        print(f"Höchster verfügbarer Schlüssel: {highest_key}")
        return highest_key
    else:
        print("Kein passender Schlüssel in der Datei gefunden.")
        return None

# Funktion zur Verarbeitung der Bilddaten
def process_images(image_directory, latitude, longitude, config_file, delay_hours=40):
    # Suche nach der neuesten Datei
    image_files = [f for f in os.listdir(image_directory) if f.endswith('.12957')]
    latest_file = max(image_files, key=lambda f: os.path.getctime(os.path.join(image_directory, f)))
    file_path = os.path.join(image_directory, latest_file)
    
    print(f"Lade die neueste Datei: {file_path}")
    
    try:
        # Extrahiere Datum und Uhrzeit aus dem Dateinamen (Dateiname: irccam_YYYYMMDDHHMM)
        base_name = os.path.basename(latest_file).replace('.12957', '')
        date_str = base_name.split('_')[1][:8]  # YYYYMMDD
        time_str = base_name.split('_')[1][8:12]  # HHMM
        
        # Konvertiere in ein datetime-Objekt und subtrahiere die Verzögerung
        date = datetime.strptime(date_str, "%Y%m%d")
        time = datetime.strptime(time_str, "%H%M").time()
        timestamp = datetime.combine(date, time).replace(tzinfo=timezone.utc)
        
        # Subtrahiere die Verzögerung, falls zutreffend
        if delay_hours > 0:
            timestamp = timestamp - timedelta(hours=delay_hours)

        print(f"Timestamp (mit Verzögerung) für Datei: {timestamp}")

        # Lade die MAT-Datei
        mat_data = loadmat(file_path)

        # Höchsten Schlüssel finden
        highest_key = find_highest_key(mat_data)

        if highest_key:
            # Sicherstellen, dass der Schlüssel Bilddaten enthält
            if 'image' in mat_data[highest_key].dtype.names:
                image_data = mat_data[highest_key]['image'][0, 0]
                clusters = detect_cloud_clusters(image_data)
                azimuth, elevation = calculate_sun_position(timestamp, latitude, longitude)
                
                connection = connect_to_database(config_file)
                if connection:
                    cursor = connection.cursor()

                    closest_distance = None
                    sun_position = (320, 240)  # Beispiel: Mittelpunkt des Bildes
                    for cluster in clusters:
                        distance = np.linalg.norm(np.array(cluster) - np.array(sun_position))
                        if closest_distance is None or distance < closest_distance:
                            closest_distance = distance

                    try:
                        if image_data is not None:
                            _, img_encoded = cv2.imencode('.png', image_data)
                            if img_encoded is not None:
                                image_blob = img_encoded.tobytes()
                                
                                sql = """
                                INSERT INTO ancillary.image_irccam (date_time, image_data, sun_azimuth, sun_elevation, cloud_flag, cloud_distance)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                """
                                cursor.execute(sql, (timestamp, image_blob, azimuth, elevation, len(clusters) > 0, closest_distance))
                                connection.commit()
                                print(f"Erfolgreich in die Datenbank eingefügt: {timestamp}")
                            else:
                                print("Fehler beim Kodieren des Bildes.")
                        else:
                            print("Kein Bild geladen, Daten werden nicht in die Datenbank eingefügt.")
                    except mysql.connector.Error as e:
                        print(f"Fehler beim Einfügen in die Datenbank: {e}")
                    finally:
                        cursor.close()
                        connection.close()
            else:
                print(f"Kein 'image'-Feld im Schlüssel {highest_key} gefunden.")
        else:
            print("Kein Bild geladen.")
    except Exception as e:
        print(f"Fehler beim Laden der Datei {file_path}: {e}")

# Hauptprogramm
if __name__ == "__main__":
    image_directory = r"\\ad.pmodwrc.ch\Institute\Projects\IRCCAM\IRCCAM_12957\data\2024"
    config_file = "config.ini"
    latitude = 46.813187
    longitude = 9.84422
    
    # Füge eine Verzögerung hinzu (z.B. 40 Stunden Verzögerung)
    delay_hours = 40
    
    process_images(image_directory, latitude, longitude, config_file, delay_hours)
