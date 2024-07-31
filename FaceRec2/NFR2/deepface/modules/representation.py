from typing import Any, Dict, List, Union
import os,sys
import numpy as np
from tf_keras.models import load_model
# current_dir = os.path.dirname(os.path.abspath(__file__))
# commons_path = os.path.join(current_dir, 'commons')
# sys.path.append(commons_path)
# print("\nHi path:",current_dir,"\n",commons_path,"\n bi\n")
from deepface.commons import image_utils
from deepface.modules import detection, preprocessing
from deepface.models.FacialRecognition import FacialRecognition


def represent(
    img_path: Union[str, np.ndarray],
    model_name: str = "VGG-Face",
    enforce_detection: bool = True,
    detector_backend: str = "opencv",
    align: bool = True,
    expand_percentage: int = 0,
    normalization: str = "base", # normalization (string): Normalize the input image before feeding it to the model
    anti_spoofing: bool = False,
) -> List[Dict[str, Any]]:
    # Represent facial images as multi-dimensional vector embeddings.
    resp_objs = []
    # 
    # model: FacialRecognition = modeling.build_model(model_name)
    # 
    project_path = os.getcwd()
    # model :FacialRecognition =load_model("D://NFR2/NFRmodel.h5")
    model = FacialRecognition("D://NFR2/NAFF.h5")
    # ---------------------------------
    # we have run pre-process in verification. so, this can be skipped if it is coming from verify.
    target_size = model.input_shape
    # in here there seems a delay
    
    # handling the extraction of faces from the image
    if detector_backend != "skip":
        img_objs = detection.extract_faces(
            img_path=img_path,
            detector_backend=detector_backend,
            grayscale=False,
            enforce_detection=enforce_detection,
            align=align,
            expand_percentage=expand_percentage,
            anti_spoofing=anti_spoofing,
        )
    else:  # skip
        # Try load. If load error, will raise exception internal
        img, _ = image_utils.load_image(img_path)

        if len(img.shape) != 3:
            raise ValueError(f"Input img must be 3 dimensional but it is {img.shape}")

        # make dummy region and confidence to keep compatibility with `extract_faces`
        img_objs = [
            {
                "face": img,
                "facial_area": {"x": 0, "y": 0, "w": img.shape[0], "h": img.shape[1]},
                "confidence": 0,
            }
        ]
    # ---------------------------------

    for img_obj in img_objs:
        if anti_spoofing is True and img_obj.get("is_real", True) is False:
            raise ValueError("Spoof detected in the given image.")
        img = img_obj["face"]

        # rgb to bgr
        img = img[:, :, ::-1]

        region = img_obj["facial_area"]
        confidence = img_obj["confidence"]

        # resize to expected shape of ml model
        img = preprocessing.resize_image(
            img=img,
            # thanks to DeepId (!)
            target_size=(target_size[1], target_size[0]),
        )

        # custom normalization
        img = preprocessing.normalize_input(img=img, normalization=normalization)

        embedding = model.forward(img)

        resp_obj = {}
        resp_obj["embedding"] = embedding
        resp_obj["facial_area"] = region
        resp_obj["face_confidence"] = confidence
        resp_objs.append(resp_obj)

    return resp_objs
