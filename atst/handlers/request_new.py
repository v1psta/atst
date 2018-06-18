import tornado
from atst.handler import BaseHandler
from atst.forms.request import RequestForm
from atst.forms.organization_info import OrganizationInfoForm
from atst.forms.funding import FundingForm
from atst.forms.readiness import ReadinessForm
from atst.forms.review import ReviewForm
import tornado.httputil


class RequestNew(BaseHandler):
    screens = [
            { 'title' : 'Details of Use',
              'form'  : RequestForm,
              'subitems' : [
                {'title' : 'Application Details',
                 'id' : 'application-details'},
                {'title' : 'Computation',
                  'id' : 'computation' },
                {'title' : 'Storage',
                  'id' : 'storage' },
                {'title' : 'Usage',
                  'id' : 'usage' },
            ]},
            {
                'title' : 'Organizational Info',
                'form'  : OrganizationInfoForm,
            },
            {
                'title' : 'Funding/Contracting',
                'form'  : FundingForm,
            },
            {
                'title' : 'Readiness Survey',
                'form'  : ReadinessForm,
            },
            {
                'title' : 'Review & Submit',
                'form'  : ReviewForm,
            }
     ]

    def initialize(self, page, requests_client):
        self.page = page
        self.requests_client = requests_client

    @tornado.web.authenticated
    @tornado.gen.coroutine
    def post(self, screen = 1):
        self.check_xsrf_cookie()
        screen = int(screen)
        form = self.screens[ screen - 1 ]['form'](self.request.arguments)
        if form.validate():
            response = yield self.create_or_update_request(form.data)
            if response.ok:
                where = self.application.default_router.reverse_url('request_form', str(screen + 1))
                self.redirect(where)
            else:
                self.set_status(response.code)
        else:
            self.show_form(screen, form)

    @tornado.web.authenticated
    def get(self, screen = 1):
        self.show_form(screen=screen)

    def show_form(self, screen = 1, form = None):
        if not form:
            form = self.screens[ int(screen) - 1 ]['form'](self.request.arguments)
        self.render( 'requests/screen-%d.html.to' % int(screen),
                    f = form,
                    page = self.page,
                    screens = self.screens,
                    current = int(screen),
                    next_screen = int(screen) + 1 )

    @tornado.gen.coroutine
    def create_or_update_request(self, form_data):
        # TODO: Check session for existing form, and send a PATCH instead if it exists.
        request_data = {
            'creator_id': '9cb348f0-8102-4962-88c4-dac8180c904c',
            'request': form_data
        }
        response = yield self.requests_client.post('/requests', json=request_data)
        return response
