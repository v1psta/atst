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
from atst.models.workspace_role import WorkspaceRole, Status as WorkspaceRoleStatus
from atst.models.environment_role import EnvironmentRole
from atst.models.invitation import Invitation, Status as InvitationStatus
from atst.domain.invitations import Invitations


def random_service_branch():
    return random.choice([k for k, v in SERVICE_BRANCHES if k])


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
    phone_number = factory.LazyFunction(
        lambda: "".join(random.choices(string.digits, k=10))
    )
    service_branch = factory.LazyFunction(random_service_branch)
    citizenship = "United States"
    designation = "military"
    date_latest_training = factory.LazyFunction(
        lambda: datetime.date.today()
        + datetime.timedelta(days=-(random.randrange(1, 365)))
    )

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
    def _adjust_kwargs(cls, **kwargs):
        if kwargs.pop("with_task_order", False) and "task_order" not in kwargs:
            kwargs["task_order"] = TaskOrderFactory.build()
        return kwargs

    @classmethod
    def create_initial_status_event(cls, request):
        return RequestStatusEventFactory(
            request=request,
            new_status=RequestStatus.STARTED,
            revision=request.revisions,
        )

    @classmethod
    def create_initial_revision(cls, request, dollar_value=1_000_000):
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
            dod_component=random_service_branch(),
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
            phone_ext="123",
            email_request=user.email,
            fname_request=user.first_name,
            lname_request=user.last_name,
            service_branch=random_service_branch(),
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
    clin_0001 = random.randrange(100, 100_000)
    clin_0003 = random.randrange(100, 100_000)
    clin_1001 = random.randrange(100, 100_000)
    clin_1003 = random.randrange(100, 100_000)
    clin_2001 = random.randrange(100, 100_000)
    clin_2003 = random.randrange(100, 100_000)


class WorkspaceFactory(Base):
    class Meta:
        model = Workspace

    request = factory.SubFactory(RequestFactory, with_task_order=True)
    # name it the same as the request ID by default
    name = factory.LazyAttribute(lambda w: w.request.id)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_projects = kwargs.pop("projects", [])
        owner = kwargs.pop("owner", UserFactory.create())
        members = kwargs.pop("members", [])

        workspace = super()._create(model_class, *args, **kwargs)

        projects = [
            ProjectFactory.create(workspace=workspace, **p) for p in with_projects
        ]

        workspace.request.creator = owner
        WorkspaceRoleFactory.create(
            workspace=workspace,
            role=Roles.get("owner"),
            user=owner,
            status=WorkspaceRoleStatus.ACTIVE,
        )

        for member in members:
            user = member.get("user", UserFactory.create())
            role_name = member["role_name"]
            WorkspaceRoleFactory.create(
                workspace=workspace,
                role=Roles.get(role_name),
                user=user,
                status=WorkspaceRoleStatus.ACTIVE,
            )

        workspace.projects = projects
        return workspace


class ProjectFactory(Base):
    class Meta:
        model = Project

    workspace = factory.SubFactory(WorkspaceFactory)
    name = factory.Faker("name")
    description = "A test project"

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_environments = kwargs.pop("environments", [])
        project = super()._create(model_class, *args, **kwargs)

        environments = [
            EnvironmentFactory.create(project=project, **e) for e in with_environments
        ]

        project.environments = environments
        return project


class EnvironmentFactory(Base):
    class Meta:
        model = Environment

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        with_members = kwargs.pop("members", [])
        environment = super()._create(model_class, *args, **kwargs)

        for member in with_members:
            user = member.get("user", UserFactory.create())
            role_name = member["role_name"]
            EnvironmentRoleFactory.create(
                environment=environment, role=role_name, user=user
            )

        return environment


class WorkspaceRoleFactory(Base):
    class Meta:
        model = WorkspaceRole

    workspace = factory.SubFactory(WorkspaceFactory)
    role = factory.SubFactory(RoleFactory)
    user = factory.SubFactory(UserFactory)


class EnvironmentRoleFactory(Base):
    class Meta:
        model = EnvironmentRole

    environment = factory.SubFactory(EnvironmentFactory)
    role = factory.Faker("name")
    user = factory.SubFactory(UserFactory)


class InvitationFactory(Base):
    class Meta:
        model = Invitation

    status = InvitationStatus.PENDING
    expiration_time = Invitations.current_expiration_time()
