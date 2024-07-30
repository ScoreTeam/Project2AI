# Video Distance and Points Calculator API

## Project Structure

- `Distance.py`: Contains the `DistanceProcessor` class, which handles the distance calculations.
- `main.py`: Contains the FastAPI application and the core logic for processing the video and calculating points.

## Usage

1. Start the FastAPI server:

    ```bash
    uvicorn main:app --host 127.0.0.1 --port 8000
    ```

2. Send a POST request to `/process_video` with the path to your video file:

    ```json
    {
      "path": "path/to/your/video.mp4"
    }
    ```

## API Endpoints

### POST /process_video

This endpoint processes the video, extracts frames, calculates distances, and assigns points.

**Request Body:**

- `path` (string): The local path to the video file.

**Response:**

- `endpoint` (string): The endpoint where results can be processed.
- `data` (list): A list of dictionaries containing `employee_id`, `customer_id`, and `points`.

## Classes and Methods

### Individual

Represents an individual in a frame.

- `id` (int): The ID of the individual.
- `type` (str): The type of individual.
- `start_coords` (tuple): The starting coordinates of the individual.
- `gender` (str): The gender of the individual.
- `full_body_height_px` (int): The full body height in pixels.
- `face_height` (int): The face height in pixels.

### Frame

Represents a single frame in the video.

- `individuals` (List[Individual]): A list of individuals in the frame.
- `max_distance_cm` (int): The maximum distance in centimeters.
- `image_height` (int): The height of the image.

### VideoProcessor

Handles video processing.

- `path` (str): The path to the video.
- `get_video_from_path()`: Gets the video data from the path.
- `divide_video_into_frames()`: Divides the video into frames.
- `extract_information_from_frames(images)`: Extracts information from the frames.

### DistanceCalculator

Handles distance calculation.

- `frames` (List[Frame]): A list of frames.
- `num_frames` (int): The number of frames.
- `process_frame(frame, time_delta)`: Processes a single frame.
- `process_data(frame)`: Processes data for a frame.
- `run(time_delta)`: Runs the distance calculation.

### PointCalculator

Handles point calculation.

- `results` (Dict): The results from distance calculation.
- `calculate_points()`: Calculates points from the results.

## Logic of Time Spent Calculations

### Step-by-Step Process

1. **Initialization**:
    - The `DistanceCalculator` is initialized with a list of frames.
    - Data structures to track time spent, minimum valid time reached, and threshold time reached are initialized.

2. **Processing Frames**:
    - For each frame, the `process_frame` method is called with a `time_delta` (time difference between frames).
    - The frame data is processed using the `process_data` method, which utilizes the `DistanceProcessor` to get the distances between individuals.

3. **Tracking Time**:
    - For each pair of individuals (employee and customer) in the results:
        - If the distance is `-1` (indicating no valid measurement), the time spent is reset to `0` if the minimum valid time has not been reached.
        - If the distance is valid, the time spent is incremented by `time_delta`.

4. **Checking Time Thresholds**:
    - The code checks if the time spent for each pair has reached the minimum valid time (`5` seconds) or the threshold time (`60` seconds).
    - Flags (`min_valid_time_reached` and `threshold_time_reached`) are set accordingly.

5. **Calculating Results**:
    - After processing all frames, the results are compiled.
    - For each pair of individuals, the total time spent together and whether the threshold was reached are recorded.

### Example of Time Tracking

```python
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
```

In this example:

- The time spent for each pair of individuals is tracked.
- If the distance is `-1` (indicating no valid measurement), the time is reset unless the minimum valid time has already been reached.
- If the distance is valid, the time spent is incremented.
- The code checks if the time spent has reached the minimum valid time or the threshold time and sets the corresponding flags.

## Example Walkthrough

### Step 1: Input Video Path

**Input:**

```json
{
  "path": "path/to/your/video.mp4"
}
```

### Step 2: Divide Video into Frames

**Output:**

```json
[
  "image_0.jpg",
  "image_1.jpg",
  ...
  "image_9.jpg"
]
```

### Step 3: Extract Information from Frames

**Output:**

```json
[
  {
    "individuals": [
      {
        "id": 0,
        "type": "type",
        "start_coords": [0, 0],
        "gender": "gender",
        "full_body_height_px": 100,
        "face_height": 15,
        "coords": [0, 0]
      }
    ],
    "max_distance_cm": 50,
    "image_height": 1080
  },
  ...
]
```

### Step 4: Calculate Distance

**Output:**

```json
{
  "results": [
    {
      "employee_id": 1,
      "customer_id": 2,
      "total_time": 12.4,
      "threshold_reached": true
    },
    ...
  ]
}
```

### Step 5: Calculate Points

**Output:**

```json
{
  "endpoint": "/process_results",
  "data": [
    {
      "employee_id": 1,
      "customer_id": 2,
      "points": 124
    },
    ...
  ]
}
```
