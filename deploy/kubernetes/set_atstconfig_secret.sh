#!/bin/bash

kubectl -n atat delete secret atst-config-ini
kubectl -n atat create secret generic atst-config-ini --from-file="${1}"
