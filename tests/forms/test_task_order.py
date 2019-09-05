import datetime
from dateutil.relativedelta import relativedelta
from flask import current_app as app

from atst.forms.task_order import CLINForm
from atst.models import JEDICLINType
from atst.utils.localization import translate

import tests.factories as factories


def test_clin_form_jedi_clin_type():
    jedi_type = JEDICLINType.JEDI_CLIN_2
    clin = factories.CLINFactory.create(jedi_clin_type=jedi_type)
    clin_form = CLINForm(obj=clin)
    assert clin_form.jedi_clin_type.data == jedi_type.value


def test_clin_form_start_date_before_end_date():
    invalid_start = datetime.date(2020, 12, 12)
    invalid_end = datetime.date(2020, 1, 1)
    invalid_clin = factories.CLINFactory.create(
        start_date=invalid_start, end_date=invalid_end
    )
    clin_form = CLINForm(obj=invalid_clin)
    assert not clin_form.validate()
    assert translate("forms.task_order.start_date_error") in clin_form.start_date.errors
    valid_start = datetime.date(2020, 1, 1)
    valid_end = datetime.date(2020, 12, 12)
    valid_clin = factories.CLINFactory.create(
        start_date=valid_start, end_date=valid_end
    )
    valid_clin_form = CLINForm(obj=valid_clin)
    assert valid_clin_form.validate()


def test_clin_form_pop_dates_within_contract_dates():
    CONTRACT_START_DATE = datetime.datetime.strptime(
        app.config.get("CONTRACT_START_DATE"), "%Y-%m-%d"
    ).date()
    CONTRACT_END_DATE = datetime.datetime.strptime(
        app.config.get("CONTRACT_END_DATE"), "%Y-%m-%d"
    ).date()

    invalid_start = CONTRACT_START_DATE - relativedelta(months=1)
    invalid_end = CONTRACT_END_DATE + relativedelta(months=1)
    invalid_clin = factories.CLINFactory.create(
        start_date=invalid_start, end_date=invalid_end
    )
    clin_form = CLINForm(obj=invalid_clin)
    assert not clin_form.validate()
    assert (
        "PoP start date must be on or after {}.".format(CONTRACT_START_DATE)
    ) in clin_form.start_date.errors
    assert (
        "PoP end date must be before or on {}.".format(CONTRACT_END_DATE)
    ) in clin_form.end_date.errors

    valid_start = CONTRACT_START_DATE + relativedelta(months=1)
    valid_end = CONTRACT_END_DATE - relativedelta(months=1)
    valid_clin = factories.CLINFactory.create(
        start_date=valid_start, end_date=valid_end
    )
    valid_clin_form = CLINForm(obj=valid_clin)
    assert valid_clin_form.validate()
