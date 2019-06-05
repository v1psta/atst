import DateSelector from './date_selector'
import optionsinput from './options_input'
import textinput from './text_input'

export default {
  name: 'clin-fields',

  components: {
    DateSelector,
    optionsinput,
    textinput,
  },

  props: {
    clinIndex: String,
  },
  // get clin index from props and pass into template
  template: `
    <div>
      <optionsinput name="clins-0-jedi_clin_type">
      </optionsinput>
      <div class="  usa-input usa-input--validation--anything usa-input--success">
        <label for="clins-0-number">
          <div class="usa-input__title"> Number </div>
        </label>
        <input type="text" id="clins-0-number" placeholder="">
        <input type="hidden" name="clins-0-number" value="123">
      </div>
      <fieldset class="usa-input date-picker">
        <legend>
          <div class="usa-input__title"> Start Date
          </div>
        </legend>
        <div class="date-picker-component">
          <input name="clins-0-start_date" type="hidden">
          <div class="usa-form-group usa-form-group-month">
            <label>Month
            </label>
            <input name="date-month" max="12" maxlength="2" min="1" type="number" class="">
          </div>
          <div class="usa-form-group usa-form-group-day">
            <label>Day
            </label>
            <input name="date-day" maxlength="2" min="1" type="number" max="31" class="">
          </div>
          <div class="usa-form-group usa-form-group-year">
            <label>Year
            </label>
            <input id="date-year" maxlength="4" type="number">
          </div>
          <!---->
        </div>
        <p class="usa-input-error-message">
        </p>
      </fieldset>
      <fieldset class="usa-input date-picker">
        <legend>
          <div class="usa-input__title"> End Date
          </div>
        </legend>
        <div class="date-picker-component">
          <input name="clins-0-end_date" type="hidden">
          <div class="usa-form-group usa-form-group-month">
            <label>Month
            </label>
            <input name="date-month" max="12" maxlength="2" min="1" type="number" class="">
          </div>
          <div class="usa-form-group usa-form-group-day">
            <label>Day
            </label>
            <input name="date-day" maxlength="2" min="1" type="number" max="31" class="">
          </div>
          <div class="usa-form-group usa-form-group-year">
            <label>Year
            </label>
            <input id="date-year" maxlength="4" type="number">
          </div>
          <!---->
        </div>
        <p class="usa-input-error-message">
        </p>
      </fieldset>
      <div class="  usa-input usa-input--validation--anything">
        <label for="clins-0-obligated_amount">
          <div class="usa-input__title"> Obligated Amount
          </div>
        </label>
        <input type="text" id="clins-0-obligated_amount" placeholder="">
        <input type="hidden" name="clins-0-obligated_amount">
      </div>
    </div>`,
}
