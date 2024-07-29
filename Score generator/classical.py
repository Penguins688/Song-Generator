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


def create_ending_measures1(selected_key, i, left_hand, right_hand):
    key_shifts = {
        "C": 0, "G": 7, "D": 2, "A": 9, "E": 4, "B": 11,
        "F#": 6, "C#": 1, "F": 5, "Bb": 10, "Eb": 3, "Ab": 8, "Db": 1, "Gb": 6, "Cb": 11
    }
    
    shift = key_shifts[selected_key]
    bass_notes = [(transpose("F2", shift), 1, None), (transpose("C3", shift), 1, None), (transpose("F3", shift), 2, None)]
    measure = create_measure(bass_notes, i, selected_key)
    left_hand.append(measure)
    treble_notes = [("rest", 4, None)]
    measure = create_measure(treble_notes, i, selected_key)
    right_hand.append(measure)
    i += 1
    bass_notes = [(transpose("G#3", shift), 4, None)]
    measure = create_measure(bass_notes, i, selected_key)
    left_hand.append(measure)
    treble_notes = [("rest", 4, None)]
    measure = create_measure(treble_notes, i, selected_key)
    right_hand.append(measure)
    i += 1
    bass_notes = [([transpose("C2", shift), transpose("E2", shift), transpose("G2", shift), transpose("C3", shift)], 4, None)]
    treble_notes = [([transpose("C4", shift), transpose("E4", shift), transpose("G4", shift), transpose("C5", shift)], 4, None)]
    bass_measure = create_measure(bass_notes, i, selected_key)
    left_hand.append(bass_measure)
    measure = create_measure(treble_notes, i, selected_key)
    right_hand.append(measure)
    return i

