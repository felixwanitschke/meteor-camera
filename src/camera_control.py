from picamera import PiCamera
import picamera as picam
import os
import io
from time import sleep
from measurements_calendar import DailySchedule
import datetime as dt
from PIL import Image
import time
import random


class Camera:
    def __init__(
        self, framerate, sensorMode=0
    ) -> None:  # for HQ camera sensor mode 2: 2x2 binned full FOV
        self.sensorMode = sensorMode
        self.framerate = framerate
        self.camera = PiCamera(sensor_mode=self.sensorMode, framerate=self.framerate)
        sleep(2)
        self.prior_image = None

    def bufferRecording(self, sunset, sunrise, dailySchedule: DailySchedule):
        stream = picam.PiCameraCircularIO(self.camera, seconds=10)
        self.camera.start_recording(stream, format="h264")
        try:
            while dailySchedule.isDark(sunset, sunrise, dt.datetime.now()):
                self.camera.wait_recording(0.5)
                if self.isMeteorDetected():
                    print("Motion detected!")
                    detectionTime = dt.datetime.now().isoformat()
                    self.camera.wait_recording(10)
                    # while self.detectMotion():
                    #    self.camera.wait_recording(0.5)
                    print("Motion stopped!")
                    stream.copy_to(f"Detection_{detectionTime}.h264", seconds=20)
        finally:
            self.camera.stop_recording()

    def bufferRecordingTest(self, start, stop, dailySchedule: DailySchedule):
        stream = picam.PiCameraCircularIO(self.camera, seconds=20)
        self.camera.start_recording(stream, format="h264")
        print("Recording started!")
        try:
            while dailySchedule.isSupposedToMeasure(start, stop, dt.datetime.now()):
                self.camera.wait_recording(0.5)
                if self.detect_motion():
                    # print(self.camera.exposure_speed)
                    print("Motion detected!")
                    loop_start = time.time()
                    detectionTime = dt.datetime.now().isoformat()
                    self.camera.split_recording(
                        f"/home/kefe/{dailySchedule.date}/Detection_{detectionTime}.h264"
                    )
                    self.camera.wait_recording(10)
                    self.camera.split_recording(stream)
                    loop_stop = time.time()

                    # stream.copy_to(
                    #     f"/home/kefe/{dailySchedule.date}/Detection_{detectionTime}.h264",
                    #     seconds=15,
                    # )

                    loopTime = loop_stop - loop_start
                    print(loopTime)
        finally:
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

        try:
            os.makedirs(f"/home/kefe/{date}")
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
    def __init__(self) -> None:
        camera = Camera(framerate=30)
        print("Camera created")
        dailySchedule = DailySchedule()
        print("Schedule created")
        date = dt.date.today()
        date_iso = dt.date.today().isoformat()
        try:
            os.makedirs(f"/home/kefe/{date_iso}")
        except FileExistsError:
            os.makedirs(f"/home/kefe/{date_iso}(1)")
            pass

        finally:
            pass
        start, stop = dailySchedule.getTestWindow(delta=1)

        while True:
            sleep(5)
            if dt.datetime.now().replace(tzinfo=dailySchedule.timezone) >= stop:
                break
            if not dailySchedule.isSupposedToMeasure(start, stop, dt.datetime.now()):
                pass
            else:
                camera.bufferRecordingTest(start, stop, dailySchedule)
                pass


TestMeasurement()
