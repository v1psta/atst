import random
import string
import factory
from uuid import uuid4
import datetime
from faker import Faker as _Faker

from atst.forms.data import SERVICE_BRANCHES
from atst.models.environment import Environment
from atst.models.request import Request
from atst.models.request_revision import RequestRevision
from atst.models.request_review import RequestReview
from atst.models.request_status_event import RequestStatusEvent, RequestStatus
from atst.models.pe_number import PENumber
from atst.models.project import Project
from atst.models.task_order import TaskOrder, Source, FundingType
from atst.models.user import User
from atst.models.role import Role
from atst.models.workspace import Workspace
from atst.domain.roles import Roles


class Base(factory.alchemy.SQLAlchemyModelFactory):
    @classmethod
    def dictionary(cls, **attrs):
        return factory.build(dict, FACTORY_CLASS=cls, **attrs)


class RoleFactory(Base):
    class Meta:
        model = Role

    name = factory.Faker("name")
    display_name = "Role display name"
    description = "This is a test role."
    permissions = []


class UserFactory(Base):
    class Meta:
        model = User

    id = factory.Sequence(lambda x: uuid4())
    email = factory.Faker("email")
    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")
    atat_role = factory.SubFactory(RoleFactory)
    dod_id = factory.LazyFunction(lambda: "".join(random.choices(string.digits, k=10)))

    @classmethod
    def from_atat_role(cls, atat_role_name, **kwargs):
        role = Roles.get(atat_role_name)
        return cls.create(atat_role=role, **kwargs)


class RequestStatusEventFactory(Base):
    class Meta:
        model = RequestStatusEvent

    id = factory.Sequence(lambda x: uuid4())
    sequence = 1


class RequestRevisionFactory(Base):
    class Meta:
        model = RequestRevision

    id = factory.Sequence(lambda x: uuid4())


class RequestReviewFactory(Base):
    class Meta:
        model = RequestReview

    comment = factory.Faker("sentence")
    fname_mao = factory.Faker("first_name")
    lname_mao = factory.Faker("last_name")
    email_mao = factory.Faker("email")
    phone_mao = factory.LazyFunction(
        lambda: "".join(random.choices(string.digits, k=10))
    )
    fname_ccpo = factory.Faker("first_name")
    lname_ccpo = factory.Faker("last_name")


class RequestFactory(Base):
    class Meta:
        model = Request

    id = factory.Sequence(lambda x: uuid4())
    creator = factory.SubFactory(UserFactory)
    revisions = factory.LazyAttribute(
        lambda r: [RequestFactory.create_initial_revision(r)]
    )
    status_events = factory.RelatedFactory(
        RequestStatusEventFactory,
        "request",
        new_status=RequestStatus.STARTED,
        revision=factory.LazyAttribute(lambda se: se.factory_parent.revisions[-1]),
    )

    class Params:
        initial_revision = None

    @classmethod
    def create_initial_status_event(cls, request):
        return RequestStatusEventFactory(
            request=request,
            new_status=RequestStatus.STARTED,
            revision=request.revisions,
        )

    @classmethod
    def create_initial_revision(cls, request, dollar_value=1000000):
        user = request.creator
        default_data = dict(
            name=factory.Faker("domain_word"),
            am_poc=False,
            dodid_poc=user.dod_id,
            email_poc=user.email,
            fname_poc=user.first_name,
            lname_poc=user.last_name,
            jedi_usage="adf",
            start_date=datetime.date(2050, 1, 1),
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
            date_latest_training=datetime.date(2018, 8, 6),
        )

        data = (
            request.initial_revision
            if request.initial_revision is not None
            else default_data
        )

        return RequestRevisionFactory.build(**data)

    @classmethod
    def create_with_status(cls, status=RequestStatus.STARTED, **kwargs):
        request = RequestFactory(**kwargs)
        RequestStatusEventFactory.create(
            request=request, revision=request.latest_revision, new_status=status
        )
        return request

    @classmethod
    def mock_financial_data(cls):
        fake = _Faker()
        return {
            "pe_id": "0101110F",
            "fname_co": fake.first_name(),
            "lname_co": fake.last_name(),
            "email_co": fake.email(),
            "office_co": fake.phone_number(),
            "fname_cor": fake.first_name(),
            "lname_cor": fake.last_name(),
            "email_cor": fake.email(),
            "office_cor": fake.phone_number(),
            "uii_ids": "123abc",
            "treasury_code": "00123456",
            "ba_code": "02A",
        }


class PENumberFactory(Base):
    class Meta:
        model = PENumber


class TaskOrderFactory(Base):
    class Meta:
        model = TaskOrder

    source = Source.MANUAL
    funding_type = FundingType.PROC
    funding_type_other = None
    number = factory.LazyFunction(
        lambda: "".join(random.choices(string.ascii_uppercase + string.digits, k=13))
    )
    expiration_date = factory.LazyFunction(
        lambda: datetime.date(
            datetime.date.today().year + random.randrange(1, 5),
            random.randrange(1, 12),
            random.randrange(1, 28),
        )
    )
    clin_0001 = random.randrange(100, 100000)
    clin_0003 = random.randrange(100, 100000)
    clin_1001 = random.randrange(100, 100000)
    clin_1003 = random.randrange(100, 100000)
    clin_2001 = random.randrange(100, 100000)
    clin_2003 = random.randrange(100, 100000)


class WorkspaceFactory(Base):
    class Meta:
        model = Workspace

    request = factory.SubFactory(RequestFactory)
    # name it the same as the request ID by default
    name = factory.LazyAttribute(lambda w: w.request.id)


class ProjectFactory(Base):
    class Meta:
        model = Project

    workspace = factory.SubFactory(WorkspaceFactory)
    name = factory.Faker("name")
    description = "A test project"


class EnvironmentFactory(Base):
    class Meta:
        model = Environment
