import pendulum
from copy import deepcopy
from wtforms.fields.html5 import DateField, EmailField, TelField
from wtforms.fields import RadioField, StringField, SelectMultipleField, FieldList, BooleanField, FormField
from wtforms.validators import Email, DataRequired, Optional
from wtforms.widgets import ListWidget, CheckboxInput, TextInput

from .fields import SelectField
from .forms import CacheableForm
from .data import SERVICE_BRANCHES
from atst.models.user import User

from .validators import Name, DateRange, PhoneNumber

class MultiCheckboxField(SelectMultipleField):
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()


USER_FIELDS = {
    "first_name": StringField("First Name", validators=[Name()]),
    "last_name": StringField("Last Name", validators=[Name()]),
    "email": EmailField(
        "E-mail Address",
        description="Enter your preferred contact e-mail address",
        validators=[Email()],
    ),
    "phone_number": TelField("Phone Number", validators=[PhoneNumber()]),
    "phone_ext": StringField("Extension"),
    "service_branch": SelectField(
        "Service Branch or Agency",
        description="Which service or organization do you belong to within the DoD?",
        choices=SERVICE_BRANCHES,
    ),
    "citizenship": RadioField(
        description="What is your citizenship status?",
        choices=[
            ("United States", "United States"),
            ("Foreign National", "Foreign National"),
            ("Other", "Other"),
        ],
    ),
    # "animals": FieldList(
    #     SelectMultipleField(
    #         "I am a:",
    #         description="Please select the type of animals you are",
    #         choices=[
    #             ("cat", "Cat"),
    #             ("dog", "Dog"),
    #             ('horse', 'Horse')
    #         ],
    #         widget=ListWidget(prefix_label=False),
    #         option_widget=CheckboxInput()
    #     ),
    # ),
    "animals": SelectMultipleField(
        "I am a:",
        description="Please select the type of animals you are",
        choices=[
            ("cat", "Cat"),
            ("dog", "Dog"),
            ("human", "Human"),
        ],
        widget=ListWidget(prefix_label=False),
        option_widget=CheckboxInput()
    ),
    "other": BooleanField(
        "I am something else!",
        default=False,
        false_values=(False, "false", "False", "no", ""),
    ),
    "animals_other": StringField(
        "Other animal",
        description="What are you????",
    ),
    "designation": RadioField(
        "Designation of Person",
        description="What is your designation within the DoD?",
        choices=[
            ("military", "Military"),
            ("civilian", "Civilian"),
            ("contractor", "Contractor"),
        ],
    ),
    "date_latest_training": DateField(
        "Latest Information Assurance (IA) Training Completion Date",
        description='To complete the training, you can find it in <a class="icon-link" href="https://iatraining.disa.mil/eta/disa_cac2018/launchPage.htm" target="_blank">Information Assurance Cyber Awareness Challange</a> website.',
        validators=[
            DateRange(
                lower_bound=pendulum.duration(years=1),
                upper_bound=pendulum.duration(days=0),
                message="Must be a date within the last year.",
            )
        ],
        format="%m/%d/%Y",
    ),
}


def inherit_field(unbound_field, required=True):
    kwargs = deepcopy(unbound_field.kwargs)
    if not "validators" in kwargs:
        kwargs["validators"] = []

    if required:
        kwargs["validators"].append(DataRequired())
    else:
        kwargs["validators"].append(Optional())

    return unbound_field.field_class(*unbound_field.args, **kwargs)


def inherit_user_field(field_name):
    required = field_name in User.REQUIRED_FIELDS
    return inherit_field(USER_FIELDS[field_name], required=required)


class AnimalsForm(CacheableForm):
    # create sub form that contains all of the fields we want
    # then use FieldList to compile them all into one field in the form?
    # can combine, but not rendering
    # having issue w/ other
    animals = inherit_user_field("animals")
    other = inherit_user_field("other")
    animals_other = inherit_user_field("animals_other")


class EditUserForm(CacheableForm):

    first_name = inherit_user_field("first_name")
    last_name = inherit_user_field("last_name")
    email = inherit_user_field("email")
    phone_number = inherit_user_field("phone_number")
    phone_ext = inherit_user_field("phone_ext")
    service_branch = inherit_user_field("service_branch")
    citizenship = inherit_user_field("citizenship")
    # animals_form = FieldList(FormField(AnimalsForm))
    animals = inherit_user_field("animals")
    other = inherit_user_field("other")
    animals_other = inherit_user_field("animals_other")
    designation = inherit_user_field("designation")
    date_latest_training = inherit_user_field("date_latest_training")
