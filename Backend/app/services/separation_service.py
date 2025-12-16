from demucs import pretrained
from demucs.apply import apply_model

import io
import soundfile as sf
import numpy as np
import librosa
import torch

from typing import Dict, BinaryIO

from . import MAX_DURATION

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
        # Loading audio
        y, sr = librosa.load(audio, sr=None, mono=False)
        # waveform, sr = torchaudio.load(audio)
        duration = librosa.get_duration(y=y, sr=sr)

        if duration > MAX_DURATION:
            raise ValueError(f"Audio too long! (max {MAX_DURATION//60} minutes)")
        
        # Convert to demucs format (tensor)
        waveform = torch.from_numpy(y).float()

        # Convert to correct shape if needed
        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0) 
        elif waveform.shape[0] != 1 and waveform.shape[0] != 2:
            waveform = waveform.T

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
        mix_np = mix.cpu().numpy().T 

        # Write to mp3 file
        sf.write(
            file=audio_buffer, 
            data=mix_np, 
            samplerate=sr, 
            format="mp3"
        )
        audio_buffer.seek(0)

        return audio_buffer        
        