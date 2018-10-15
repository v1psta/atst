import re

from atst.domain.task_orders import TaskOrders
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
        if self._same_as_previous(request, field):
            return True

        try:
            PENumbers.get(field.data)
        except NotFoundError:
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

    def _same_as_previous(self, request, field):
        return request.pe_number == field.data


class TaskOrderNumberValidator(object):
    def validate(self, field):
        try:
            TaskOrders.get(field.data)
        except NotFoundError:
            return False

        return True
