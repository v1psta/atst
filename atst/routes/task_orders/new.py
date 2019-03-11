from copy import deepcopy

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
from atst.domain.portfolios import Portfolios
from atst.utils.flash import formatted_flash as flash
import atst.forms.task_order as task_order_form


TASK_ORDER_SECTIONS = [
    {
        "section": "app_info",
        "title": "What You're Making",
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
        "title": "Review",
        "template": "task_orders/new/review.html",
        "form": task_order_form.ReviewForm,
    },
]


class ShowTaskOrderWorkflow:
    def __init__(self, user, screen=1, task_order_id=None, portfolio_id=None):
        self.user = user
        self.screen = screen
        self.task_order_id = task_order_id
        self._task_order = None
        self.portfolio_id = portfolio_id
        self._portfolio = None
        self._section = TASK_ORDER_SECTIONS[screen - 1]
        self._form = None

    @property
    def task_order(self):
        if not self._task_order and self.task_order_id:
            self._task_order = TaskOrders.get(self.user, self.task_order_id)

        return self._task_order

    @property
    def portfolio(self):
        if not self._portfolio:
            if self.task_order:
                self._portfolio = self.task_order.portfolio
            elif self.portfolio_id:
                self._portfolio = Portfolios.get(self.user, self.portfolio_id)

        return self._portfolio

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
            self._form = self._section[form_type](obj=self.task_order)
            # manually set SelectMultipleFields
            if self._section["section"] == "app_info":
                self._form.complexity.data = self.task_order.complexity
                self._form.dev_team.data = self.task_order.dev_team
            elif self._section["section"] == "oversight":
                if self.user.dod_id == self.task_order.cor_dod_id:
                    self._form.am_cor.data = True
                if self.task_order.contracting_officer or self.task_order.ko_invite:
                    self._form.ko_invite.data = True
                if (
                    self.task_order.contracting_officer_representative
                    or self.task_order.cor_invite
                ):
                    self._form.cor_invite.data = True
                if self.task_order.security_officer or self.task_order.so_invite:
                    self._form.so_invite.data = True

        else:
            self._form = self._section[form_type]()

        if self.pf_attributes_read_only and self.screen == 1:
            self._form = task_order_form.AppInfoWithExistingPortfolioForm(
                obj=self.task_order
            )

        return self._form

    @property
    def template(self):
        return self._section["template"]

    @property
    def display_screens(self):
        screen_info = deepcopy(TASK_ORDER_SECTIONS)

        if self.task_order:
            for section in screen_info:
                section["completion"] = TaskOrders.section_completion_status(
                    self.task_order, section["section"]
                )

        return screen_info

    @property
    def is_complete(self):
        if self.task_order and TaskOrders.all_sections_complete(self.task_order):
            return True
        else:
            return False

    @property
    def pf_attributes_read_only(self):
        if self.task_order and self.portfolio.num_task_orders > 1:
            return True
        elif self.portfolio_id:
            return True
        else:
            return False


class UpdateTaskOrderWorkflow(ShowTaskOrderWorkflow):
    def __init__(
        self, user, form_data, screen=1, task_order_id=None, portfolio_id=None
    ):
        self.user = user
        self.form_data = form_data
        self.screen = screen
        self.task_order_id = task_order_id
        self.portfolio_id = portfolio_id
        self._task_order = None
        self._section = TASK_ORDER_SECTIONS[screen - 1]
        self._form = None

    @property
    def form(self):
        if not self._form:
            form_type = (
                "unclassified_form"
                if "unclassified_form" in self._section
                and not app.config.get("CLASSIFIED")
                else "form"
            )

            if self.pf_attributes_read_only and self.screen == 1:
                self._form = task_order_form.AppInfoWithExistingPortfolioForm(
                    self.form_data
                )
            else:
                self._form = self._section[form_type](
                    self.form_data, obj=self.task_order
                )

        return self._form

    @property
    def portfolio(self):
        if self.task_order:
            return self.task_order.portfolio

    @property
    def task_order_form_data(self):
        to_data = self.form.data.copy()
        if "portfolio_name" in to_data:
            to_data.pop("portfolio_name")
        if "defense_component" in to_data:
            to_data.pop("defense_component")

        # don't save other text in DB unless "other" is checked
        if "complexity" in to_data and "other" not in to_data["complexity"]:
            to_data["complexity_other"] = None
        if "dev_team" in to_data and "other" not in to_data["dev_team"]:
            to_data["dev_team_other"] = None

        if self.form_data.get("am_cor"):
            cor_data = {
                "cor_first_name": self.user.first_name,
                "cor_last_name": self.user.last_name,
                "cor_email": self.user.email,
                "cor_phone_number": self.user.phone_number,
                "cor_dod_id": self.user.dod_id,
                "cor_id": self.user.id,
            }
            to_data = {**to_data, **cor_data}

        return to_data

    def validate(self):
        return self.form.validate()

    def update(self):
        if self.task_order:
            if "portfolio_name" in self.form.data:
                new_name = self.form.data["portfolio_name"]
                old_name = self.task_order.portfolio_name
                if not new_name == old_name:
                    Portfolios.update(self.task_order.portfolio, {"name": new_name})
            TaskOrders.update(self.user, self.task_order, **self.task_order_form_data)
        else:
            if self.portfolio_id:
                pf = Portfolios.get(self.user, self.portfolio_id)
            else:
                pf = Portfolios.create(
                    self.user,
                    self.form.portfolio_name.data,
                    self.form.defense_component.data,
                )
            self._task_order = TaskOrders.create(portfolio=pf, creator=self.user)
            TaskOrders.update(self.user, self.task_order, **self.task_order_form_data)

        return self.task_order


@task_orders_bp.route("/task_orders/new/get_started")
def get_started():
    return render_template("task_orders/new/get_started.html")  # pragma: no cover


@task_orders_bp.route("/task_orders/new/<int:screen>")
@task_orders_bp.route("/task_orders/new/<int:screen>/<task_order_id>")
@task_orders_bp.route("/portfolios/<portfolio_id>/task_orders/new/<int:screen>")
def new(screen, task_order_id=None, portfolio_id=None):
    workflow = ShowTaskOrderWorkflow(
        g.current_user, screen, task_order_id, portfolio_id
    )
    template_args = {
        "current": screen,
        "task_order_id": task_order_id,
        "screens": workflow.display_screens,
        "form": workflow.form,
        "complete": workflow.is_complete,
    }

    if task_order_id and screen is 4:
        if not TaskOrders.all_sections_complete(workflow.task_order):
            flash("task_order_draft")

    if workflow.pf_attributes_read_only:
        template_args["portfolio"] = workflow.portfolio

    url_args = {"screen": screen}
    if task_order_id:
        url_args["task_order_id"] = task_order_id
    else:
        url_args["portfolio_id"] = portfolio_id

    if workflow.task_order:
        template_args["task_order"] = workflow.task_order
        if http_request.args.get("ko_edit"):
            template_args["ko_edit"] = True
            template_args["next"] = url_for(
                "portfolios.ko_review",
                portfolio_id=workflow.task_order.portfolio.id,
                task_order_id=task_order_id,
            )
            url_args["next"] = template_args["next"]

    template_args["action_url"] = url_for("task_orders.update", **url_args)

    return render_template(workflow.template, **template_args)


@task_orders_bp.route("/task_orders/new/<int:screen>", methods=["POST"])
@task_orders_bp.route("/task_orders/new/<int:screen>/<task_order_id>", methods=["POST"])
@task_orders_bp.route(
    "/portfolios/<portfolio_id>/task_orders/new/<int:screen>", methods=["POST"]
)
def update(screen, task_order_id=None, portfolio_id=None):
    form_data = {**http_request.form, **http_request.files}
    workflow = UpdateTaskOrderWorkflow(
        g.current_user, form_data, screen, task_order_id, portfolio_id
    )

    if workflow.validate():
        workflow.update()
        if http_request.args.get("next"):
            redirect_url = http_request.args.get("next")
        else:
            redirect_url = url_for(
                "task_orders.new",
                screen=screen + 1,
                task_order_id=workflow.task_order.id,
            )
        return redirect(redirect_url)
    else:
        return render_template(
            workflow.template,
            current=screen,
            task_order_id=task_order_id,
            portfolio_id=portfolio_id,
            screens=workflow.display_screens,
            form=workflow.form,
        )
