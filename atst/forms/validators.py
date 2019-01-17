import re
from wtforms.validators import ValidationError, StopValidation
import pendulum
from datetime import datetime
from atst.utils.localization import translate


def DateRange(lower_bound=None, upper_bound=None, message=None):
    def _date_range(form, field):
        if field.data is None:
            return

        now = pendulum.now().date()

        if isinstance(field.data, str):
            date = datetime.strptime(field.data, field.format)
        else:
            date = field.data

        if lower_bound is not None:
            if (now - lower_bound) > date:
                raise ValidationError(message)

        if upper_bound is not None:
            if (now + upper_bound) < date:
                raise ValidationError(message)

    return _date_range


def IsNumber(message=translate("forms.validators.is_number_message")):
    def _is_number(form, field):
        try:
            int(field.data)
        except ValueError:
            raise ValidationError(message)

    return _is_number


def PhoneNumber(message=translate("forms.validators.phone_number_message")):
    def _is_phone_number(form, field):
        digits = re.sub(r"\D", "", field.data)
        if len(digits) not in [5, 10]:
            raise ValidationError(message)

        match = re.match(r"[\d\-\(\) ]+", field.data)
        if not match or match.group() != field.data:
            raise ValidationError(message)

    return _is_phone_number


def Name(message=translate("forms.validators.name_message")):
    def _name(form, field):
        match = re.match(r"[\w \,\.\'\-]+", field.data)
        if not match or match.group() != field.data:
            raise ValidationError(message)

    return _name


def ListItemRequired(
    message=translate("forms.validators.list_item_required_message"),
    empty_values=("", None),
):
    def _list_item_required(form, field):
        non_empty_values = [v for v in field.data if v not in empty_values]
        if len(non_empty_values) == 0:
            raise ValidationError(message)

    return _list_item_required


def ListItemsUnique(message=translate("forms.validators.list_items_unique_message")):
    def _list_items_unique(form, field):
        if len(field.data) > len(set(field.data)):
            raise ValidationError(message)

    return _list_items_unique


def RequiredIfNot(other_field_name, message=translate("forms.validators.is_required")):
    """ A validator which makes a field required only if another field
        has a falsy value
        Args:
            other_field_name (str): the name of the field we check before
                determining if this field is required; if this other field is falsy,
                the field will be required
            message (str): an optional message to display if the field is
                required but hasNone value
    """
    def _required_if_not(form, field):
        other_field = form._fields.get(other_field_name)
        if other_field is None:
            raise Exception('no field named "%s" in form' % self.other_field_name)

        if not bool(other_field.data):
            if field.data is None:
                raise ValidationError(message)
        else:
            raise StopValidation()

    return _required_if_not
