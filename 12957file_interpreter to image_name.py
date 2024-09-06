import os
from scipy.io import loadmat
from datetime import datetime, timedelta

# Function to calculate the dynamic image key based on a given time
def generate_dynamic_key(current_time):
    # Extract hour, minute, and second from the time
    hour = current_time.strftime("%H")
    minute = current_time.strftime("%M")
    second = current_time.strftime("%S")
    
    # Construct the image key in the format 'img_HHMMSS'
    key = f"img_{hour}{minute}{second}"
    return key

# Function to load and extract the appropriate image data from the MAT file
def process_file(file_path, target_time):
    print(f"Lade die Datei: {file_path}")
    
    try:
        # Load the MAT file
        mat_data = loadmat(file_path)
        
        # Generate the dynamic image key based on the target time
        dynamic_key = generate_dynamic_key(target_time)
        print(f"Dynamischer Schlüssel: {dynamic_key}")
        
        # Check if the exact key exists
        if dynamic_key not in mat_data:
            print(f"Schlüssel {dynamic_key} nicht gefunden, Suche nach nächstem verfügbaren Schlüssel.")
            available_keys = [key for key in mat_data.keys() if key.startswith('img_')]
            
            if available_keys:
                # Use the highest available key if the exact match is not found
                closest_key = max(available_keys)
                print(f"Bilddaten für Schlüssel {closest_key} geladen.")
                image_data = mat_data[closest_key]['image'][0, 0]
                return image_data
            else:
                print("Kein passender Schlüssel in der Datei gefunden.")
                return None
        else:
            print(f"Bilddaten für Schlüssel {dynamic_key} geladen.")
            image_data = mat_data[dynamic_key]['image'][0, 0]
            return image_data
        
    except Exception as e:
        print(f"Fehler beim Laden der Datei {file_path}: {e}")
        return None

# Function to analyze data for the last 'n' hours with a buffer for delay
def analyze_last_n_hours(directory, hours_to_analyze, delay_in_minutes=60):
    # Get the current time
    current_time = datetime.now()
    
    # Iterate over the last 'n' hours
    for i in range(hours_to_analyze):
        # Calculate the time for the current iteration (subtract 'i' hours from the current time)
        target_time = current_time - timedelta(hours=i)
        
        # Create the file name based on the target time (in the format YYYYMMDDHH00)
        file_name = f"irccam_{target_time.strftime('%Y%m%d%H00')}.12957"
        file_path = os.path.join(directory, file_name)
        
        # Check if the file exists (allow for a delay in upload)
        if os.path.exists(file_path):
            # Process the file and attempt to extract the image data
            image_data = process_file(file_path, target_time)
            
            if image_data is not None:
                print(f"Bild erfolgreich für {target_time} geladen.")
            else:
                print(f"Kein Bild für {target_time} geladen.")
        else:
            # Add a buffer to account for delay in file upload
            delayed_time = target_time - timedelta(minutes=delay_in_minutes)
            file_name_delayed = f"irccam_{delayed_time.strftime('%Y%m%d%H00')}.12957"
            file_path_delayed = os.path.join(directory, file_name_delayed)
            
            if os.path.exists(file_path_delayed):
                # Process the delayed file
                image_data = process_file(file_path_delayed, delayed_time)
                
                if image_data is not None:
                    print(f"Bild erfolgreich für verzögerten Zeitpunkt {delayed_time} geladen.")
                else:
                    print(f"Kein Bild für {delayed_time} geladen.")
            else:
                print(f"Datei {file_name} und auch verzögerte Datei {file_name_delayed} nicht gefunden.")

# Main Program
if __name__ == "__main__":
    # Directory where the 2024 .12957 files are stored
    directory_2024 = r"\\ad.pmodwrc.ch\Institute\Projects\IRCCAM\IRCCAM_12957\data\2024"
    
    # Number of hours you want to analyze (e.g., last 5 hours)
    hours_to_analyze = 40
    
    # Delay in minutes to account for upload delays (e.g., 60 minutes)
    delay_in_minutes = 60
    
    # Analyze the images for the last 'n' hours with a delay buffer
    analyze_last_n_hours(directory_2024, hours_to_analyze, delay_in_minutes)
