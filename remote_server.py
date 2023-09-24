import os
import io
import cv2
import numpy as np
from PIL import Image
from argparse import ArgumentParser


from fastapi import FastAPI, WebSocket, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.websockets import WebSocketDisconnect
from demo_utils import FaceAnimationClass

parser = ArgumentParser()
parser.add_argument("--source_image", default="./assets/source.jpg", help="path to source image")
parser.add_argument("--restore_face", default=False, action="store_true", help="restore face from the result")
args = parser.parse_args()

faceanimation = FaceAnimationClass(source_image_path=args.source_image, use_sr=args.restore_face)
# remote server fps is lower than local camera fps, so we need to increase the frequency of face detection and increase the smooth factor
faceanimation.detect_interval = 2
faceanimation.smooth_factor = 0.8


app = FastAPI()
websocket_port = 8066


# WebSocket endpoint to receive and process images
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Receive the image as a binary stream
            image_data = await websocket.receive_bytes()
            processed_image = process_image(image_data)
            # Send the processed image back to the client
            await websocket.send_bytes(processed_image)
    except WebSocketDisconnect:
        pass


def process_image(image_data):
    image = Image.open(io.BytesIO(image_data))
    image_cv2 = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    face, result = faceanimation.inference(image_cv2)
    # resize to 256x256
    if face.shape[1] != 256 or face.shape[0] != 256:
        face = cv2.resize(face, (256, 256))
    if result.shape[0] != 256 or result.shape[1] != 256:
        result = cv2.resize(result, (256, 256))
    result = cv2.hconcat([face, result])
    _, processed_image_data = cv2.imencode(".jpg", result, [cv2.IMWRITE_JPEG_QUALITY, 95])
    return processed_image_data.tobytes()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=websocket_port)
