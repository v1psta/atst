
# ATST

[![Build Status](https://travis-ci.org/dod-ccpo/atst.svg?branch=master)](https://travis-ci.org/dod-ccpo/atst)

## Installation

    ./script/setup

The setup script will create a new Python virtual environment for the application to use. All of the scripts will activate this virutal envirnment automatically, but you can also manually activate it like this:

    source .venv/bin/activate

If you want to automatically load the virtual environment whenever you enter the project directory, take a look at [direnv](https://direnv.net/).  An `.envrc` file is included in this repository.

## Running (development)

To start the app and watch for changes:

    DEBUG=1 ./script/server

## Testing

To run unit tests:

    ./script/test

or

    python -m pytest

or

    make test

## Notes

tornado templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache

