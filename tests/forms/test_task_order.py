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
    assert (
        translate("forms.task_order.pop_errors.date_order")
        in clin_form.start_date.errors
    )
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
        translate(
            "forms.task_order.pop_errors.start",
            {"date": CONTRACT_START_DATE.strftime("%b %d, %Y")},
        )
    ) in clin_form.start_date.errors
    assert (
        translate(
            "forms.task_order.pop_errors.end",
            {"date": CONTRACT_END_DATE.strftime("%b %d, %Y")},
        )
    ) in clin_form.end_date.errors

    valid_start = CONTRACT_START_DATE + relativedelta(months=1)
    valid_end = CONTRACT_END_DATE - relativedelta(months=1)
    valid_clin = factories.CLINFactory.create(
        start_date=valid_start, end_date=valid_end
    )
    valid_clin_form = CLINForm(obj=valid_clin)
    assert valid_clin_form.validate()


def test_clin_form_obligated_greater_than_total():
    invalid_clin = factories.CLINFactory.create(
        total_amount=0,
        obligated_amount=1,
        start_date=datetime.date(2019, 9, 15),
        end_date=datetime.date(2020, 9, 14),
    )
    invalid_clin_form = CLINForm(obj=invalid_clin)
    assert not invalid_clin_form.validate()
    assert (
        translate("forms.task_order.clin_funding_errors.obligated_amount_error")
    ) in invalid_clin_form.obligated_amount.errors


def test_clin_form_dollar_amounts_out_of_range():
    invalid_clin = factories.CLINFactory.create(
        total_amount=-1,
        obligated_amount=1000000001,
        start_date=datetime.date(2019, 9, 15),
        end_date=datetime.date(2020, 9, 14),
    )
    invalid_clin_form = CLINForm(obj=invalid_clin)
    assert not invalid_clin_form.validate()
    assert (
        translate("forms.task_order.clin_funding_errors.funding_range_error")
    ) in invalid_clin_form.total_amount.errors
    assert (
        translate("forms.task_order.clin_funding_errors.funding_range_error")
    ) in invalid_clin_form.obligated_amount.errors
