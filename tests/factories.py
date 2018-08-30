import random
import string
import factory
from uuid import uuid4
import datetime

from atst.forms.data import SERVICE_BRANCHES
from atst.models.request import Request
from atst.models.request_revision import RequestRevision
from atst.models.request_status_event import RequestStatusEvent, RequestStatus
from atst.models.pe_number import PENumber
from atst.models.task_order import TaskOrder
from atst.models.user import User
from atst.models.role import Role
from atst.models.workspace import Workspace
from atst.models.request_status_event import RequestStatusEvent
from atst.domain.roles import Roles


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
    sequence = 1


class RequestRevisionFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = RequestRevision

    id = factory.Sequence(lambda x: uuid4())


class RequestFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Request

    id = factory.Sequence(lambda x: uuid4())
    status_events = factory.RelatedFactory(
        RequestStatusEventFactory, "request", new_status=RequestStatus.STARTED
    )
    creator = factory.SubFactory(UserFactory)
    revisions = factory.LazyAttribute(
        lambda r: [RequestFactory.create_initial_revision(r)]
    )

    class Params:
        initial_revision = None

    @classmethod
    def create_initial_revision(cls, request, dollar_value=1000000):
        user = request.creator
        default_data = dict(
            am_poc=False,
            dodid_poc=user.dod_id,
            email_poc=user.email,
            fname_poc=user.first_name,
            lname_poc=user.last_name,
            jedi_usage="adf",
            start_date=datetime.datetime(2018, 8, 8, tzinfo=datetime.timezone.utc),
            cloud_native="yes",
            dollar_value=dollar_value,
            dod_component=SERVICE_BRANCHES[2][1],
            data_transfers="Less than 100GB",
            expected_completion_date="Less than 1 month",
            jedi_migration="yes",
            num_software_systems=1,
            number_user_sessions=2,
            average_daily_traffic=1,
            engineering_assessment="yes",
            technical_support_team="yes",
            estimated_monthly_spend=100,
            average_daily_traffic_gb=4,
            rationalization_software_systems="yes",
            organization_providing_assistance="In-house staff",
            citizenship="United States",
            designation="military",
            phone_number="1234567890",
            email_request=user.email,
            fname_request=user.first_name,
            lname_request=user.last_name,
            service_branch=SERVICE_BRANCHES[1][1],
            date_latest_training=datetime.datetime(
                2018, 8, 6, tzinfo=datetime.timezone.utc
            ),
        )

        data = (
            request.initial_revision
            if request.initial_revision is not None
            else default_data
        )

        return RequestRevisionFactory.build(**data)


class PENumberFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = PENumber


class TaskOrderFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = TaskOrder


class WorkspaceFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Workspace

    request = factory.SubFactory(RequestFactory)
    # name it the same as the request ID by default
    name = factory.LazyAttribute(lambda w: w.request.id)
