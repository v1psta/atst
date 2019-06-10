import pendulum


class Clock(object):
    @classmethod
    def today(cls, tz="UTC"):
        return pendulum.today(tz=tz).date()

    @classmethod
    def now(cls, tz="UTC"):
        return pendulum.now(tz=tz)
