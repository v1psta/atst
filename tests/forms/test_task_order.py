from atst.forms.task_order import CLINForm
from atst.models import JEDICLINType

import tests.factories as factories


def test_clin_form_jedi_clin_type():
    jedi_type = JEDICLINType.JEDI_CLIN_2
    clin = factories.CLINFactory.create(jedi_clin_type=jedi_type)
    clin_form = CLINForm(obj=clin)
    assert clin_form.jedi_clin_type.data == jedi_type.value
