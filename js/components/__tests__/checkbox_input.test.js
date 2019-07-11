import { mount } from '@vue/test-utils'

import Vue from 'vue'

import checkboxinput from '../checkbox_input'

const fs = require('fs')
const testTemplate = fs.readFileSync('js/test_templates/checkbox_input_template.html', 'utf-8')
console.log(testTemplate)
const template = `
    <div>
      <div class='usa-input'>
        <fieldset data-ally-disabled="true" v-on:change="onInput" class="usa-input__choices">
          <legend>
            <input type="checkbox" v-model="isChecked"></input>
            Some words about this checkbox
          </legend>
        </fieldset>
      </div>
    </div>
`

// const templatedCheckboxInput = {
//     ...checkboxinput,
//     template
// }

// Define test wrapping component
// Use test template for wrapping component template
// Inject component under test (checkboxInput) into wrapping component??

const WrapperComponent = {
    name: 'WrapperComponent',
    components: { checkboxinput },
    template: testTemplate,
    data: function () {
        return {
            name: 'testCheck',
            initialChecked: true
        }
    }
}

describe('CheckboxInput Renders Correctly', () => {
    it('Should initialize checked', () => {
        const wrapper = mount(WrapperComponent, {
            propsData: {
                name: 'testCheck',
                initialChecked: true
            }
        })

        wrapper.vm.$children[0].$data.isChecked = true

        expect(wrapper.find('.usa-input input').element.checked).toBe(true)
    })

    it('Should initialize unchecked', () => {
        const wrapper = mount(WrapperComponent, {
            propsData: {
                name: 'testCheck',
                initialChecked: false
            }
        })

        expect(wrapper.find('.usa-input input').element.checked).toBe(false)
    })
})
