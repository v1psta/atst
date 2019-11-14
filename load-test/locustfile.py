import os
from random import choice, choices, randint
from urllib.parse import urlparse

from locust import HttpLocust, TaskSequence, seq_task

from pyquery import PyQuery as pq

# Provide username/password for basic auth
USERNAME = os.getenv("ATAT_BA_USERNAME", "")
PASSWORD = os.getenv("ATAT_BA_PASSWORD", "")

# Ability to disable SSL verification for bad cert situations
DISABLE_VERIFY = os.getenv("DISABLE_VERIFY", "true").lower() == "true"

# Alpha numerics for random entity names
LETTERS = "qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890"


def login(l):
    l.client.get("/login-dev", auth=(USERNAME, PASSWORD))


def logout(l):
    l.client.get("/logout")


def get_index(l):
    l.client.get("/")


def get_portfolios(l):
    response = l.client.get("/portfolios")
    d = pq(response.text)
    portfolio_links = [
        p.attr("href")
        for p in d(
            ".global-panel-container .atat-table tbody tr td:first-child a"
        ).items()
    ]
    force_new_portfolio = randint(0, 10) > 9
    if len(portfolio_links) == 0 or force_new_portfolio:
        portfolio_links += [create_portfolio(l)]

    l.locust.portfolio_links = portfolio_links


def get_portfolio(l):
    portfolio_link = choice(l.locust.portfolio_links)
    response = l.client.get(portfolio_link)
    d = pq(response.text)
    application_links = [
        p.attr("href")
        for p in d(".application-list .accordion__actions a:first-child").items()
    ]
    if len(application_links) > 0:
        portfolio_id = portfolio_link.split("/")[-2]
        update_app_registry(l, portfolio_id, application_links)


def update_app_registry(l, portfolio_id, app_links):
    if not hasattr(l.locust, "app_links"):
        l.locust.app_links = {}
    l.locust.app_links[portfolio_id] = app_links


def get_app(l):
    app_link = pick_app(l)
    force_new_app = randint(0, 10) > 9
    if app_link is not None and not force_new_app:
        l.client.get(app_link)
    else:
        portfolio_id = choice(l.locust.portfolio_links).split("/")[-2]
        update_app_registry(l, portfolio_id, create_new_app(l, portfolio_id))


def pick_app(l):
    if hasattr(l.locust, "app_links") and len(l.locust.app_links.items()) > 0:
        return choice(choice(list(l.locust.app_links.values())))


def create_new_app(l, portfolio_id):
    create_app_body = {
        "name": f"Load Test Created - {''.join(choices(LETTERS, k=5))}",
        "description": "Description",
    }

    create_app_url = f"/portfolios/{portfolio_id}/applications/new"

    create_app_response = l.client.post(create_app_url, create_app_body)

    application_id = create_app_response.url.split("/")[-3]

    create_environments_body = {
        "environment_names-0": "Development",
        "environment_names-1": "Testing",
        "environment_names-2": "Staging",
        "environment_names-3": "Production",
    }

    create_environments_url = (
        f"/applications/{application_id}/new/step_2?portfolio_id={portfolio_id}"
    )

    l.client.post(create_environments_url, create_environments_body)

    return f"/applications/{application_id}/settings"


def create_portfolio(l):
    new_portfolio_body = {
        "name": f"Load Test Created - {''.join(choices(LETTERS, k=5))}",
        "defense_component": "Army, Department of the",
        "description": "Test",
        "app_migration": "none",
        "native_apps": "yes",
        "complexity": "storage",
        "complexity_other": "",
        "dev_team": "civilians",
        "dev_team_other": "",
        "team_experience": "none",
    }

    response = l.client.post("/portfolios", new_portfolio_body)

    return urlparse(response.url).path


class UserBehavior(TaskSequence):
    def on_start(self):
        self.client.verify = not DISABLE_VERIFY
        login(self)

    @seq_task(1)
    def home(l):
        get_index(l)

    @seq_task(2)
    def portfolios(l):
        get_portfolios(l)

    @seq_task(3)
    def pick_a_portfolio(l):
        get_portfolio(l)

    @seq_task(4)
    def pick_an_app(l):
        get_app(l)

    def on_stop(self):
        logout(self)


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 3000
    max_wait = 9000


if __name__ == "__main__":
    # if run as the main file, will spin up a single locust
    WebsiteUser().run()

