import os
from mido import MidiFile, MidiTrack

def remove_silence_from_midi(input_path, output_path):
    """
    Entfernt die Stille am Anfang einer MIDI-Datei und setzt die Zeit der ersten Nachricht auf 0, falls sie größer als 15000 ist.
    
    :param input_path: Pfad zur Eingabedatei.
    :param output_path: Pfad zur Ausgabedatei.
    """
    mid = MidiFile(input_path)
    new_mid = MidiFile()

    for i, track in enumerate(mid.tracks):
        new_track = MidiTrack()
        notes_started = False
        
        # Variable zum Überprüfen der ersten 'note_on' Nachricht
        first_note_checked = False

        for msg in track:
            if msg.type == 'channel_prefix':
                print(f"Found 'channel_prefix' MetaMessage in Track {i} with channel {msg.channel} and time {msg.time}. Setting time to 0.")
                # time auf 0 setzen
                msg.time = 0
            if msg.type == 'note_on' and msg.velocity > 0:
                if not first_note_checked:
                    
                    # Überprüfe, ob die Zeit der ersten Nachricht größer als 15000 ist
                    if msg.time > 100:
                        print(f"Erste Nachricht im Track {i} hat eine Zeit von {msg.time}. Setze auf 0.")
                        msg.time = 0
                    first_note_checked = True
                # notes_started = True

            # if notes_started:
            new_track.append(msg)

        new_mid.tracks.append(new_track)

    new_mid.save(output_path)

def process_directory(input_dir, output_dir):
    """
    Durchsucht ein Verzeichnis nach MIDI-Dateien und entfernt die Stille am Anfang jeder Datei.
    
    :param input_dir: Verzeichnis mit den Eingabedateien.
    :param output_dir: Verzeichnis, in dem die bearbeiteten Dateien gespeichert werden sollen.
    """
    # Erstelle das Ausgabeverzeichnis, falls es nicht existiert
    os.makedirs(output_dir, exist_ok=True)
    
    # Durchsuchen des Eingabeverzeichnisses und aller Unterverzeichnisse
    for root, dirs, files in os.walk(input_dir):
        for filename in files:
            if filename.endswith(".mid") or filename.endswith(".midi"):
                input_path = os.path.join(root, filename)
                
                # Erstelle den entsprechenden Unterordner im Ausgabeordner
                relative_path = os.path.relpath(root, input_dir)
                output_folder = os.path.join(output_dir, relative_path)
                os.makedirs(output_folder, exist_ok=True)
                
                output_path = os.path.join(output_folder, filename)

                print(f"Bearbeite Datei: {input_path} -> {output_path}")
                remove_silence_from_midi(input_path, output_path)

# Beispielaufruf
input_directory = 'put_your_input_dir_here'  # Pfad zu deinem Verzeichnis mit MIDI-Dateien
output_directory = 'put_your_destination_dir_here' # Pfad zum Zielverzeichnis für bearbeitete Dateien

process_directory(input_directory, output_directory)
