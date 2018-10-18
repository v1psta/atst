from wtforms.validators import ValidationError
import pytest

from atst.forms.validators import Alphabet, IsNumber, PhoneNumber, ListItemsUnique


class TestIsNumber:
    @pytest.mark.parametrize("valid", ["0", "12", "-12"])
    def test_IsNumber_accepts_integers(self, valid, dummy_form, dummy_field):
        validator = IsNumber()
        dummy_field.data = valid
        validator(dummy_form, dummy_field)

    @pytest.mark.parametrize("invalid", ["12.1", "two", ""])
    def test_IsNumber_rejects_anything_else(self, invalid, dummy_form, dummy_field):
        validator = IsNumber()
        dummy_field.data = invalid
        with pytest.raises(ValidationError):
            validator(dummy_form, dummy_field)


class TestPhoneNumber:
    @pytest.mark.parametrize("valid", ["12345", "1234567890", "(123) 456-7890"])
    def test_PhoneNumber_accepts_valid_numbers(self, valid, dummy_form, dummy_field):
        validator = PhoneNumber()
        dummy_field.data = valid
        validator(dummy_form, dummy_field)

    @pytest.mark.parametrize(
        "invalid", ["1234", "123456", "1234567abc", "(123) 456-789012"]
    )
    def test_PhoneNumber_rejects_invalid_numbers(
        self, invalid, dummy_form, dummy_field
    ):
        validator = PhoneNumber()
        dummy_field.data = invalid
        with pytest.raises(ValidationError):
            validator(dummy_form, dummy_field)


class TestAlphabet:
    @pytest.mark.parametrize("valid", ["a", "abcde", "hi mark", "cloud9", "niña"])
    def test_Alphabet_accepts_letters(self, valid, dummy_form, dummy_field):
        validator = Alphabet()
        dummy_field.data = valid
        validator(dummy_form, dummy_field)

    @pytest.mark.parametrize("invalid", [""])
    def test_Alphabet_rejects_non_letters(self, invalid, dummy_form, dummy_field):
        validator = Alphabet()
        dummy_field.data = invalid
        with pytest.raises(ValidationError):
            validator(dummy_form, dummy_field)


class TestListItemsUnique:
    @pytest.mark.parametrize("valid", [["a", "aa", "aaa"], ["one", "two", "three"]])
    def test_ListItemsUnique_allows_unique_items(self, valid, dummy_form, dummy_field):
        validator = ListItemsUnique()
        dummy_field.data = valid
        validator(dummy_form, dummy_field)

    @pytest.mark.parametrize(
        "invalid", [["a", "a", "a"], ["one", "two", "two", "three"]]
    )
    def test_ListItemsUnique_rejects_duplicate_names(
        self, invalid, dummy_form, dummy_field
    ):
        validator = ListItemsUnique()
        dummy_field.data = invalid
        with pytest.raises(ValidationError):
            validator(dummy_form, dummy_field)
