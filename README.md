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

* `pipenv`
  ATST requires `pipenv` to be installed for python dependency management. `pipenv`
  will fetch and install the appropriate versions of Python and `pip`. [See
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

    script/dev_server

To watch for changes to any js/css assets:

    yarn watch

After running `script/dev_server`, the application is available at
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
