export default {
  name: 'confirmation-popover',

  props: {
    action: String,
    btn_text: String,
    btn_icon: String,
    btn_class: String,
    cancel_btn_text: String,
    confirm_btn_text: String,
    confirm_msg: String,
    csrf_token: String,
    name: String,
  },

  template: `
    <v-popover placement='top-start'>
      <template slot="popover">
        <p>{{ confirm_msg }}</p>
        <div class='action-group'>
          <form method="POST" v-bind:action="action">
            <input id="csrf_token" name="csrf_token" type="hidden" v-bind:value="csrf_token">
            <button class='usa-button usa-button-primary' type='submit'>
              {{ confirm_btn_text }}
            </button>
          </form>
          <button class='usa-button usa-button-secondary' v-close-popover>
            {{ cancel_btn_text }}
          </button>
        </div>
      </template>
      <button class="tooltip-target" v-bind:class="[btn_class]" type="button">
        <div v-html="btn_icon" />
        {{ btn_text }}
      </button>
    </v-popover>
  `,
}
