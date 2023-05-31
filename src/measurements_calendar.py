# from picamera import PiCamera
from datetime import date
import datetime as dt
import pytz

import astral.sun
from astral import LocationInfo
import astral.moon


class DailySchedule:
    def __init__(
        self,
        longitude=11.5,
        latitude=50.9,
        timezone="Europe/Berlin",
        region="East",
        name="Jena",
    ):
        self.timezone = pytz.timezone(timezone)
        self.longitude = longitude
        self.latitude = latitude

        self.city = LocationInfo(
            name=name,
            region=region,
            timezone=self.timezone,
            longitude=self.longitude,
            latitude=self.latitude,
        )

        self.date = dt.date.today().isoformat()

    def isDark(self, sunrise, sunset, currentDatetime):
        currentDatetime = currentDatetime.replace(tzinfo=self.timezone)
        return sunset <= currentDatetime <= sunrise

    def isSupposedToMeasure(self, start, stop, currentDatetime):
        currentDatetime = currentDatetime.replace(tzinfo=self.timezone)
        return start <= currentDatetime <= stop

    def getTestWindow(self, delta):
        now = dt.datetime.now()
        now = now.replace(tzinfo=self.timezone)
        start = now + dt.timedelta(seconds=5)
        stop = now + dt.timedelta(minutes=delta)
        return start, stop

    def getMeasurementWindow(self, date):
        tomorrow = date + dt.timedelta(days=1)
        sunrise = astral.sun.time_at_elevation(
            self.city.observer, -7, tomorrow, tzinfo=self.timezone
        )  # diameter of sun is here assumed to be roughly 0.57 deg

        sunset = astral.sun.time_at_elevation(
            self.city.observer, 187, date, tzinfo=self.timezone
        )
        return sunset, sunrise
