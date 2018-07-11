
# ATST

[![Build Status](https://travis-ci.org/dod-ccpo/atst.svg?branch=master)](https://travis-ci.org/dod-ccpo/atst)

## Description

This is the main user-facing web application for the ATAT stack. All end-user
requests are handled by ATST, with it making backend calls to various
microservices when appropriate.

## Installation

See the [scriptz](https://github.com/dod-ccpo/scriptz) repository for the shared 
requirements and guidelines for all ATAT applications.

This project contains git submodules. Here is an example clone command that will 
automatically initialize and update those modules:
`git clone --recurse-submodules git@github.com:dod-ccpo/atst.git`

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

If you want to automatically load the virtual environment whenever you enter the project directory, take a look at [direnv](https://direnv.net/).  An `.envrc` file is included in this repository.  direnv will activate and deactivate virtualenvs for you when you enter and leave the directory.

Additionally, ATST requires a redis instance for session management. Have redis installed and running. By default, ATST will try to connect to a redis instance running on localhost on its default port, 6379.

## Running (development)

To start the app locally in the foreground and watch for changes:

    script/dev_server

## Testing

To run lint, static analysis, and unit tests:

    script/test

To run only the unit tests:

    pipenv run python -m pytest

To re-run tests each time a file is changed:

    pipenv run ptw

## Notes

tornado templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache

