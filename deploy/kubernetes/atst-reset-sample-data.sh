#!/usr/bin/env bash
#
# deploy/kubernetes/atst-update-deploy.sh: Resets the sample data on the target
#                                          environment.

set -o pipefail
set -o errexit
set -o nounset
# set -o xtrace

# Config
MAX_DEPLOY_WAIT='300'

if [[ $# -eq 0 ]]; then
  NAMESPACE=atat
else
  NAMESPACE=$1
fi

if [ "${IMAGE_NAME}x" = "x" ]
then
    IMAGE_NAME="${ATAT_DOCKER_REGISTRY_URL}/${PROD_IMAGE_NAME}:${GIT_SHA}"
fi

# Remove the K8S CA file when the script exits
function cleanup {
    printf "Cleaning up...\n"
    rm -vf "${HOME}/k8s_ca.crt"
    printf "Cleaning done."
}
trap cleanup EXIT

# Decode and save the K8S CA cert
echo "${K8S_CA_CRT}" | base64 -d - > "${HOME}/k8s_ca.crt"

# Setup the local kubectl client
kubectl config set-context atst-deployer \
    --cluster=atat-cluster \
    --user=atat-deployer \
    --namespace=${NAMESPACE}

kubectl config set-cluster atat-cluster \
    --embed-certs=true \
    --server="${K8S_ENDPOINT}"  \
    --certificate-authority="${HOME}/k8s_ca.crt"

kubectl config set-credentials atat-deployer --token="$(echo ${K8S_USER_TOKEN} | base64 -d -)"

kubectl config use-context atst-deployer
kubectl config current-context

# we only need to run these commands against one existing pod
ATST_POD=$(kubectl -n ${NAMESPACE} get pods -l app=atst -o custom-columns=NAME:.metadata.name --no-headers)
kubectl -n ${NAMESPACE} exec ${ATST_POD} -- pipenv run python script/remove_sample_data.py
kubectl -n ${NAMESPACE} exec ${ATST_POD} -- pipenv run python script/seed_sample.py

