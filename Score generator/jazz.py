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
    major_keys = ["C", "G", "D", "A", "E", "B", "F#", "C#", "F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"]
    selected_key = random.choice(major_keys)
    key_shifts = {
        "C": 0, "G": 7, "D": 2, "A": 9, "E": 4, "B": 11,
        "F#": 6, "C#": 1, "F": 5, "Bb": 10, "Eb": 3, "Ab": 8, "Db": 1, "Gb": 6, "Cb": 11
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
    measure_length = 4.0

    scale = ["C4", "D4", "Eb4", "F4", "G4", "A4", "Bb4", "C5"]

    bass_pattern = [
        [([transpose("D3", shift), transpose("F3", shift), transpose("A3", shift), transpose("C4", shift)], 4, None)],
        [([transpose("C3", shift), transpose("Eb3", shift), transpose("G3", shift), transpose("Bb3", shift)], 4, None)]
    ]

    durations = [duration.Duration(2.0), duration.Duration(1.0), duration.Duration(0.25)]

    def create_right_hand_measure():
        m = stream.Measure(number=1)
        total_duration = 0.0
        
        while total_duration < measure_length:
            dur = random.choice(durations)
            if total_duration + dur.quarterLength > measure_length:
                dur = duration.Duration(measure_length - total_duration)
            
            n = note.Note(transpose(random.choice(scale), shift))
            n.duration = dur
            m.append(n)
            
            total_duration += dur.quarterLength

        return m



    for i in range(measures):
        right_hand.append(create_right_hand_measure())
        
        if i % 2 == 0:
            left_hand.append(create_measure(bass_pattern[0], i, selected_key))
        else:
            left_hand.append(create_measure(bass_pattern[1], i, selected_key))
    
    left_hand.append(create_measure([([transpose("D3", shift), transpose("F3", shift), transpose("A3", shift), transpose("C4", shift)], 4, None)], i, selected_key))    
    right_hand.append(create_measure([([transpose("F4", shift), transpose("A4", shift), transpose("C4", shift), transpose("E4", shift)], 4, None)], i, selected_key))

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