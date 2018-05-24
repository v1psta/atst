
# ATST

## Installation

    brew install python3
    python3 -m venv .venv
    . .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    npm install
    gem install sass

## Running (development)

To start the app and watch for changes:

    DEBUG=1 ./app.py

## Testing

To run unit tests:

    python -m pytest

or

    make test

## Notes

tornado templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache

