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

    def validate(self, request, pe_id):
        if self._same_as_previous(request, pe_id):
            return True

        try:
            PENumbers.get(pe_id)
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

    def _same_as_previous(self, request, pe_id):
        return request.pe_number == pe_id


class TaskOrderNumberValidator(object):
    def validate(self, task_order_number):
        try:
            TaskOrders.get(task_order_number)
        except NotFoundError:
            return False

        return True
