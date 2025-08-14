import io, librosa, torch
from app.core.net_config import Config
import numpy as np

class Preprocess():
    def __init__(self, config: Config):
        self.config = config

    def process_audio(self, audio: bytes) -> list[torch.Tensor]:
        """
        Processes audio into features according to the config
        """
        
        # Load audio
        audio_buffer = io.BytesIO(audio)
        x, sr = librosa.load(audio_buffer, sr=self.config.data.preprocess.sampling_rate)

        # Extract features
        features = self._extract_features(x)

        # Split into fragments
        fragment_size = self.config.data.preprocess.fragment_size
        fragments = []

        # Return with no fragmenting
        if fragment_size == 0:
            fragments.append(torch.tensor(features, dtype=torch.float32))
            return fragments
        
        # Fragment
        for start in range(0, len(features), fragment_size):
            fragment = features[start:start+fragment_size]
            fragments.append(torch.tensor(fragment, dtype=torch.float32))
        
        return fragments

    def _extract_features(self, x) -> np.ndarray:
        """
        Extracts features from audio
        """
        if self.config.data.preprocess.pcp.enabled:
            features = librosa.feature.chroma_cqt(y=x, sr=self.config.data.preprocess.sampling_rate, bins_per_octave=self.config.data.preprocess.bins_per_octave, hop_length=self.config.data.preprocess.hop_length, n_chroma=self.config.data.preprocess.pcp.bins, n_octaves=self.config.data.preprocess.pcp.octaves)
        else:
            features = np.abs(librosa.cqt(x, sr=self.config.data.preprocess.sampling_rate, bins_per_octave=self.config.data.preprocess.bins_per_octave,n_bins=self.config.data.preprocess.cqt_bins, hop_length=self.config.data.preprocess.hop_length))
            features = librosa.amplitude_to_db(features, ref=np.max)

        features = features.T
        # times = librosa.frames_to_time(np.arange(features.shape[0]), sr=self.config.data.preprocess.sampling_rate, hop_length=self.config.data.preprocess.hop_length)

        return features