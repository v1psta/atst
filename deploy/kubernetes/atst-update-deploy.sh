#!/usr/bin/env bash
#
# deploy/kubernetes/atst-update-deploy.sh: Updates the existing ATST deployment
#                                          with a new source image

set -o pipefail
set -o errexit
set -o nounset
# set -o xtrace

# Config
MAX_DEPLOY_WAIT='300'

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
    --namespace=atat

kubectl config set-cluster atat-cluster \
    --embed-certs=true \
    --server="${K8S_ENDPOINT}"  \
    --certificate-authority="${HOME}/k8s_ca.crt"

kubectl config set-credentials atat-deployer --token="$(echo ${K8S_USER_TOKEN} | base64 -d -)"

kubectl config use-context atst-deployer
kubectl config current-context

# Update the ATST deployment
kubectl -n atat set image deployment.apps/atst atst="${IMAGE_NAME}"
kubectl -n atat set image deployment.apps/atst-worker atst-worker="${IMAGE_NAME}"

# Wait for deployment to finish
if ! timeout -t "${MAX_DEPLOY_WAIT}" -s INT kubectl -n atat rollout status deployment/atst
then
    # Deploy did not finish before max wait time; abort and rollback the deploy
    kubectl -n atat rollout undo deployment/atst
    kubectl -n atat rollout undo deployment/atst-worker
    # Exit with a non-zero return code
    exit 2
fi
