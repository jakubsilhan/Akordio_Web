import torch
from app.core.net_config import Config

PITCH_CLASS = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
MAJMIN = ["maj", "min"]
MAJMIN7 = ["maj", "min", "maj7", "min7", "7"]
COMPLEX = ["maj", "min", "maj7", "min7", "7", "dim", "aug", "min6", "maj6", "minmaj7", "dim7", "hdim7", "sus2", "sus4"]

class Decode:
    def __init__(self, config: Config):
        self.config = config
        self.majmin_encodings = self._generate_encodings(PITCH_CLASS, MAJMIN)
        self.majmin7_encodings = self._generate_encodings(PITCH_CLASS, MAJMIN7)
        self.complex_encodings = self._generate_encodings(PITCH_CLASS, COMPLEX)

    def _generate_encodings(self, pitch_classes: list, qualities: list) -> list:
        """
        Generates encodings for different chord types
        """
        chords = []
        chords.append("N")
        for pitch in pitch_classes:
            for quality in qualities:
                chords.append(f"{pitch}:{quality}")
        return chords

    def decode(self, preds: list) -> list[str]:
        """
        Decodes a list of predicted ints into chords
        """
        chords = list()
        match self.config.train.model_complexity:
            case "complex":
                encodings = self.complex_encodings
            case "majmin7":
                encodings = self.majmin7_encodings
            case default:
                encodings = self.majmin_encodings
        
        for pred in preds:
            try:
                chords.append(encodings[pred])
            except IndexError:
                chords.append("N")

        return chords
    
    def decode_single(self, pred) -> str:
        match self.config.train.model_complexity:
            case "complex":
                encodings = self.complex_encodings
            case "majmin7":
                encodings = self.majmin7_encodings
            case default:
                encodings = self.majmin_encodings
        
        try:
            chord = encodings[pred]
        except IndexError:
            chord = ("N")

        return chord