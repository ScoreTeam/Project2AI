#-----------------------------------------------------------------------
# from fastapi import FastAPI
# geeksforgeeks is the best
# app = FastAPI()

# # Define a route at the root web address ("/")
# @app.get("/")
# def read_root():
#     return {"message": "Hello, FastAPI!"}
#-----------------------------------------------------------------------

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from NFR2 import NFR 
import uvicorn,logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class ImagePath(BaseModel):
    path: str

@app.post("/CheckFace/")
async def CheckFace(image: ImagePath):
    logger.info(f"Received request with image path: {image.path}")
    try:
        print(image.path)
        name, xmin, ymin, w, h, xmax, ymax, dis = NFR.FindFaceFromImage(image.path)
        result = {
            "name": name,
            "xmin": int(xmin),
            "ymin": int(ymin),
            "width": int(w),
            "height": int(h),
            "xmax": int(xmax),
            "ymax": int(ymax),
            "distance": float(dis)
        }
        logger.info(f"Processing result: {result}")
        return JSONResponse(content={"Employee Info ": result})
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing image: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
