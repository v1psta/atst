const fs = require('fs')

/*
Jinja templates will be exported with a root node that is a custom tag mapped to a vue component
This wrapper allows us to mount the template and provide props. Props are provided by setting
values on in this wrapper's data function. The names returned by the data function must align
with the field names set in the template exporter script.

In the example below, initial-checked is set to a value 'initialchecked', so
'initialchecked' must be exported as a key from from the data function in order
to be passed as a prop to checkboxinput at mount time
<checkboxinput
    name='testVal'
    inline-template
    key='testVal'
    v-bind:initial-checked='initialvalue'
    >
*/
const makeTestWrapper = ({ components, templatePath, data }) => {
  const templateString = fs.readFileSync(
    `js/test_templates/${templatePath}`,
    'utf-8'
  )

  const WrapperComponent = {
    name: 'WrapperComponent',
    components,
    template: templateString,
    props: ['initialData'],
    data,
  }

  return WrapperComponent
}

export { makeTestWrapper }
