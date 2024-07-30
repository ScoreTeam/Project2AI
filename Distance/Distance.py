import json
import math
from itertools import combinations
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from typing import List, Tuple, Optional

AVG_MALE_HEIGHT_CM = 175
AVG_FEMALE_HEIGHT_CM = 162
DEFAULT_FACE_HEIGHT_CM = 24

class FrameInfo(BaseModel):
    id: str
    type: str  # employee or customer
    coords: Tuple[int, int]
    gender: str  # male or female
    full_body_height_px: Optional[int] = None
    face_height_px: Optional[int] = None
    

class DistanceCalculatorMethods:
    @staticmethod
    def euclidean_distance(coord1, coord2):
        value=math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)
        print("value:",value)
        return math.sqrt((coord1[0] - coord2[0]) ** 2 + (coord1[1] - coord2[1]) ** 2)

    @staticmethod
    def manhattan_distance(coord1, coord2):
        return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

    @staticmethod
    def cosine_similarity(coord1, coord2):
        dot_product = coord1[0] * coord2[0] + coord1[1] * coord2[1]
        magnitude1 = math.sqrt(coord1[0] ** 2 + coord1[1] ** 2)
        magnitude2 = math.sqrt(coord2[0] ** 2 + coord2[1] ** 2)
        return dot_product / (magnitude1 * magnitude2)

# Pixel to Cm Converter
class PixelToCmConverter:
    def __init__(self, image_height):
        self.image_height = image_height

    def calculate_ratio(self, FrameInfo):
        
        if FrameInfo.face_height_px:
            pixel_ratio = DEFAULT_FACE_HEIGHT_CM / FrameInfo.face_height_px
        elif FrameInfo.full_body_height_px:
            avg_height_cm = AVG_MALE_HEIGHT_CM if FrameInfo.gender == 'male' else AVG_FEMALE_HEIGHT_CM
            pixel_ratio = avg_height_cm / FrameInfo.full_body_height_px
        else:
            raise ValueError("there are no height or face height information")

        # dynamic adjustment based on Y-coordinate
        # its like a simple camera calibration 
        '''
        y_coordinate = FrameInfo.coords[1]
        adjustment_factor = 1 + (self.image_height - y_coordinate) / self.image_height
        pixel_ratio *= adjustment_factor
        '''

        return pixel_ratio

    @staticmethod
    def pixel_to_real_distance(pixel_distance, pixel_to_cm_ratio):
        return pixel_distance * pixel_to_cm_ratio


class DistanceProcessor:
    def __init__(self, FrameInfos, max_distance_cm, image_height, distance_metric = 'euclidean'):
        self.FrameInfos =  FrameInfos
        self.max_distance_cm = max_distance_cm
        self.image_height = image_height
        self.distance_metric = "euclidean"
        self.converter = PixelToCmConverter(image_height)

    def process(self):
        results = []
        # print("test3")
        #the distance function based on the metric
        if self.distance_metric == 'euclidean':
            # print("euclidean")
            distance_func = DistanceCalculatorMethods.euclidean_distance
            # print(distance_func)
        elif self.distance_metric == 'manhattan':
            distance_func = DistanceCalculatorMethods.manhattan_distance
        elif self.distance_metric == 'cosine': # not recommended 
            distance_func = DistanceCalculatorMethods.cosine_similarity
        else:
            raise ValueError("Invalid distance metric provided")

        # get all combinations of FrameInfos
        pairs = list(combinations(self.FrameInfos, 2))
        # print(pairs)

        def process_pair(pair): # it will be changed based on the input 
            person1, person2 = pair
            coord1, coord2 = person1.coords, person2.coords
            id1, id2 = person1.id, person2.id
            type1, type2 = person1.type, person2.type
            
            if type1 == type2:
                return None
            
            try:
                # calculate pixel-to-cm ratios
                ratio1 = self.converter.calculate_ratio(person1)
                ratio2 = self.converter.calculate_ratio(person2)
                pixel_to_cm_ratio = (ratio1 + ratio2) / 2

                # calculate distances
                pixel_distance = distance_func(coord1, coord2)
                real_distance = self.converter.pixel_to_real_distance(pixel_distance, pixel_to_cm_ratio)

                # check if pair is within max distance and involves customer and employee
                if real_distance <= self.max_distance_cm:
                    
                    return (id1 if type1 == 'employee' else id2,
                                id2 if type2 == 'customer' else id1,
                                real_distance) # could be true
                else:
                    return (id1 if type1 == 'employee' else id2,
                            id2 if type2 == 'customer' else id1,
                            -1) # could be false 
            except ValueError as e:
                print(f"skipping pair {id1}-{id2}: {e}")
                return (id1 if type1 == 'employee' else id2,
                        id2 if type2 == 'customer' else id1,
                        -1)

        with ThreadPoolExecutor() as executor: # using threads for faster process 
            
            results = list(executor.map(process_pair, pairs))
            
            
        results = [result for result in results if result is not None]
        return results