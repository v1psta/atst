import random
import string
import factory
from uuid import uuid4

from atst.models.request import Request
from atst.models.request_status_event import RequestStatusEvent, RequestStatus
from atst.models.pe_number import PENumber
from atst.models.task_order import TaskOrder
from atst.models.user import User
from atst.models.role import Role
from atst.models.request_status_event import RequestStatusEvent
from atst.domain.roles import Roles


class RequestStatusFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RequestStatusEvent


class RequestFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Request

    id = factory.Sequence(lambda x: uuid4())
    status_events = factory.RelatedFactory(
        RequestStatusFactory, "request", new_status=RequestStatus.STARTED
    )
    body = {}


class PENumberFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PENumber


class TaskOrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TaskOrder


class RoleFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Role

    permissions = []


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User

    id = factory.Sequence(lambda x: uuid4())
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    atat_role = factory.SubFactory(RoleFactory)
    dod_id = factory.LazyFunction(lambda: "".join(random.choices(string.digits, k=10)))


class RequestStatusEventFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = RequestStatusEvent

    id = factory.Sequence(lambda x: uuid4())
