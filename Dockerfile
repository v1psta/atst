FROM nginx:1.13.2

WORKDIR /cac
ADD requirements.txt .
RUN apt-get update
RUN apt-get install -y python3 python3-pip unzip wget
RUN ln -s /usr/bin/python3 /usr/bin/python && ln -s /usr/bin/pip3 /usr/bin/pip
RUN pip install -r /cac/requirements.txt
RUN wget https://github.com/uswds/uswds/releases/download/v1.6.3/uswds-1.6.3.zip && \
    unzip uswds-1.6.3.zip -d static/

COPY docker/default.conf /etc/nginx/conf.d/default.conf
COPY docker/cert.pem /etc/nginx/cert.pem
COPY docker/np.key.pem /etc/nginx/key.pem
COPY docker/ca-chain.pem /etc/nginx/dod-root-certs.pem

RUN ["service", "nginx", "start"]
CMD ["./app.py"]
