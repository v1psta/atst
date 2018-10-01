def test_can_get_title(live_app, ie10_driver):
    ie10_driver.get(live_app.server_url)
    assert "JEDI" in ie10_driver.title
