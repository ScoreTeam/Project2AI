import time
import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
from Distance.Distance import DistanceProcessor

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
        self.face_height_px = face_height
        self.coords = start_coords

class Frame:
    def __init__(self, individuals: List[Individual], max_distance_cm: int, image_height: int):
        self.individuals = individuals
        self.max_distance_cm = max_distance_cm
        self.image_height = image_height

# class VideoProcessor:
#     def __init__(self, path: str):
#         self.path = path
#         self.video_data = self.get_video_from_path()


#     def extract_information_from_frames(self, images: List[str]):
#         # extracting information
#         frames = [
#             Frame(
#                 individuals=[Individual(id=i, type='type', start_coords=(0, 0), gender='gender', full_body_height_px=100,face_height =15)],
#                 max_distance_cm=50,
#                 image_height=1080
#             ) for i in range(len(images))
#         ]
#         return frames

class DistanceCalculator:
    def __init__(self,):
        # self.num_frames = num_frames
        # self.frames = frames
        self.time_spent = {}
        self.min_valid_time_reached = {}
        self.threshold_time_reached = {}
        self.min_valid_time = 0
        self.threshold_time = 0

    def process_frame(self, frame: Frame, time_delta):
        response = self.process_data(frame)
        results = response["results"]
        print("results:",results)
        for pair in results:
            employee_id, customer_id, distance = pair
            pair_key = (employee_id, customer_id)
            print("pairkey:",pair_key)
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
            return results

    def process_data(self, frame: Frame):
        # print("frameinfo:",frame.individuals,)
        # print("frameinfo:")
        # for individual in frame.individuals:
        #     print(f"Individual ID: {individual.id}, Type: {individual.type}, Start Coords: {individual.start_coords}, "
        #           f"Gender: {individual.gender}, Full Body Height: {individual.full_body_height_px}px, "
        #           f"Face Height: {individual.face_height_px}px, Coords: {individual.coords}")
        processor = DistanceProcessor(
            FrameInfos=frame.individuals,
            max_distance_cm=frame.max_distance_cm,
            image_height=frame.image_height
        )
        
        results = processor.process()
        print("test2")
        print(results)
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
        print("test1")
        print(results)
        return results

