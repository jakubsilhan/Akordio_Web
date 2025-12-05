from demucs import pretrained
from demucs.apply import apply_model

import io
import torchaudio
import torch

from typing import Dict, BinaryIO

class Separation_Service:
    def __init__(self):
        # Loading model
        self.model = pretrained.get_model('htdemucs_6s')

        # Separations
        self.separations: Dict[str, list[str]] = {
            "guitar" : ["guitar"],
            "vocals" : ["vocals"],
            "both" : ["guitar", "vocals"]
        }

    def run_separation(self, audio: BinaryIO, separation_choice: str) -> BinaryIO:
        """
        Runs the separation
        """
        # Converting to demucs format (torch.Tensor)
        waveform, sr = torchaudio.load(audio)

        # Separation
        sources = apply_model(self.model, waveform.unsqueeze(0), split=True, device="cpu")[0] # unsqueeze and [0] - create and remove dummy batch dimension for demucs

        # Stem preparation
        stems = {name: sources[i] for i, name in enumerate(self.model.sources)}
        to_remove = self.separations[separation_choice]

        # Full mix
        mix = torch.tensor(sum(stems.values()))

        # Removing unwanted stems
        for name in to_remove:
            mix -= stems[name]

        # Tensor -> BinaryIO
        audio_buffer = io.BytesIO()
        torchaudio.save(uri=audio_buffer, src=mix, sample_rate=sr, format="mp3") # type: ignore
        audio_buffer.seek(0)

        return audio_buffer        
        