def main():
    major_keys = ["C", "G", "D", "A", "E", "B", "F#", "C#", "F", "Bb", "Eb", "Ab", "Db", "Gb", "Cb"]
    selected_key = random.choice(major_keys)
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
    i = 1

    scales = {
        "C": ["C4", "D4", "E4", "F4", "G4", "A4", "B4"],
        "G": ["G4", "A4", "B4", "C5", "D5", "E5", "F#5"],
        "D": ["D4", "E4", "F#4", "G4", "A4", "B4", "C#5"],
        "A": ["A4", "B4", "C#5", "D5", "E5", "F#5", "G#5"],
        "E": ["E4", "F#4", "G#4", "A4", "B4", "C#5", "D#5"],
        "B": ["B4", "C#5", "D#5", "E5", "F#5", "G#5", "A#5"],
        "F#": ["F#4", "G#4", "A#4", "B4", "C#5", "D#5", "E#5"],
        "C#": ["C#4", "D#4", "E#4", "F#4", "G#4", "A#4", "B#4"],
        "F": ["F4", "G4", "A4", "Bb4", "C5", "D5", "E5"],
        "Bb": ["Bb4", "C5", "D5", "Eb5", "F5", "G5", "A5"],
        "Eb": ["Eb4", "F4", "G4", "Ab4", "Bb4", "C5", "D5"],
        "Ab": ["Ab4", "Bb4", "C5", "Db5", "Eb5", "F5", "G5"],
        "Db": ["Db4", "Eb4", "F4", "Gb4", "Ab4", "Bb4", "C5"],
        "Gb": ["Gb4", "Ab4", "Bb4", "Cb5", "Db5", "Eb5", "F5"],
        "Cb": ["Cb4", "Db4", "Eb4", "Fb4", "Gb4", "Ab4", "Bb4"]
    }

    bass_patterns = {
        "C": [
            [("C2", 1, None), ("G2", 1, None), ("C3", 1, None), ("G2", 1, None)],
            [("G2", 1, None), ("D3", 1, None), ("G3", 1, None), ("D3", 1, None)],
            [("A2", 1, None), ("E3", 1, None), ("A3", 1, None), ("E3", 1, None)],
            [("F2", 1, None), ("C3", 1, None), ("F3", 1, None), ("C3", 1, None)]
        ],
        "G": [
            [("G2", 1, None), ("D3", 1, None), ("G3", 1, None), ("D3", 1, None)],
            [("D2", 1, None), ("A2", 1, None), ("D3", 1, None), ("A2", 1, None)],
            [("A2", 1, None), ("E3", 1, None), ("A3", 1, None), ("E3", 1, None)],
            [("C2", 1, None), ("G2", 1, None), ("C3", 1, None), ("G2", 1, None)]
        ],
        "D": [
            [("D2", 1, None), ("A2", 1, None), ("D3", 1, None), ("A2", 1, None)],
            [("A2", 1, None), ("E3", 1, None), ("A3", 1, None), ("E3", 1, None)],
            [("B2", 1, None), ("F#3", 1, None), ("B3", 1, None), ("F#3", 1, None)],
            [("G2", 1, None), ("D3", 1, None), ("G3", 1, None), ("D3", 1, None)]
        ],
        "A": [
            [("A2", 1, None), ("E3", 1, None), ("A3", 1, None), ("E3", 1, None)],
            [("E2", 1, None), ("B2", 1, None), ("E3", 1, None), ("B2", 1, None)],
            [("B2", 1, None), ("F#3", 1, None), ("B3", 1, None), ("F#3", 1, None)],
            [("D2", 1, None), ("A2", 1, None), ("D3", 1, None), ("A2", 1, None)]
        ],
        "E": [
            [("E2", 1, None), ("B2", 1, None), ("E3", 1, None), ("B2", 1, None)],
            [("B2", 1, None), ("F#3", 1, None), ("B3", 1, None), ("F#3", 1, None)],
            [("G#2", 1, None), ("D#3", 1, None), ("G#3", 1, None), ("D#3", 1, None)],
            [("A2", 1, None), ("E3", 1, None), ("A3", 1, None), ("E3", 1, None)]
        ],
        "B": [
            [("B2", 1, None), ("F#3", 1, None), ("B3", 1, None), ("F#3", 1, None)],
            [("F#2", 1, None), ("C#3", 1, None), ("F#3", 1, None), ("C#3", 1, None)],
            [("G#2", 1, None), ("D#3", 1, None), ("G#3", 1, None), ("D#3", 1, None)],
            [("E2", 1, None), ("B2", 1, None), ("E3", 1, None), ("B2", 1, None)]
        ],
        "F#": [
            [("F#2", 1, None), ("C#3", 1, None), ("F#3", 1, None), ("C#3", 1, None)],
            [("C#2", 1, None), ("G#2", 1, None), ("C#3", 1, None), ("G#2", 1, None)],
            [("D#2", 1, None), ("A#2", 1, None), ("D#3", 1, None), ("A#2", 1, None)],
            [("B2", 1, None), ("F#3", 1, None), ("B3", 1, None), ("F#3", 1, None)]
        ],
        "C#": [
            [("C#2", 1, None), ("G#2", 1, None), ("C#3", 1, None), ("G#2", 1, None)],
            [("G#2", 1, None), ("D#3", 1, None), ("G#3", 1, None), ("D#3", 1, None)],
            [("A#2", 1, None), ("F3", 1, None), ("A#3", 1, None), ("F3", 1, None)],
            [("F#2", 1, None), ("C#3", 1, None), ("F#3", 1, None), ("C#3", 1, None)]
        ],
        "F": [
            [("F2", 1, None), ("C3", 1, None), ("F3", 1, None), ("C3", 1, None)],
            [("C2", 1, None), ("G2", 1, None), ("C3", 1, None), ("G2", 1, None)],
            [("D2", 1, None), ("A2", 1, None), ("D3", 1, None), ("A2", 1, None)],
            [("Bb2", 1, None), ("F3", 1, None), ("Bb3", 1, None), ("F3", 1, None)]
        ],
        "Bb": [
            [("Bb2", 1, None), ("F3", 1, None), ("Bb3", 1, None), ("F3", 1, None)],
            [("F2", 1, None), ("C3", 1, None), ("F3", 1, None), ("C3", 1, None)],
            [("G2", 1, None), ("D3", 1, None), ("G3", 1, None), ("D3", 1, None)],
            [("Eb2", 1, None), ("Bb2", 1, None), ("Eb3", 1, None), ("Bb2", 1, None)]
        ],
        "Eb": [
            [("Eb2", 1, None), ("Bb2", 1, None), ("Eb3", 1, None), ("Bb2", 1, None)],
            [("Bb2", 1, None), ("F3", 1, None), ("Bb3", 1, None), ("F3", 1, None)],
            [("C2", 1, None), ("G2", 1, None), ("C3", 1, None), ("G2", 1, None)],
            [("Ab2", 1, None), ("Eb3", 1, None), ("Ab3", 1, None), ("Eb3", 1, None)]
        ],
        "Ab": [
            [("Ab2", 1, None), ("Eb3", 1, None), ("Ab3", 1, None), ("Eb3", 1, None)],
            [("Eb2", 1, None), ("Bb2", 1, None), ("Eb3", 1, None), ("Bb2", 1, None)],
            [("F2", 1, None), ("C3", 1, None), ("F3", 1, None), ("C3", 1, None)],
            [("Db2", 1, None), ("Ab2", 1, None), ("Db3", 1, None), ("Ab2", 1, None)]
        ],
        "Db": [
            [("Db2", 1, None), ("Ab2", 1, None), ("Db3", 1, None), ("Ab2", 1, None)],
            [("Ab2", 1, None), ("Eb3", 1, None), ("Ab3", 1, None), ("Eb3", 1, None)],
            [("Bb2", 1, None), ("F3", 1, None), ("Bb3", 1, None), ("F3", 1, None)],
            [("Gb2", 1, None), ("Db3", 1, None), ("Gb3", 1, None), ("Db3", 1, None)]
        ],
        "Gb": [
            [("Gb2", 1, None), ("Db3", 1, None), ("Gb3", 1, None), ("Db3", 1, None)],
            [("Db2", 1, None), ("Ab2", 1, None), ("Db3", 1, None), ("Ab2", 1, None)],
            [("Eb2", 1, None), ("Bb2", 1, None), ("Eb3", 1, None), ("Bb2", 1, None)],
            [("B2", 1, None), ("F#3", 1, None), ("B3", 1, None), ("F#3", 1, None)]
        ],
        "Cb": [
            [("Cb2", 1, None), ("Gb2", 1, None), ("Cb3", 1, None), ("Gb2", 1, None)],
            [("Gb2", 1, None), ("Db3", 1, None), ("Gb3", 1, None), ("Db3", 1, None)],
            [("Ab2", 1, None), ("Eb3", 1, None), ("Ab3", 1, None), ("Eb3", 1, None)],
            [("E2", 1, None), ("B2", 1, None), ("E3", 1, None), ("B2", 1, None)]
        ]
    }

    while i <= measures:
        scale = scales[selected_key]
        if i < 4 or i > 15:
            treble_notes = [("rest", 4, None)]
        else:
            treble_notes = [(random.choice(scale), 1, None) for _ in range(4)]
            treble_notes = [
                (random.choice([note for note in scale if note != "F4"]), 1, None)
                if i % 4 in {1, 3} and note == "F4" else
                (random.choice([note for note in scale if note != "G4"]), 1, None)
                if i % 4 in {1, 2} and note == "G4" else
                (random.choice([note for note in scale if note != "E4"]), 1, None)
                if i % 4 == 0 and note == "E4" else note
                for note in treble_notes
            ]

        bass_notes = bass_patterns[selected_key][(i - 1) % 4]

        measure = create_measure(bass_notes, i, selected_key)
        left_hand.append(measure)
        measure = create_measure(treble_notes, i, selected_key)
        right_hand.append(measure)
        i += 1
    
    create_ending_measures1(selected_key, i, left_hand, right_hand)

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