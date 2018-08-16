#!/usr/bin/env bash
#
# deploy/kubernetes/atst-update-deploy.sh: Updates the existing ATST deployment
#                                          with a new source image

set -o pipefail
set -o errexit
set -o nounset
# set -o xtrace

# Decode and save the K8S CA cert
echo "${K8S_CA_CRT}" | base64 --decode -i > "${HOME}/k8s_ca.crt"

# Setup the local kubectl client
kubectl config set-context travis \
    --cluster=atat-cluster \
    --user=atat-deployer \
    --namespace=atat

kubectl config set-cluster atat-cluster \
    --embed-certs=true \
    --server="${K8S_ENDPOINT}"  \
    --certificate-authority="${HOME}/k8s_ca.crt"

kubectl config set-credentials atat-deployer --token=`echo ${K8S_USER_TOKEN} | base64 --decode`

kubectl config use-context travis
kubectl config current-context

# Update the ATST deployment
kubectl -n atat set image deployment.apps/atst atst="${remote_image_name}"

# Remove the K8S CA file when the script exits
function cleanup {
    printf "Cleaning up...\n"
    rm -vf "${HOME}/k8s_ca.crt"
    printf "Cleaning done."
}

trap cleanup EXIT
