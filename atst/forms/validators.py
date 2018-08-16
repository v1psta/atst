import re
from wtforms.validators import ValidationError
import pendulum

from atst.domain.date import parse_date


def DateRange(lower_bound=None, upper_bound=None, message=None):
    def _date_range(form, field):
        now = pendulum.now().date()
        date = parse_date(field.data)

        if lower_bound is not None:
            if (now - lower_bound) > date:
                raise ValidationError(message)

        if upper_bound is not None:
            if (now + upper_bound) < date:
                raise ValidationError(message)

    return _date_range


def IsNumber(message="Please enter a valid number."):
    def _is_number(form, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError(message)

    return _is_number


def PhoneNumber(message="Please enter a valid 5 or 10 digit phone number."):
    def _is_phone_number(form, field):
        digits = re.sub(r"\D", "", field.data)
        if len(digits) not in [5, 10]:
            raise ValidationError(message)

        match = re.match(r"[\d\-\(\) ]+", field.data)
        if not match or match.group() != field.data:
            raise ValidationError(message)

    return _is_phone_number


def Alphabet(message="Please enter only letters."):
    def _alphabet(form, field):
        match = re.match(r"[A-Za-z]+", field.data)
        if not match or match.group() != field.data:
            raise ValidationError(message)

    return _alphabet
