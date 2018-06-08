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

    def initialize(self, page):
        self.page = page

    @tornado.web.authenticated
    def post(self, screen = 1):
        self.check_xsrf_cookie()
        screen = int(screen)
        form = self.screens[ screen - 1 ]['form'](self.request.arguments)
        print( 'data---------' )
        print( form.data )
        if form.validate():
            where=self.application.default_router.reverse_url('request_form', str(screen + 1))
            self.redirect(where)
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
