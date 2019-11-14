FROM locustio/locust
USER root
RUN apk update && apk --no-cache add g++ gcc libxslt-dev
RUN pip install pyquery
USER locust
ADD locustfile.py locustfile.py

