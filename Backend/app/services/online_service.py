import io, torch, librosa, os
import numpy as np

from typing import Dict, Tuple
from torch.utils.data import DataLoader

from app.core.net_config import Config, load_config 
from app.core.song_dataset import SongDataset, make_collate_fn
from app.tools.preprocessor import Preprocess
from app.tools.decoder import Decode
from app.neural_nets.online.Model import Model

class Online_Service:
    def __init__(self):
        # Device agnostic code
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Loading models
        self.models: Dict[str, Tuple[Model, Config]] = {
            "majmin": self._load_model(os.path.join("app", "neural_nets", "online", "majmin")),
            "majmin7": self._load_model(os.path.join("app", "neural_nets", "online", "majmin7")),
            "complex": self._load_model(os.path.join("app", "neural_nets", "online", "complex"))
        }

    def _load_model(self, path) -> Tuple[Model, Config]:
        """
        Returns a model and its configuration
        """
        # Load config
        config = load_config(os.path.join(path, "config.yaml"))
        # Load model
        model = Model(config, self.device).to(self.device)
        model_path = os.path.join(path, "final_model.pt")
        loaded = torch.load(model_path, map_location=self.device)
        model.load_state_dict(loaded['model'])

        return (model, config)
    
    def _compute_mean_std(self, tensors: list[torch.Tensor]) -> tuple[float, float]:
        """
        Calculate mean and std:
        """
        mean = 0.0
        square_mean = 0.0
        num_batches = 0

        # Aggregations across the whole song
        for tensor in tensors:
            tensor = tensor.unsqueeze(0) # [1, num_frames, num_features]
            mean += torch.mean(tensor).item()
            square_mean += torch.mean(tensor.pow(2)).item()
            num_batches += 1

        # Calculating characteristics
        mean /= num_batches
        square_mean /= num_batches
        std = np.sqrt(square_mean - mean * mean)

        return mean, std


    def run_inference(self, audio, model_choice) -> str:
        """
        Runs the inference
        """
        # Initializations
        if model_choice not in self.models:
            raise ValueError(f"Unknown model: {model_choice}")
        model, config = self.models[model_choice]
        decoder = Decode(config)

        # Preprocessing
        preprocessor = Preprocess(config)
        tensors = preprocessor.process_audio(audio)

        mean, std = self._compute_mean_std(tensors)

        predictions = []
        for tensor in tensors:
            # Reshaping for the model
            x_tensor = tensor.unsqueeze(0).to(self.device) # [1, num_frames, num_features]

            # Normalization
            x_tensor = (x_tensor-mean)/std

            # Predictions
            preds = torch.softmax(model(x_tensor), dim=2).argmax(dim=2)
            preds = preds.view(-1).tolist()
            predictions.extend(preds)

        counts = np.bincount(predictions, minlength=config.train.model.output)

        # Penalization of "N"
        # NO_CHORD_IDX = 0 # index of N
        # counts[NO_CHORD_IDX] = int(counts[NO_CHORD_IDX] * 0.05)  # reduce its vote weight

        majority_chord = counts.argmax()
        chord = decoder.decode_single(majority_chord)

        # Return
        return chord