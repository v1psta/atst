
# ATST

## Installation

    brew install python3
    python3 -m venv .venv
    . .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd static/assets
    wget https://github.com/uswds/uswds/releases/download/v1.6.3/uswds-1.6.3.zip
    unzip uswds-1.6.3.zip

## Running (development)

    DEBUG=1 ./app.py

## Notes

tornado templates are like mustache templates -- add the
following to `~/.vim/filetype.vim` for syntax highlighting:

    :au BufRead *.html.to set filetype=mustache

## To Run the CAC Auth Demo

This CAC auth demo leaves client authentication as optional in the NGINX config.

This will start the demo app:

```
docker-compose up
```

For some reason, NGINX isn't starting correctly from the Dockerfile. To fix this, start NGINX within the container once the container is running:

```
docker-compose exec web service nginx start
```

Next, visit localhost on your machine (`http://localhost`). You should be redirected to https and wind up on a welcome page served by the app. If the PromptWorks smart card is plugged in and working, it will tell you you're SSL verified and display the SDN info. If not, it will say false.
