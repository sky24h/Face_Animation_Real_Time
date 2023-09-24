import os
import cv2
import time
import numpy as np

from argparse import ArgumentParser
from demo_utils import FaceAnimationClass


class VideoCamera(object):
    def __init__(self, video_path=0, CameraSize=(640, 480)):
        self.video_path = video_path
        self.video = cv2.VideoCapture(video_path) if video_path != 0 else cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, CameraSize[0])
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, CameraSize[1])
        self.video.set(cv2.CAP_PROP_FPS, 24)
        # check if camera opened successfully
        if video_path == 0 and not self.video.isOpened():
            raise Exception("Camera not found")
        elif video_path != 0 and not self.video.isOpened():
            raise Exception("Video file not found")

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        image = cv2.flip(image, 1) if self.video_path == 0 else image
        return image


def process_frame(image, ScreenSize=512):
    face, result = faceanimation.inference(image)
    if face.shape[1] != ScreenSize:
        face = cv2.resize(face, (ScreenSize, ScreenSize))
    if result.shape[0] != ScreenSize or result.shape[1] != ScreenSize:
        result = cv2.resize(result, (ScreenSize, ScreenSize))
    return cv2.hconcat([face, result])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--source_image", default="./assets/source.jpg", help="path to source image")
    parser.add_argument("--driving_video", default=None, help="path to driving video")
    parser.add_argument("--result_video", default="./result_video.mp4", help="path to output")
    parser.add_argument("--output_size", default=512, type=int, help="size of the output video")
    parser.add_argument("--restore_face", default=False, action="store_true", help="restore face from the result")
    args = parser.parse_args()

    if args.driving_video is None:
        video_path = 0
        print("Using webcam")
    else:
        video_path = args.driving_video
        print("Using driving video: {}".format(video_path))
    camera = VideoCamera(video_path=video_path)
    faceanimation = FaceAnimationClass(source_image_path=args.source_image, use_sr=args.restore_face)

    frames = [] if args.result_video is not None else None
    frame_count = 0
    times = []
    while True:
        time_start = time.time()
        image = camera.get_frame()
        if image is None and frame_count != 0:
            print("Video ended")
            break
        try:
            res = process_frame(image, ScreenSize=args.output_size)
            frame_count += 1
            times.append(time.time() - time_start)
            if frame_count % 100 == 0:
                print("FPS: {:.2f}".format(1 / np.mean(times)))
                times = []
            frames.append(res) if args.result_video is not None else None
        except Exception as e:
            print(e)
            raise e

    if args.result_video is not None:
        import imageio
        from tqdm import tqdm

        writer = imageio.get_writer(args.result_video, fps=24, quality=9, macro_block_size=1, codec="libx264", pixelformat="yuv420p")
        for frame in tqdm(frames):
            writer.append_data(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        writer.close()
        print("Video saved to {}".format(args.result_video))
