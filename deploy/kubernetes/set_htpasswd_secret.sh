#!/bin/bash

kubectl -n atat delete secret atst-nginx-htpasswd
kubectl -n atat create secret generic atst-nginx-htpasswd --from-file="${1}"
