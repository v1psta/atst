FROM nginx:1.13.2

RUN apt-get update
RUN apt-get -y install perl curl build-essential libssl-dev
RUN curl -L http://cpanmin.us | perl - App::cpanminus
RUN cpanm Mojolicious
# RUN cpanm Mojolicious::Plugin::SslAuth

WORKDIR /cac
COPY default.conf /etc/nginx/conf.d/default.conf
COPY cert.pem /etc/nginx/cert.pem
COPY np.key.pem /etc/nginx/key.pem
COPY ca-chain.pem /etc/nginx/dod-root-certs.pem

RUN ["service", "nginx", "start"]
CMD ["/cac/myapp.pl", "daemon", "-l", "http://localhost:8080"]
