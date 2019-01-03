from flask import (
    request as http_request,
    render_template,
    g,
    redirect,
    url_for,
    current_app as app,
)

from . import task_orders_bp
from atst.domain.task_orders import TaskOrders
from atst.domain.workspaces import Workspaces
import atst.forms.task_order as task_order_form
from atst.services.invitation import Invitation as InvitationService


TASK_ORDER_SECTIONS = [
    {
        "section": "app_info",
        "title": "What You're Building",
        "template": "task_orders/new/app_info.html",
        "form": task_order_form.AppInfoForm,
    },
    {
        "section": "funding",
        "title": "Funding",
        "template": "task_orders/new/funding.html",
        "form": task_order_form.FundingForm,
        "unclassified_form": task_order_form.UnclassifiedFundingForm,
    },
    {
        "section": "oversight",
        "title": "Oversight",
        "template": "task_orders/new/oversight.html",
        "form": task_order_form.OversightForm,
    },
    {
        "section": "review",
        "title": "Review & Download",
        "template": "task_orders/new/review.html",
        "form": task_order_form.ReviewForm,
    },
]


class ShowTaskOrderWorkflow:
    def __init__(self, screen=1, task_order_id=None):
        self.screen = screen
        self.task_order_id = task_order_id
        self._section = TASK_ORDER_SECTIONS[screen - 1]
        self._task_order = None
        self._form = None

    @property
    def task_order(self):
        if not self._task_order and self.task_order_id:
            self._task_order = TaskOrders.get(self.task_order_id)

        return self._task_order

    @property
    def task_order_formdata(self):
        task_order_dict = self.task_order.to_dictionary()
        for field in task_order_dict:
            if task_order_dict[field] is None:
                task_order_dict[field] = ""
        return task_order_dict

    @property
    def form(self):
        form_type = (
            "unclassified_form"
            if "unclassified_form" in self._section and not app.config.get("CLASSIFIED")
            else "form"
        )

        if self._form:
            pass
        elif self.task_order:
            self._form = self._section[form_type](formdata=self.task_order_formdata)
        else:
            self._form = self._section[form_type]()

        return self._form

    @property
    def template(self):
        return self._section["template"]

    @property
    def display_screens(self):
        screen_info = TASK_ORDER_SECTIONS.copy()

        if self.task_order:
            for section in screen_info:
                if TaskOrders.is_section_complete(self.task_order, section["section"]):
                    section["complete"] = True

        return screen_info


class UpdateTaskOrderWorkflow(ShowTaskOrderWorkflow):
    def __init__(self, form_data, user, screen=1, task_order_id=None):
        self.form_data = form_data
        self.user = user
        self.screen = screen
        self.task_order_id = task_order_id
        self._task_order = None
        self._section = TASK_ORDER_SECTIONS[screen - 1]

    @property
    def form(self):
        return self._section["form"](self.form_data)

    def validate(self):
        return self.form.validate()

    def _update_task_order(self):
        if self.task_order:
            TaskOrders.update(self.task_order, **self.form.data)
        else:
            ws = Workspaces.create(self.user, self.form.portfolio_name.data)
            to_data = self.form.data.copy()
            to_data.pop("portfolio_name")
            self._task_order = TaskOrders.create(workspace=ws, creator=self.user)
            TaskOrders.update(self.task_order, **to_data)

    OFFICER_INVITATIONS = [
        {
            "field": "ko_invite",
            "prefix": "ko",
            "role": "contracting_officer",
            "subject": "Review a task order",
            "template": "emails/invitation.txt",
        },
        {
            "field": "cor_invite",
            "prefix": "cor",
            "role": "contracting_officer_representative",
            "subject": "Help with a task order",
            "template": "emails/invitation.txt",
        },
        {
            "field": "so_invite",
            "prefix": "so",
            "role": "security_officer",
            "subject": "Review security for a task order",
            "template": "emails/invitation.txt",
        },
    ]

    def _update_invitations(self):
        for officer_type in self.OFFICER_INVITATIONS:
            field = officer_type["field"]
            if hasattr(self.form, field) and self.form[field].data:
                prefix = officer_type["prefix"]
                officer_data = {
                    field: getattr(self.task_order, prefix + "_" + field)
                    for field in ["first_name", "last_name", "email", "dod_id"]
                }
                invite_service = InvitationService(
                    self.user,
                    self.task_order.workspace,
                    {**officer_data, "workspace_role": officer_type["role"]},
                    subject=officer_type["subject"],
                    email_template=officer_type["template"],
                )
                invite_service.invite()

    def update(self):
        self._update_task_order()
        self._update_invitations()
        return self.task_order


@task_orders_bp.route("/task_orders/new/<int:screen>")
@task_orders_bp.route("/task_orders/new/<int:screen>/<task_order_id>")
def new(screen, task_order_id=None):
    workflow = ShowTaskOrderWorkflow(screen, task_order_id)
    return render_template(
        workflow.template,
        current=screen,
        task_order_id=task_order_id,
        task_order=workflow.task_order,
        screens=workflow.display_screens,
        form=workflow.form,
    )


@task_orders_bp.route("/task_orders/new/<int:screen>", methods=["POST"])
@task_orders_bp.route("/task_orders/new/<int:screen>/<task_order_id>", methods=["POST"])
def update(screen, task_order_id=None):
    workflow = UpdateTaskOrderWorkflow(
        http_request.form, g.current_user, screen, task_order_id
    )

    if workflow.validate():
        workflow.update()
        return redirect(
            url_for(
                "task_orders.new",
                screen=screen + 1,
                task_order_id=workflow.task_order.id,
            )
        )
    else:
        return render_template(
            workflow.template,
            current=screen,
            task_order_id=task_order_id,
            screens=TASK_ORDER_SECTIONS,
            form=workflow.form,
        )
