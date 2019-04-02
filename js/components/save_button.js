export default {
  name: 'savebutton',

  props: {
    text: String,
    disabled: Boolean,
    classes: String,
  },

  data: function() {
    return {
      displayClasses: `usa-button usa-button-primary ${this.classes}`,
    }
  },

  template:
    '<button type="submit" :class="displayClasses" tabindex="0" :disabled="disabled">{{ text }}</button>',
}
