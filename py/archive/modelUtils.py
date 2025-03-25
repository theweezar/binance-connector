import os
from keras.src.models.sequential import Sequential
from keras.src.saving import load_model
from util import get_export_dir


def save_model(model: Sequential, model_name: str):
    export_path = os.path.join(get_export_dir(), model_name)
    model.save(export_path)


def load_local_model(model_name: str) -> Sequential:
    export_path = os.path.join(get_export_dir(), model_name)
    print(export_path)
    loaded_model = load_model(export_path)
    return loaded_model
