import pytest
from wtforms import Form

from atst.forms.task_order import AppInfoForm

def test_complexity():
    form  = AppInfoForm(formdata={"complexity":["other", "not_sure", "storage"]})

    assert form.data["complexity"] == ["other", "not_sure", "storage"]
