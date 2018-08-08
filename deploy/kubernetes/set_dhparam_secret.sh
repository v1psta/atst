#!/bin/bash

kubectl -n atat delete secret dhparam-4096
kubectl -n atat create secret generic dhparam-4096 --from-file="${1}"
