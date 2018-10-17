# ATST

[![Build Status](https://travis-ci.org/dod-ccpo/atst.svg?branch=master)](https://travis-ci.org/dod-ccpo/atst)

## Description

This is the user-facing web application for ATAT.

## Installation

### System Requirements
ATST uses the [Scripts to Rule Them All](https://github.com/github/scripts-to-rule-them-all)
pattern for setting up and running the project. The scripts are located in the
`scripts` directory and use script fragments in the
[scriptz](https://github.com/dod-ccpo/scriptz) repository that are shared across
ATAT repositories.

Before running the setup scripts, a couple of dependencies need to be installed
locally:

* `python` == 3.6
  Python version 3.6 must be installed on your machine before installing `pipenv`.
  You can download Python 3.6 [from python.org](https://www.python.org/downloads/)
  or use your preferred system package manager.

* `pipenv`
  ATST requires `pipenv` to be installed for python dependency management. `pipenv`
  will create the virtual environment that the app requires. [See
  `pipenv`'s documentation for instructions on installing `pipenv](
  https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv).

* `postgres` >= 9.6
  ATST requires a PostgreSQL instance (>= 9.6) for persistence. Have PostgresSQL installed
  and running on the default port of 5432. You can verify that PostgresSQL is running
  by executing `psql` and ensuring that a connection is successfully made.

* `redis`
  ATST also requires a Redis instance for session management. Have Redis installed and
  running on the default port of 6379. You can ensure that Redis is running by
  executing `redis-cli` with no options and ensuring a connection is succesfully made.

* [`entr`](http://www.entrproject.org/)
  This dependency is optional. If present, the queue worker process will hot
  reload in development.

### Cloning
This project contains git submodules. Here is an example clone command that will
automatically initialize and update those modules:

    git clone --recurse-submodules git@github.com:dod-ccpo/atst.git

If you have an existing clone that does not yet contain the submodules, you can
set them up with the following command:

    git submodule update --init --recursive

### Setup
This application uses Pipenv to manage Python dependencies and a virtual
environment. Instead of the classic `requirements.txt` file, pipenv uses a
Pipfile and Pipfile.lock, making it more similar to other modern package managers
like yarn or mix.

To perform the installation, run the setup script:

    script/setup

The setup script creates the virtual environment, and then calls script/bootstrap
to install all of the Python and Node dependencies.

To enter the virtualenv manually (a la `source .venv/bin/activate`):

    pipenv shell

If you want to automatically load the virtual environment whenever you enter the
project directory, take a look at [direnv](https://direnv.net/).  An `.envrc`
file is included in this repository.  direnv will activate and deactivate
virtualenvs for you when you enter and leave the directory.


## Running (development)

To start the app locally in the foreground and watch for changes:

    script/server

After running `script/server`, the application is available at
[`http://localhost:8000`](http://localhost:8000).


### Users

There are currently six mock users for development:

- Sam (a CCPO)
- Amanda
- Brandon
- Christina
- Dominick
- Erica

To log in as one of them, navigate to `/login-dev?username=<lowercase name>`.
For example `/login-dev?username=amanda`.

In development mode, there is a `DEV Login` button available on the home page
that will automatically log you in as Amanda.

### Seeding the database

We have a helper script that will seed the database with requests, workspaces and
projects for all of the test users:

`pipenv run python script/seed_sample.py`

### Email Notifications

To send email, the following configuration values must be set:

```
MAIL_SERVER = <SMTP server URL>
MAIL_PORT = <SMTP server port>
MAIL_SENDER = <Login name for the email account and sender address>
MAIL_PASSWORD = <login password for the email account>
MAIL_TLS = <Boolean, whether TLS should be enabled for outgoing email. Defaults to false.>
```

When the `DEBUG` environment variable is enabled and the app environment is not
set to production, sent email messages are available at the `/messages` endpoint.
Emails are not sent in development and test modes.

## Testing

Tests require a test database:

```
createdb atat_test
```

To run lint, static analysis, and unit tests:

    script/test

To run only the unit tests:

    pipenv run python -m pytest

To re-run tests each time a file is changed:

    pipenv run ptw

### Selenium Tests

Selenium tests rely on BrowserStack. In order to run the Selenium tests
locally, you need BrowserStack credentials. The user email and key can
be found on the account settings page. To run the selenium tests:

```
BROWSERSTACK_TOKEN=<token> BROWSERSTACK_EMAIL=<email> ./script/selenium_test
```

The selenium tests are in `tests/acceptance`. This directory is ignored by
pytest for normal test runs.

The `selenium_test` script manages the setup of a separate database and
launching the BrowserStackLocal client. If you already have the client running
locally, you can run the selenium tests with:

```
BROWSERSTACK_TOKEN=<token> BROWSERSTACK_EMAIL=<email> pipenv run pytest tests/acceptance
```

The BrowserStack email is the one associated with the account. The token is
available in the BrowserStack profile information page. Go to the dashboard,
then "Account" > "Settings", then the token is under "Local Testing".

## Notes

Jinja templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache


## Icons
To render an icon, use

```jinja
{% import "components/icon.html" %}
{{ Icon("icon-name", classes="css-classes") }}
```

where `icon-name` is the filename of an svg in `static/icons`.

All icons used should be from the Noun Project, specifically [this collection](https://thenounproject.com/monstercritic/collection/tinicons-a-set-of-tiny-icons-perfect-for-ui-elemen/) if possible.

SVG markup should be cleaned an minified, [Svgsus](http://www.svgs.us/) works well.

## Deployment

The `/login-dev` endpoint is protected by HTTP basic auth when deployed. This can be configured for NGINX following the instructions [here](https://docs.nginx.com/nginx/admin-guide/security-controls/configuring-http-basic-authentication/). The following config should added within the main server block for the site:

```nginx
location /login-dev {
    auth_basic "Developer Access";
    auth_basic_user_file /etc/apache2/.htpasswd;
    [proxy information should follow this]
}
```

The location block will require the same proxy pass configuration as other location blocks for the app.
