import re

from atst.domain.legacy_task_orders import LegacyTaskOrders
from atst.domain.pe_numbers import PENumbers
from atst.domain.exceptions import NotFoundError


class PENumberValidator(object):
    PE_REGEX = re.compile(
        r"""
        (0?\d) # program identifier
        (0?\d) # category
        (\d)   # activity
        (\d+)  # sponsor element
        (.+)   # service
    """,
        re.X,
    )

    def validate(self, request, field):
        if field.errors:
            return False

        if self._same_as_previous(request, field.data):
            return True

        try:
            PENumbers.get(field.data)
        except NotFoundError:
            self._apply_error(field)
            return False

        return True

    def suggest_pe_id(self, pe_id):
        suggestion = pe_id
        match = self.PE_REGEX.match(pe_id)
        if match:
            (program, category, activity, sponsor, service) = match.groups()
            if len(program) < 2:
                program = "0" + program
            if len(category) < 2:
                category = "0" + category
            suggestion = "".join((program, category, activity, sponsor, service))

        if suggestion != pe_id:
            return suggestion
        return None

    def _same_as_previous(self, request, pe_id):
        return request.pe_number == pe_id

    def _apply_error(self, field):
        suggestion = self.suggest_pe_id(field.data)
        error_str = (
            "We couldn't find that PE number. {}"
            "If you have double checked it you can submit anyway. "
            "Your request will need to go through a manual review."
        ).format('Did you mean "{}"? '.format(suggestion) if suggestion else "")
        field.errors += (error_str,)


class TaskOrderNumberValidator(object):
    def validate(self, field):
        try:
            LegacyTaskOrders.get(field.data)
        except NotFoundError:
            self._apply_error(field)
            return False

        return True

    def _apply_error(self, field):
        field.errors += ("Task Order number not found",)
