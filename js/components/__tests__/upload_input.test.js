import { mount } from '@vue/test-utils'

import uploadinput from '../upload_input'

import { makeTestWrapper } from '../../test_utils/component_test_helpers'

const UploadWrapper = makeTestWrapper({
  components: { uploadinput },
  templatePath: 'upload_input_template.html',
  data: function() {
    return { initialvalue: this.initialData.initialvalue, token: this.token }
  }
})

const UploadErrorWrapper = makeTestWrapper({
  components: { uploadinput },
  templatePath: 'upload_input_error_template.html',
  data: function() {
    return { initialvalue: null, token: null }
  }
})

describe('UploadInput Test', () => {
  it('should show input and button when no attachment present', () => {
    const wrapper = mount(UploadWrapper, {
      propsData: {
        initialData: { initialvalue: null, token: "token" },
      },
    })

    const fileInput = wrapper.find('input[type=file]').element
    expect(fileInput).not.toBe(undefined)
  })

  it('should show file name and hide input', () => {
    const wrapper = mount(UploadWrapper, {
      propsData: {
        initialData: { initialvalue: "somepdf.pdf", token: "token" }
      },
    })

    const fileInput = wrapper.find('input[type=file]').element
    const fileNameSpan = wrapper.find('.uploaded-file__name')

    expect(fileInput).toBe(undefined)
    expect(fileNameSpan.html()).toContain('somepdf.pdf')
  })

  it('should correctly display error treatment', () => {
    const wrapper = mount(UploadErrorWrapper, {
      propsData: {
        initialData: { initialvalue: "somepdf.pdf", token: "token" }
      }
    })

    const messageArea = wrapper.find('.usa-input__message')
    expect(messageArea.html()).toContain('Test Error Message')
  })
})
