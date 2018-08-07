import factory
from uuid import uuid4

from atst.models import Request
from atst.models.pe_number import PENumber
from atst.models.task_order import TaskOrder
from atst.models.user import User
from atst.models.role import Role


class RequestFactory(factory.alchemy.SQLAlchemyModelFactory):

    class Meta:
        model = Request

    id = factory.Sequence(lambda x: uuid4())


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
    email = "fake.user@mail.com"
    first_name = "Fake"
    last_name = "User"
    atat_role = factory.SubFactory(RoleFactory)

