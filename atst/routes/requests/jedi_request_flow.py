from collections import defaultdict

from atst.domain.requests import Requests
from atst.forms.request import RequestForm
from atst.forms.org import OrgForm
from atst.forms.poc import POCForm
from atst.forms.review import ReviewForm


class JEDIRequestFlow(object):
    def __init__(
        self,
        current_step,
        current_user=None,
        request=None,
        post_data=None,
        request_id=None,
        existing_request=None,
    ):
        self.current_step = current_step

        self.current_user = current_user
        self.request = request

        self.post_data = post_data
        self.is_post = self.post_data is not None

        self.request_id = request_id
        self.form = self._form()

        self.existing_request = existing_request

    def _form(self):
        if self.is_post:
            return self.form_class()(self.post_data)
        else:
            return self.form_class()(data=self.current_step_data)

    def validate(self):
        return self.form.validate()

    def validate_warnings(self):
        existing_request_data = (
            self.existing_request and self.existing_request.body.get(self.form_section)
        ) or None

        valid = self.form.perform_extra_validation(existing_request_data)
        return valid

    @property
    def current_screen(self):
        return self.screens[self.current_step - 1]

    @property
    def form_section(self):
        return self.current_screen["section"]

    def form_class(self):
        return self.current_screen["form"]

    # maps user data to fields in OrgForm; this should be moved into the
    # request initialization process when we have a request schema, or we just
    # shouldn't record this data on the request
    def map_user_data(self, user):
        return {
            "fname_request": user.first_name,
            "lname_request": user.last_name,
            "email_request": user.email
        }

    @property
    def current_step_data(self):
        data = {}

        if self.is_post:
            data = self.post_data

        if self.request:
            if self.form_section == "review_submit":
                data = self.request.body
            elif self.form_section == "information_about_you":
                form_data = self.request.body.get(self.form_section, {})
                data = { **self.map_user_data(self.request.creator), **form_data }
            else:
                data = self.request.body.get(self.form_section, {})
        elif self.form_section == "information_about_you":
            data = self.map_user_data(self.current_user)

        return defaultdict(lambda: defaultdict(lambda: None), data)

    @property
    def can_submit(self):
        return self.request and Requests.should_allow_submission(self.request)

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
            },
            {
                "title": "Information About You",
                "section": "information_about_you",
                "form": OrgForm,
            },
            {
                "title": "Workspace Owner",
                "section": "primary_poc",
                "form": POCForm,
            },
            {
                "title": "Review & Submit",
                "section": "review_submit",
                "form": ReviewForm,
            },
        ]

    def create_or_update_request(self):
        request_data = {self.form_section: self.form.data}
        if self.request_id:
            Requests.update(self.request_id, request_data)
        else:
            request = Requests.create(self.current_user, request_data)
            self.request_id = request.id
