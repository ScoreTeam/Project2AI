import time
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from Distance import DistanceProcessor

# first we got take the video from a local path
# second we gotta divide it into such a frames and images 
# third we gotta extract the information from each frame(image) and send it to the distance classes 
# forth we got the calculations of the distance from the DistanceProcessor
# at last we should take those results and calculate the points for them
# finally we should wrap everything together into a fast api request 

class Individual:
    def __init__(self, id: int, type: str, start_coords: tuple, gender: str, full_body_height_px: int,face_height :int):
        self.id = id
        self.type = type
        self.start_coords = start_coords
        self.gender = gender
        self.full_body_height_px = full_body_height_px
        self.face_height = face_height
        self.coords = start_coords

class Frame:
    def __init__(self, individuals: List[Individual], max_distance_cm: int, image_height: int):
        self.individuals = individuals
        self.max_distance_cm = max_distance_cm
        self.image_height = image_height

class VideoProcessor:
    def __init__(self, path: str):
        self.path = path
        self.video_data = self.get_video_from_path()

    def get_video_from_path(self):
        return "video_data"

    def divide_video_into_frames(self):
        images = [f"image_{i}.jpg" for i in range(10)]
        return images

    def extract_information_from_frames(self, images: List[str]):
        # extracting information
        frames = [
            Frame(
                individuals=[Individual(id=i, type='type', start_coords=(0, 0), gender='gender', full_body_height_px=100,face_height =15)],
                max_distance_cm=50,
                image_height=1080
            ) for i in range(len(images))
        ]
        return frames

class DistanceCalculator:
    def __init__(self, frames: List[Frame], num_frames=100):
        self.num_frames = num_frames
        self.frames = frames
        self.time_spent = {}
        self.min_valid_time_reached = {}
        self.threshold_time_reached = {}
        self.min_valid_time = 5
        self.threshold_time = 60

    def process_frame(self, frame: Frame, time_delta):
        response = self.process_data(frame)
        results = response["results"]
        for pair in results:
            employee_id, customer_id, distance = pair
            pair_key = (employee_id, customer_id)
            if pair_key not in self.time_spent:
                self.time_spent[pair_key] = 0
                self.min_valid_time_reached[pair_key] = False
                self.threshold_time_reached[pair_key] = False

            if distance == -1:
                if not self.min_valid_time_reached[pair_key]:
                    # reset time if distance is -1 and minimum valid time not reached
                    self.time_spent[pair_key] = 0
            else:
                self.time_spent[pair_key] += time_delta

                # check if the minimum valid time has been reached
                if self.time_spent[pair_key] >= self.min_valid_time:
                    self.min_valid_time_reached[pair_key] = True
                if self.time_spent[pair_key] >= self.threshold_time:
                    self.threshold_time_reached[pair_key] = True

    def process_data(self, frame: Frame):
        processor = DistanceProcessor(
            individuals=frame.individuals,
            max_distance_cm=frame.max_distance_cm,
            image_height=frame.image_height
        )
        results = processor.process()
        return {"results": results}

    def run(self, time_delta=0.2):
        for frame in self.frames:
            self.process_frame(frame, time_delta)

        results = {
            "results": []
        }

        for pair, total_time in self.time_spent.items():
            employee_id, customer_id = pair
            threshold_reached = self.threshold_time_reached[pair]
            results["results"].append({
                "employee_id": employee_id,
                "customer_id": customer_id,
                "total_time": round(total_time, 3),
                "threshold_reached": threshold_reached
            })

        return results

class PointCalculator:
    def __init__(self, results: Dict[str, Any]):
        self.results = results

    def calculate_points(self):
        print("Calculating points from results")
        # calculating points
        points = [{"employee_id": result["employee_id"], "customer_id": result["customer_id"], "points": result["total_time"] * 10} for result in self.results["results"]]
        return points

# FastAPI 
app = FastAPI()

class VideoPath(BaseModel):
    path: str

@app.post("/process_video")
async def process_video(video_path: VideoPath):
    try:
        # Step 1: initialize VideoProcessor
        video_processor = VideoProcessor(video_path.path)

        # Step 2: divide video into frames and extract information from frames
        images = video_processor.divide_video_into_frames()
        frames = video_processor.extract_information_from_frames(images)

        # Step 3: calculate distance
        distance_calculator = DistanceCalculator(frames)
        simulation_results = distance_calculator.run()

        # Step 4: calculate points 
        point_calculator = PointCalculator(simulation_results)
        points = point_calculator.calculate_points()

        # Step 5: wrap everything into a FastAPI request
        return {"endpoint": "/process_results", "data": points}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
