import cv2
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from objectdetection import ObjectDetection  
from FaceRec2 import NFRscript as fr
from Distance.CallDistance2 import DistanceCalculator, Frame, Individual
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Score:
    def __init__(self):
        self.od = ObjectDetection()
        self.dis = DistanceCalculator()

    def VideoToFrames(self, videopath, FPS, Outputpath):
        cap = cv2.VideoCapture(videopath)
        frame_folder = Outputpath  
        os.makedirs(frame_folder, exist_ok=True)
        count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            if count % (cap.get(cv2.CAP_PROP_FPS) // FPS) == 0:
                cv2.imwrite(os.path.join(frame_folder, f'frame_{count}.jpg'), frame)
            count += 1
        cap.release()

    def FaceRec(self, frame, box_coordinate):
        labeledboxes = fr.DetectFace(frame, box_coordinate)
        return labeledboxes

    def fhamza(self, data, heights) -> Frame:
        individuals = []
        for idx, item in enumerate(data):
            individual_info = {
                "id": int(item[2][1]),
                "type": item[2][0],
                "start_coords": [float(item[1][0]), float(item[1][1])],
                "gender": "male" if item[2][1] == '2' else 'male',
                "full_body_height_px": int(item[1][3]),
                "face_height_px": int(heights[idx]),
            }

            individual = Individual(
                id=individual_info["id"],
                type=individual_info["type"],
                start_coords=tuple(individual_info["start_coords"]),
                gender=individual_info["gender"],
                full_body_height_px=individual_info["full_body_height_px"],
                face_height=individual_info["face_height_px"],
            )

            individuals.append(individual)

        frame_info = Frame(
            individuals=individuals,
            max_distance_cm=50,
            image_height=408
        )

        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        print(f"Frame max distance: {frame_info.max_distance_cm} cm, Image height: {frame_info.image_height} px")
        print("Individuals info:")
        for individual in frame_info.individuals:
            print(f"  ID: {individual.id}, Type: {individual.type}, Start Coords: {individual.start_coords}, "
                  f"Gender: {individual.gender}, Full Body Height: {individual.full_body_height_px}px, "
                  f"Face Height: {individual.face_height_px}px, Coords: {individual.coords}")
        print("xxxxxxxxxxxxxxxxxxxxxxxxxxxxx")

        return frame_info

    def ProcessFrame(self, image_path, FPS):
        if not isinstance(image_path, str):
            raise ValueError("Image path must be a string.")

        image_path = r"{}".format(image_path)

        if not os.path.exists(image_path):
            raise ValueError(f"Image file does not exist at path: {image_path}")
        
        print("New image path :",image_path)
        image=image_path
        # image="Customer_200.jpg"
        timeupdate = 1 / FPS
        box_coordinate = self.od.DetectImage(image)
        labeled_boxes, heights = self.FaceRec(image, box_coordinate)
        labeled_boxes_json = self.fhamza(labeled_boxes, heights)
        Updatedframe = self.dis.process_frame(labeled_boxes_json, timeupdate)
        
        return Updatedframe

score = Score()

class ProcessFrameRequest(BaseModel):
    image_path: str
    FPS: int

@app.post("/process-frame/")
async def process_frame(request: ProcessFrameRequest):
    try:
        updated_frame = score.ProcessFrame(request.image_path, request.FPS)
        return {"status": "success", "updated_frame": updated_frame}  
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
