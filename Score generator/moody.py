import zipfile
import os
import random
from music21 import stream, note, metadata, instrument, clef, key, duration, chord, pitch

def create_measure(notes_list, measure_number, current_key):
    m = stream.Measure(number=measure_number)
    for note_or_chord, dur, accidental_type in notes_list:
        if note_or_chord == "rest":
            r = note.Rest()
            r.duration = duration.Duration(dur)
            m.append(r)
        elif isinstance(note_or_chord, str):
            n = note.Note(note_or_chord)
            n.duration = duration.Duration(dur)
            if accidental_type:
                n.pitch.accidental = pitch.Accidental(accidental_type.lower())
            m.append(n)
        elif isinstance(note_or_chord, list):
            chord_notes = []
            for pitch_name in note_or_chord:
                n = note.Note(pitch_name)
                chord_notes.append(n)
            c = chord.Chord(chord_notes)
            c.duration = duration.Duration(dur)
            m.append(c)
    return m

def transpose(note, semitones):
    note_order = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    flat_note_order = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']

    for i, char in enumerate(note):
        if char.isdigit():
            note_name = note[:i]
            octave = int(note[i:])
            break
    else:
        raise ValueError(f"Invalid note format: {note}")
    if note_name in flat_note_order:
        note_index = flat_note_order.index(note_name)
        note_name = note_order[note_index]
    
    note_index = note_order.index(note_name)
    new_index = (note_index + semitones) % 12
    new_octave = octave + (note_index + semitones) // 12
    return note_order[new_index] + str(new_octave)

def main():
    minor_keys = ["Am", "Em", "Bm", "F#m", "C#m", "G#m", "D#m", "Dm", "Gm", "Cm", "Fm", "Bbm", "Ebm", "Abm"]
    
    selected_key = random.choice(minor_keys)
    
    key_shifts = {
        "Am": 0, "Em": 7, "Bm": 2, "F#m": 9, "C#m": 4, "G#m": 11, "D#m": 6,
        "Dm": 3, "Gm": 10, "Cm": 5, "Fm": 8, "Bbm": 1, "Ebm": 6, "Abm": 4
    }
    
    shift = key_shifts[selected_key]
    s = stream.Score()

    s.metadata = metadata.Metadata()
    s.metadata.title = input("Enter title: ")
    s.metadata.composer = input("Enter composer: ")
    
    right_hand = stream.Part()
    right_hand.id = "P1"
    right_hand.insert(0, instrument.Piano())
    right_hand.insert(0, clef.TrebleClef())
    right_hand.insert(0, key.Key(selected_key))

    left_hand = stream.Part()
    left_hand.id = "P2"
    left_hand.insert(0, instrument.Piano())
    left_hand.insert(0, clef.BassClef())
    left_hand.insert(0, key.Key(selected_key))

    measures = 16

    scale = ["A4", "B4", "C5", "D5", "E5", "F5", "G5", "A5"]

    bass_pattern = [(transpose("A2", shift), 1, None), (transpose("E3", shift), 1, None), (transpose("A3", shift), 1, None), (transpose("E3", shift), 1, None)]

    for i in range(measures):
        right_hand.append(create_measure([
            (transpose(random.choice(scale), shift), 0.5, None),
            (transpose(random.choice(scale), shift), 0.5, None),
            (transpose(random.choice(scale), shift), 0.5, None),
            (transpose(random.choice(scale), shift), 0.5, None),
            (transpose(random.choice(scale), shift), 0.5, None),
            (transpose(random.choice(scale), shift), 0.5, None),
            (transpose(random.choice(scale), shift), 0.5, None),
            (transpose(random.choice(scale), shift), 0.5, None)
        ], i, selected_key))

        left_hand.append(create_measure(bass_pattern, i, selected_key))
    
    left_hand.append(create_measure([([transpose("A2", shift), transpose("C3", shift), transpose("E3", shift), transpose("A3", shift)], 4, None)], i, selected_key))    
    right_hand.append(create_measure([([transpose("C5", shift), transpose("E5", shift), transpose("A5", shift)], 4, None)], i, selected_key))

    s.append(right_hand)
    s.append(left_hand)

    file_name = s.metadata.title.replace(" ", "_")
    xml_filename = file_name + ".xml"
    s.write("musicxml", fp=xml_filename)

    container_xml_content = '''<?xml version="1.0" encoding="UTF-8"?>
    <container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
       <rootfiles>
          <rootfile full-path="{}" media-type="application/vnd.recordare.musicxml+xml"/>
       </rootfiles>
    </container>'''.format(xml_filename)

    os.makedirs("META-INF", exist_ok=True)

    with open("META-INF/container.xml", "w") as f:
        f.write(container_xml_content)

    with zipfile.ZipFile(file_name + ".mxl", 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(xml_filename, arcname=xml_filename)
        zipf.write("META-INF/container.xml", arcname="META-INF/container.xml")

    os.remove(xml_filename)
    os.remove("META-INF/container.xml")
    os.rmdir("META-INF")

if __name__ == "__main__":
    main()