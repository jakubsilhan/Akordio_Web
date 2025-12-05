import io, torch, librosa, os
import numpy as np

from typing import Dict, Tuple
from torch.utils.data import DataLoader

from app.Akordio_Core.Classes.NetConfig import Config, load_config 
from app.Akordio_Core.Tools.Preprocessor import Preprocessor
from app.Akordio_Core.Tools.Chords import Chords, Complexity
from app.Akordio_Core.Models.online.Model import Model

class Online_Service:
    def __init__(self):
        # Device agnostic code
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Loading models
        self.models: Dict[str, Tuple[Model, Config, Dict]] = {
            "majmin": self._load_model(os.path.join("app","Akordio_Core", "Models", "online", "majmin")),
            "majmin7": self._load_model(os.path.join("app", "Akordio_Core", "Models", "online", "majmin7")),
            "complex": self._load_model(os.path.join("app", "Akordio_Core", "Models", "online", "complex"))
        }

        self.normalization = {
            'mean': 0,
            'std': 0,
        }

    def _load_model(self, path) -> Tuple[Model, Config, Dict]:
        """
        Returns a model and its configuration
        """
        # Load config
        config = load_config(os.path.join(path, "config.yaml"))
        # Load model
        model = Model(config, self.device).to(self.device)
        model_path = os.path.join(path, "best_model.pt")
        loaded = torch.load(model_path, map_location=self.device)
        model.load_state_dict(loaded['model'])
        normalization = loaded['normalization'] 

        return (model, config, normalization)

    def run_inference(self, audio, model_choice) -> str:
        """
        Runs the inference
        """
        # Initializations
        if model_choice not in self.models:
            raise ValueError(f"Unknown model: {model_choice}")
        model, config, normalization = self.models[model_choice]
        chords_decoder = Chords()
        match(model_choice):
            case 'complex':
                complexity = Complexity.COMPLEX
            case 'majmin7':
                complexity = Complexity.MAJMIN7
            case _:
                complexity = Complexity.MAJMIN

        # Preprocessing
        preprocessor = Preprocessor(config)
        tensors = preprocessor.process_audio(audio)

        predictions = []
        for tensor in tensors:
            # Reshaping for the model
            x_tensor = tensor.unsqueeze(0).to(self.device) # [1, num_frames, num_features]

            # Normalization
            x_tensor = (x_tensor-normalization['mean'])/normalization['std']

            # Predictions
            x_tensor = x_tensor.to(torch.float32)
            preds = torch.softmax(model(x_tensor), dim=2).argmax(dim=2)
            preds = preds.view(-1).tolist()
            predictions.extend(preds)

        counts = np.bincount(predictions, minlength=config.train.model.output)

        # Penalization of No chord
        # NO_CHORD_IDX = 0 # index of N
        # counts[NO_CHORD_IDX] = int(counts[NO_CHORD_IDX] * 0.05)  # reduce its vote weight

        majority_chord = int(counts.argmax())
        chord = chords_decoder.decode(majority_chord, complexity)
        print(chord)

        # Return
        return chord