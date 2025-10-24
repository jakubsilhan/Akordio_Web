import torch, os
from app.Akordio_Core.net_config import Config
from app.Akordio_Core.chords import Chords, Complexity


class PostProcess:
    def __init__(self, config: Config):
        self.config = config

    def create_annotation(self, preds: list):
        """
        Edits predictions into a usable annotation
        """
        
        # Initialization
        chords_decoder = Chords()
        match self.config.train.model_complexity:
            case 'complex':
                complexity = Complexity.COMPLEX
            case 'majmin7':
                complexity = Complexity.MAJMIN7
            case _:
                complexity = Complexity.MAJMIN
        #TODO rework using chords from core and list comprehension
        chords = [chords_decoder.decode(pred, complexity) for pred in preds]

        # Generate annotation
        annotations = self._generate_intervals(chords)

        return annotations


    def _generate_intervals(self, chords: list) -> list[tuple[float, float, str]]:
        """
        Generates timed intervals from predictions
        """
        start = 0
        frame_duration = self.config.data.preprocess.hop_length/self.config.data.preprocess.sampling_rate
        annotations = list()
        for i in range(len(chords)):
            if i == 0:
                prev_chord = chords[i]
                continue

            if chords[i] != prev_chord:
                start_time = start * frame_duration
                end_time = i * frame_duration
                annotations.append((start_time, end_time, prev_chord))
                prev_chord = chords[i]
                start = i
            
        # Last chord
        annotations.append((
            start * frame_duration,
            len(chords) * frame_duration,
            prev_chord
        ))
        
        return annotations
