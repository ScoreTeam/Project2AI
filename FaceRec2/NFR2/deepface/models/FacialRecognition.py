from abc import ABC
from typing import Any, Union, List, Tuple
import numpy as np
from deepface.commons import package_utils
from tf_keras.models import (Model,load_model)

# Notice that all facial recognition models must be inherited from this class

# pylint: disable=too-few-public-methods
class FacialRecognition(ABC):
    model: Union[Model, Any]
    model_name: str
    input_shape: Tuple[int, int]
    output_shape: int
    def __init__(self, model_path: str):
        self.model = load_model(model_path, compile=False)  # Load model from path

        # Example of setting input and output shapes based on your model
        self.input_shape = (112, 112)  # Example input shape, adjust as per your model
        self.output_shape = 512  # Example output shape, adjust as per your model


    # def forward(self, img: np.ndarray) -> List[float]:
    #     if not isinstance(self.model, Model):
    #         raise ValueError(
    #             "You must overwrite forward method if it is not a keras model,"
    #             f"but {self.model_name} not overwritten!"
    #         )
    #     # model.predict causes memory issue when it is called in a for loop
    #     # embedding = model.predict(img, verbose=0)[0].tolist()
    #     return self.model(img, training=False).numpy()[0].tolist()
    def forward(self, img: np.ndarray) -> List[float]:
        # Assuming your loaded model is a Keras model
        if not isinstance(self.model, Model):
            raise ValueError("The loaded model is not of type keras.models.Model")

        # Assuming preprocessing steps are done elsewhere (e.g., resizing, normalization)
        # model.predict causes memory issue when it is called in a for loop
        # embedding = self.model.predict(img, verbose=0)[0].tolist()
        return self.model(img, training=False).numpy()[0].tolist()

"""
what is the abc in python class? (from chat for knowledge)
The ABC class itself is a built-in class provided by Python's abc module.
It serves as a base class for defining abstract base classes.
By inheriting from ABC, a class signifies that it is intended to 
be an abstract base class.
"""