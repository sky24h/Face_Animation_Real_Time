import os
import cv2
import time
import numpy as np
import asyncio
import websockets
from argparse import ArgumentParser

websocket_port = 8066


class VideoCamera(object):
    def __init__(self, CameraSize=(640, 480)):
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, CameraSize[0])
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, CameraSize[1])
        self.video.set(cv2.CAP_PROP_FPS, 24)
        # check if camera opened successfully
        if not self.video.isOpened():
            raise Exception("Camera not found")

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        image = cv2.flip(image, 1)
        return image


async def send_image(image, ScreenSize=512, SendSize=256):
    # Encode the image as bytes
    _, image_data = cv2.imencode(".jpg", cv2.resize(image, (SendSize, SendSize)), [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    image_bytes = image_data.tobytes()
    # print size
    print("Image size: ", len(image_bytes))

    # Connect to the FastAPI WebSocket server
    async with websockets.connect("ws://localhost:{}/ws".format(websocket_port)) as websocket:
        # Send the image to the server
        await websocket.send(image_bytes)
        print("Image sent to the server")
        # Receive and process the processed frame
        try:
            processed_frame_data = await websocket.recv()

            # Decode the processed frame
            processed_frame = cv2.imdecode(np.frombuffer(processed_frame_data, dtype=np.uint8), -1)
            processed_frame = cv2.resize(processed_frame, (ScreenSize * 2, ScreenSize))
            # return processed_frame
        except Exception as e:
            print(e)
            # return image
            processed_frame = np.ones((ScreenSize, ScreenSize, 3), dtype=np.uint8) * 255
            cv2.putText(processed_frame, "No response from the server", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
        cv2.imshow("Frame", processed_frame)
        cv2.waitKey(1)


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--output_size", default=512, type=int, help="size of the output video")
    args = parser.parse_args()


    camera = VideoCamera()

    frame_count = 0
    times = []
    while True:
        image = camera.get_frame()
        frame_count += 1
        time_start = time.time()
        asyncio.run(send_image(image, ScreenSize=args.output_size, SendSize=256))
        times.append(time.time() - time_start)
        if frame_count % 10 == 0:
            print("FPS: {:.2f}".format(1 / np.mean(times)))
            times = []
