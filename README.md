
# ATST

## Installation

    brew install python3
    python3 -m venv .venv
    . .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    npm install
    ./get-css

## Running (development)

    DEBUG=1 ./app.py

## Notes

tornado templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache

