from datetime import datetime, timedelta
import time
from math import sin, pi, floor

from locust.shape import LoadTestShape


class MultiDayTestShape(LoadTestShape):
    """
    Represents a load test shape that modulates test load over multiple days.

    This class is used to define a load test shape where the number of desired
    users (in locust terminology) fluctuates and extends across
    multiple hours or days. Fluctuation function can be calculated based on time-based
    properties this class provides.

    Put your reference datetime (reference_dt) and test duration (run_duration) into the class.
    Test will start assuming it is currently reference_dt datetime and will run for the specified duration.
    Modify the `tick` function and write your definition of `desired_users` formula. Base it on "current" date or "current" time values using helper properties of this class.

    :ivar reference_dt: Reference datetime that is treated as current time by the test when it starts.
    :type reference_dt: datetime
    :ivar run_duration: Test duration
    :type run_duration: timedelta
    """
    reference_dt: datetime = datetime(2025, 6, 15, 12)
    run_duration: timedelta = timedelta(days=2, hours=12)

    @property
    def _current_dt(self) -> datetime:
        return self.reference_dt + timedelta(seconds=time.perf_counter()-self.start_time)

    @property
    def isoweekday(self) -> int:
        """
        Gets the ISO weekday for the "current" date.

        The ISO weekday is an integer where 1 represents Monday
        and 7 represents Sunday. This property provides a
        convenient way to retrieve the ISO weekday of the
        currently stored datetime object.

        :return: An integer representing the ISO weekday.
        """
        return self._current_dt.isoweekday()

    @property
    def hour(self) -> int:
        """
        Gets the hour component (0-23) of the "current" datetime.
        """
        return self._current_dt.hour

    @property
    def minute(self) -> int:
        """
        Get the minute component (0-59) of the "current" datetime.
        """
        return self._current_dt.minute

    @property
    def minutes_since_ref_dt(self) -> float:
        """
        Calculate the number of minutes that have passed since the reference
        datetime as a floating-point value.
        """
        return (self._current_dt - self.reference_dt).total_seconds() / 60

    @property
    def hours_since_ref_dt(self) -> float:
        """
        Calculates the number of elapsed hours since the reference datetime as a floating-point value.
        """
        return self.minutes_since_ref_dt / 60

    @property
    def days_since_ref_dt(self) -> float:
        """
        Calculates the number of elapsed days since the reference datetime as a floating-point value.
        """
        return self.hours_since_ref_dt / 24

    def tick(self):
        if time.perf_counter()-self.start_time > self.run_duration.total_seconds():
            return None

        # Modify `desired_users` formula to your needs.
        # This is a sample one:
        # - start with 10 users and gradually increase the number of users by 5 a day;
        # - within a day modulate additional users by sin wave, with max 10 additional users added to the load shape at the peak of the wave (hour 12);
        # - at hours (12, 13, 18, 19) add 15 additional users to the test shape.
        extra_users = 15 if self.hour in (12, 13, 18, 19) else 0
        desired_users = 5 * self.days_since_ref_dt + 10 * sin((self.days_since_ref_dt - floor(self.days_since_ref_dt)) * pi) + 10 + extra_users

        return max([0, round(desired_users)]), 100
