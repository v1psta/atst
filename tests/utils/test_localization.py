import pytest
from atst.utils.localization import (
    translate,
    load_cached_translations_file,
    LocalizationInvalidKeyError,
)


def test_loading_cached_translations_file_returns_the_file_contents():
    file_name = "translations.yaml"
    assert load_cached_translations_file(file_name) == open(file_name).read()


def test_looking_up_existing_key():
    assert translate("testing.example_string") == "Hello World"


def test_nested_keys():
    assert translate("testing.nested.example") == "Hello nested example"


def test_with_variables():
    assert (
        translate("testing.example_with_variables", {"name": "Alice"})
        == "Hello, Alice!"
    )

    assert translate("testing.example_with_variables", {"name": "Bob"}) == "Hello, Bob!"


def test_looking_up_non_existent_key():
    with pytest.raises(LocalizationInvalidKeyError):
        translate("testing.an.invalid_key")
