from picamera import PiCamera
import picamera
import os
from time import sleep
from measurements_calendar import DailySchedule
import datetime as dt


class Camera:
    def __init__(
        self, framerate, sensorMode=2
    ) -> None:  # for HQ camera sensor mode 2: 2x2 binned full FOV
        self.sensorMode = sensorMode
        self.framerate = framerate
        self.camera = PiCamera(sensor_mode=self.sensorMode, framerate=self.framerate)
        sleep(2)

    def bufferRecording(self):
        stream = picamera.PiCameraCircularIO(self.camera, seconds=20)
        self.camera.start_recording(stream, format="h264")
        try:
            while dailySchedule.isDark(dt.datetime.now()):
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

    def isMeteorDetected(self):
        return True

    def detectMotion(self):
        return True


class DailyMeasurement:
    def __init__(self, camera: Camera, dailySchedule: DailySchedule) -> None:
        date = dt.date.today()
        try:
            os.makedirs(f"/{date}")
        except FileExistsError:
            pass
        sunset, sunrise = dailySchedule.getMeasurementWindow(date)

        while True:
            sleep(10)
            if dt.datetime.now() >= sunrise:
                break  # thid could be the option if the script should rather be called everyday which should be more secure
                # date = dt.date.today()
                # sunrise, sunset = dailySchedule.getMeasurementWindow(date)

            if not dailySchedule.isDark(sunrise, sunset, dt.datetime.now()):
                pass
            else:
                camera.bufferRecording()
                pass


DailyMeasurement(Camera(framerate=10), DailySchedule)
