#!/bin/bash

kubectl -n atat create secret generic dhparam-4096 --from-file=./dhparam.pem
