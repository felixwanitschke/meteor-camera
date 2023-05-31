from picamera2.encoders import H264Encoder, Quality
from picamera2.outputs import CircularOutput, FfmpegOutput
from picamera2 import Picamera2, MappedArray
import os
import io
from time import sleep
from measurements_calendar import DailySchedule
import datetime as dt
from PIL import Image
import time
import numpy as np
from pprint import *
import random

# main={"size": (2028, 1520)}


class Camera:
    def __init__(self, framerate, outputPath, sensorMode=0) -> None:
        self.sensorMode = sensorMode
        self.framerate = framerate
        self.lsize = (1280, 720)
        self.camera = Picamera2()
        video_config = self.camera.create_video_configuration(
            controls={"FrameRate": self.framerate},
            main={"size": (1280, 720), "format": "RGB888"},
            lores={"size": self.lsize, "format": "YUV420"},
        )
        self.camera.configure(video_config)
        self.outputPath = outputPath
        self.encoder = H264Encoder(1000000, repeat=True)
        self.encoder.output = CircularOutput(buffersize=7 * self.framerate)
        self.camera.encoder = self.encoder
        self.camera.start()
        sleep(2)
        self.prior_image = None

    # def bufferRecording(self, sunset, sunrise, dailySchedule: DailySchedule):
    #     stream = picam.PiCameraCircularIO(self.camera, seconds=10)
    #     self.camera.start_recording(stream, format="h264")
    #     try:
    #         while dailySchedule.isDark(sunset, sunrise, dt.datetime.now()):
    #             self.camera.wait_recording(0.5)
    #             if self.isMeteorDetected():
    #                 print("Motion detected!")
    #                 detectionTime = dt.datetime.now().isoformat()
    #                 self.camera.wait_recording(10)
    #                 # while self.detectMotion():
    #                 #    self.camera.wait_recording(0.5)
    #                 print("Motion stopped!")
    #                 stream.copy_to(f"Detection_{detectionTime}.h264", seconds=20)
    #     finally:
    #         self.camera.stop_recording()

    def bufferRecordingTest(self, start, stop, dailySchedule: DailySchedule):
        self.camera.start_encoder()
        w, h = self.lsize
        prev = None
        encoding = False
        ltime = 0
        print("Recording started!")
        try:
            while dailySchedule.isSupposedToMeasure(start, stop, dt.datetime.now()):
                time.sleep(0.5)
                cur = self.camera.capture_buffer("lores")
                print(cur.shape)
                cur = cur[: w * h].reshape(h, w)
                print(cur.shape)
                if prev is not None:
                    # Measure pixels differences between current and
                    # previous frame
                    mse = np.square(np.subtract(cur, prev)).mean()
                    if mse > 7:
                        if not encoding:
                            detectionTime = dt.datetime.now().isoformat()
                            self.encoder.output.fileoutput = (
                                f"{self.outputPath}/Detection_{detectionTime}.h264"
                            )
                            self.encoder.output.start()
                            encoding = True
                            print("New Motion", mse)
                            if time.time() - ltime > 7.0:
                                pass  # dann aufnahme abbrechen, da Sattelit
                        ltime = time.time()
                    else:
                        if encoding and time.time() - ltime > 7.0:
                            self.encoder.output.stop()
                            encoding = False
                            print("Video End")
                prev = cur

        finally:
            print("Measurement stopped")
            self.camera.stop()

    def standard_recording(self, recordingTime):
        detectionTime = dt.datetime.now().isoformat()
        self.camera.start_recording(self.encoder, self.output, Quality.HIGH)
        self.output.fileoutput = f"{self.outputPath}/Detection_{detectionTime}.h264"
        self.output.start()
        time.sleep(recordingTime)
        self.output.stop()
        self.camera.stop_recording()

    def isMeteorDetected(self):
        return True

    def detect_motion(self):
        stream = io.BytesIO()
        self.camera.capture(stream, format="jpeg", use_video_port=True)
        stream.seek(0)
        if self.prior_image is None:
            self.prior_image = Image.open(stream)
            return False
        else:
            current_image = Image.open(stream)
            # Compare current_image to prior_image to detect motion. This is
            # left as an exercise for the reader!
            result = random.randint(0, 10) == 0
            # Once motion detection is done, make the prior image the current
            self.prior_image = current_image
            return result


class DailyMeasurement:
    def __init__(self) -> None:
        camera = Camera(framerate=10)
        print("Camera created")
        dailySchedule = DailySchedule()
        date = dt.date.today()
        filename = f"/home/kefe/{date}"

        try:
            os.makedirs(filename)
        except FileExistsError:
            pass
        sunset, sunrise = dailySchedule.getMeasurementWindow(date)

        while True:
            sleep(10)
            if dt.datetime.now() >= sunrise:
                break  # thid could be the option if the script should rather be called everyday which should be more secure
                # date = dt.date.today()
                # sunrise, sunset = dailySchedule.getMeasurementWindow(date)

            if not dailySchedule.isDark(sunset, sunrise, dt.datetime.now()):
                pass
            else:
                camera.bufferRecording(sunset, sunrise, dailySchedule)
                pass


class TestMeasurement:
    def __init__(self, delta) -> None:
        date_iso = dt.date.today().isoformat()
        filename = f"/home/kefe/{date_iso}"
        camera = Camera(framerate=30, outputPath=filename)
        print("Camera created")
        dailySchedule = DailySchedule()
        print("Schedule created")

        try:
            os.makedirs(filename)
        except FileExistsError:
            pass

        start, stop = dailySchedule.getTestWindow(delta)

        while True:
            sleep(5)
            if dt.datetime.now().replace(tzinfo=dailySchedule.timezone) >= stop:
                break
            if not dailySchedule.isSupposedToMeasure(start, stop, dt.datetime.now()):
                pass
            else:
                camera.bufferRecordingTest(start, stop, dailySchedule)
                pass


# date_iso = dt.date.today().isoformat()
# filename = f"/home/kefe/{date_iso}"

# camera = Camera(framerate=10, outputPath=filename)
# camera.standard_recording(10)

TestMeasurement(delta=1)
