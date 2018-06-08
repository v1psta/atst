
# ATST

[![Build Status](https://travis-ci.org/dod-ccpo/atst.svg?branch=master)](https://travis-ci.org/dod-ccpo/atst)

## Installation

    script/setup

The setup script installs pipenv, which is what this application uses to manage its dependences and virtualenv. Instead of the classic `requirements.txt` file, pipenv uses a Pipfile and Pipfile.lock, making it more similar to other modern package managers like yarn or mix.

To enter the virtualenv manually (a la `source .venv/bin/activate`):

    pipenv shell

If you want to automatically load the virtual environment whenever you enter the project directory, take a look at [direnv](https://direnv.net/).  An `.envrc` file is included in this repository.  direnv will activate and deactivate virtualenvs for you when you enter and leave the directory.

## Running (development)

To start the app and watch for changes:

    DEBUG=1 script/server

## Testing

To run unit tests:

    script/test

or

    python -m pytest

## Notes

tornado templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache

