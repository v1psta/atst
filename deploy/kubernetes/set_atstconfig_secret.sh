#!/bin/bash

kubectl -n atat create secret generic atst-config-ini --from-file=${1}
