
# ATST

## Installation

    brew install python3
    python3 -m venv .venv
    . .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    npm install
    ./gen-css

## Running (development)

To start the app and watch for changes:

    DEBUG=1 ./app.py

To rebuild css whenever the scss changes:

    ./gen-css --watch

## Notes

tornado templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache

