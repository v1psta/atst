from flask import Blueprint, g, render_template, url_for, redirect, request
import pendulum
from collections import defaultdict

from atst.domain.requests import Requests
from atst.forms.financial import FinancialForm
from atst.forms.request import RequestForm
from atst.forms.org import OrgForm
from atst.forms.poc import POCForm
from atst.forms.review import ReviewForm


requests_bp = Blueprint("requests", __name__)

def map_request(user, request):
    time_created = pendulum.instance(request.time_created)
    is_new = time_created.add(days=1) > pendulum.now()

    return {
        "order_id": request.id,
        "is_new": is_new,
        "status": request.status,
        "app_count": 1,
        "date": time_created.format("M/DD/YYYY"),
        "full_name": "{} {}".format(user["first_name"], user["last_name"]),
    }


@requests_bp.route("/requests", methods=["GET"])
def requests_index():
    requests = []
    if "review_and_approve_jedi_workspace_request" in g.current_user["atat_permissions"]:
        requests = Requests.get_many()
    else:
        requests = Requests.get_many(creator_id=g.current_user["id"])

    mapped_requests = [map_request(g.current_user, r) for r in requests]

    return render_template("requests.html", requests=mapped_requests)


@requests_bp.route("/requests/new/<int:screen>", methods=["GET"])
def requests_form_new():
    pass


@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["GET"])
def requests_form_update(screen=1, request_id=None):
    request = Requests.get(request_id) if request_id is not None else None
    jedi_flow = JEDIRequestFlow(screen, request, request_id=request_id)

    return render_template(
        "requests/screen-%d.html" % int(screen),
        f=jedi_flow.form,
        data=jedi_flow.current_step_data,
        screens=jedi_flow.screens,
        current=screen,
        next_screen=screen + 1,
        request_id=request_id,
        can_submit=jedi_flow.can_submit
    )

@requests_bp.route("/requests/new/<int:screen>/<string:request_id>", methods=["POST"])
def requests_update(screen=1, request_id=None):
    screen = int(screen)
    post_data = str(request.data)
    current_user = g.current_user
    existing_request = Requests.get(request_id) if request_id is not None else None
    jedi_flow = JEDIRequestFlow(
        screen,
        post_data=post_data,
        request_id=request_id,
        current_user=current_user,
        existing_request=existing_request,
    )

    rerender_args = dict(
        f=jedi_flow.form,
        data=post_data,
        screens=jedi_flow.screens,
        current=screen,
        next_screen=jedi_flow.next_screen,
        request_id=jedi_flow.request_id,
    )

    if jedi_flow.validate():
        jedi_flow.create_or_update_request()
        valid = jedi_flow.validate_warnings()
        if valid:
            if jedi_flow.next_screen > len(jedi_flow.screens):
                where = "/requests"
            else:
                where = url_for(
                    "requests.requests_Form_update", screen=jedi_flow.next_screen, request_id=jedi_flow.request_id
                )
            return redirect(where)
        else:
            return render_template(
                "requests/screen-%d.html" % int(screen),
                **rerender_args
            )
    else:
        return render_template(
            "requests/screen-%d.html" % int(screen),
            **rerender_args
        )




@requests_bp.route("/requests/verify/<string:request_id>", methods=["GET"])
def financial_verification(request_id=None):
    request = Requests.get(request_id)
    form = FinancialForm(data=request.body.get('financial_verification'))
    return render_template("requests/financial_verification.html", f=form)


@requests_bp.route("/requests/verify/<string:request_id>", methods=["POST"])
def update_financial_verification():
    pass


class JEDIRequestFlow(object):
    def __init__(
        self,
        current_step,
        request=None,
        post_data=None,
        request_id=None,
        current_user=None,
        existing_request=None,
    ):
        self.current_step = current_step
        self.request = request

        self.post_data = post_data
        self.is_post = self.post_data is not None

        self.request_id = request_id
        self.form = self._form()

        self.current_user = current_user
        self.existing_request = existing_request

    def _form(self):
        if self.is_post:
            return self.form_class()(self.post_data)
        elif self.request:
            return self.form_class()(data=self.current_step_data)
        else:
            return self.form_class()()

    def validate(self):
        return self.form.validate()

    def validate_warnings(self):
        existing_request_data = (
            self.existing_request
            and self.existing_request.body.get(self.form_section)
        ) or None

        valid = self.form.perform_extra_validation(
            existing_request_data,
        )
        return valid

    @property
    def current_screen(self):
        return self.screens[self.current_step - 1]

    @property
    def form_section(self):
        return self.current_screen["section"]

    def form_class(self):
        return self.current_screen["form"]

    @property
    def current_step_data(self):
        data = {}

        if self.is_post:
            data = self.post_data

        if self.request:
            if self.form_section == "review_submit":
                data = self.request.body
            else:
                data = self.request.body.get(self.form_section, {})

        return defaultdict(lambda: defaultdict(lambda: 'Input required'), data)

    @property
    def can_submit(self):
        return self.request and self.request.status != "incomplete"

    @property
    def next_screen(self):
        return self.current_step + 1

    @property
    def screens(self):
        return [
            {
                "title": "Details of Use",
                "section": "details_of_use",
                "form": RequestForm,
                "subitems": [
                    {
                        "title": "Overall request details",
                        "id": "overall-request-details",
                    },
                    {"title": "Cloud Resources", "id": "cloud-resources"},
                    {"title": "Support Staff", "id": "support-staff"},
                ],
                "show": True,
            },
            {
                "title": "Information About You",
                "section": "information_about_you",
                "form": OrgForm,
                "show": True,
            },
            {
                "title": "Primary Point of Contact",
                "section": "primary_poc",
                "form": POCForm,
                "show": True,
            },
            {
                "title": "Review & Submit",
                "section": "review_submit",
                "form": ReviewForm,
                "show":True,
            },
        ]

    def create_or_update_request(self):
        request_data = {
            self.form_section: self.form.data
        }
        if self.request_id:
            Requests.update(request_id, request_data)
        else:
            request = Requests.create(self.current_user["id"], request_data)
            self.request_id = request.id
