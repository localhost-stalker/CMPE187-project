TESTS = [
    {
        "id": "T1",
        "name": "Dialect/Accent Recognition",
        "audio": "dialect_recording.wav",
        "prompt": (
            "Transcribe the speech and identify the speaker's accent or dialect. "
            "Return exactly in this format: "
            "'Transcript: <transcription> | Accent: <accent or dialect>'."
        ),
        "expected": "Correct transcription and Mandarin-influenced English accent",
        "expected_transcripts": [
            "Hello, my name is Lily and I like the color blue.",
            "Hello, my name is Lily and my favorite color is blue.",
        ],
        "grader": "dialect",
    },
    {
        "id": "T2",
        "name": "Compressed Speech Recognition",
        "audio": "compressed_audio.wav",
        "prompt": (
            "Transcribe the speech in this compressed audio as accurately as possible. "
            "Recover the intended spoken text despite compression or audio degradation. "
            "Return only the reconstructed transcript."
        ),
        "expected": (
            "This is a test for our AI chatbot test project, and I will be compressing this "
            "audio file. Here are a few keywords, I guess: elephant, cucumber, entrepreneur, soda."
        ),
        "grader": "transcript",
    },
    {
        "id": "T3",
        "name": "Animal Sound Recognition",
        "audio": "animal_sound.wav",
        "prompt": (
            "Identify the animal species based on the sound in this audio. "
            "Return only the species or animal name."
        ),
        "expected": "Canary",
        "grader": "animal",
    },
    {
        "id": "T4",
        "name": "Instrument Recognition",
        "audio": "instrument_audio.wav",
        "prompt": (
            "Identify the musical instruments clearly audible in this recording. "
            "Return only the instrument names, separated by commas."
        ),
        "expected": "Violin and harp",
        "expected_instruments": ["violin", "harp"],
        "grader": "instruments",
    },
    {
        "id": "T5",
        "name": "Emotional Tone Recognition",
        "audio": "monologue.wav",
        "prompt": (
            "Identify the primary and secondary emotional tones expressed by the speaker "
            "based only on their voice and delivery. "
            "Return exactly in this format: "
            "'Primary: <emotion> | Secondary: <emotion>'."
        ),
        "expected": "Anxiety/tension primary; admiration/awe secondary",
        "grader": "emotion",
    },
    {
        "id": "T6",
        "name": "Musical Pitch Recognition",
        "audio": "car_horn.wav",
        "prompt": (
            "Identify the closest musical note and octave of the dominant pitch in this audio. "
            "Return only the note and octave, for example: B5."
        ),
        "expected": "B5",
        "grader": "pitch",
    },
    {
        "id": "T7",
        "name": "Speech Disfluency and Correction",
        "audio": "speech.wav",
        "prompt": (
            "Identify any repetitions, stutters, prolongations, false starts, or other speech "
            "disfluencies, then reconstruct the intended sentence. "
            "Return exactly in this format: "
            "'Mistakes: <identified disfluencies> | Corrected text: <clean transcript>'."
        ),
        "expected": (
            "I want to go outside. I can see the dog. I didn't know that. And then we went out. "
            "I saw my friend yesterday. That was really fun."
        ),
        "grader": "disfluency",
    },
    {
        "id": "T8",
        "name": "Music Genre Recognition",
        "audio": "music_genre.wav",
        "prompt": (
            "Identify the primary music genre of this audio. "
            "Return only the genre name."
        ),
        "expected": "Jazz",
        "grader": "genre",
    },
]
