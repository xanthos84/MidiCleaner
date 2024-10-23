import os
from mido import MidiFile, MidiTrack
import math

def subtract_until_non_negative(number, decrement):
    while number - decrement >= 0:
        number -= decrement
    return number


def remove_silence_from_midi(input_path, output_path):
    """
    Entfernt die Stille am Anfang einer MIDI-Datei
    
    :param input_path: Pfad zur Eingabedatei.
    :param output_path: Pfad zur Ausgabedatei.
    """
    mid = MidiFile(input_path)
    new_mid = MidiFile(ticks_per_beat=mid.ticks_per_beat)

    for i, track in enumerate(mid.tracks):
        new_track = MidiTrack()
        tempo = 0
        bpm = 0
        bpm_original = 0
        first_note_time = None
        
        # Variable zum Überprüfen der ersten 'note_on' Nachricht
        first_note_checked = False

        
        for msg in track:
            print(f"Noteinformation: Type: {msg.type} " + str(msg))
            
            if msg.type == 'channel_prefix':
                print(f"Found 'channel_prefix' MetaMessage in Track {i} with channel {msg.channel} and time {msg.time}. Setting time to 0.")
                continue
            
            # ACHTUNG - Aftertouch NICHT entfernen, midi file ändert sich dadurch manchmal das timing!
            # Deswegen als Workaround die values auf 0 gesetzt.. somit stören sie nicht mehr
            if msg.type == 'aftertouch':
                    msg.value = 0
                    print(f"Aftertouch found, set value to 0...")

            if msg.type == 'set_tempo':
                    tempo = msg.tempo
                    print(f"Tempo: {tempo}")
                    bpm_original = 60000000.0 / tempo;
                    bpm = int(round(60000000.0 / tempo));
                    print(f"BPM: {bpm}")
                    print(f"cleaning set_tempo...")
                    continue            
            if msg.type == 'marker':
                    print(f"METAMESSAGE marker time is: {msg} - found, cleaning...")
                    continue

            if msg.type == 'note_on' and msg.velocity > 0:
                if first_note_time is None:
                   first_note_time = msg.time  # Speichere die Zeit der ersten Note
                if not first_note_checked:
                    
                    # Überprüfe, ob die Zeit der ersten Nachricht größer als 481 ist
                    if msg.time > 481:
                        print(f"Erste Nachricht im Track {i} hat eine Zeit von {msg.time}. ")
                        msg.time = subtract_until_non_negative(msg.time, 1920)
                        
                    first_note_checked = True

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
input_directory = 'X:\\MIDIS'  # Pfad zu deinem Verzeichnis mit MIDI-Dateien
output_directory = 'X:\\MIDIS_OUT' # Pfad zum Zielverzeichnis für bearbeitete Dateien

process_directory(input_directory, output_directory)
