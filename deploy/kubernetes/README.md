# Adding a New Environment

## New Config

Add a new subfolder to this directory. You can copy `uat` or `tests`. You'll need to change any references to the previous environment name (i.e., `uat`) to your new environment name. This includes things like the k8s namespace and the subdomain for the new site.

## New Load Balancers

You need two new load balancers. Currently, these are managed in Rackspace. You will need one for the regular site and one for the auth domain. They should have all of the Kubernetes worker nodes attached. When attached to the LB for the main site domain, the nodes should point to port 32761, which is the port where all our NGINX ingress is managed. The auth LB nodes should point to a new port in the 32700 - 32799 range. The `nodePort` specified in your new environment's config should match this port.

## Initially Apply the New Config

Apply your new environment config to create the namespace. Pod creation will fail at this point.

```
kubectl -n my-new-env apply -f deploy/kubernetes/my-new-env/
```

## Create New Secrets

You should then copy and duplicate the secrets from another environment.

### Adjust the INI Config for the New Site

You can duplicate the override.ini file from one of the existing sites. For instance, to get the `atst-config-ini` secret for the UAT env:

```
kubectl -n atat-uat get secret atst-config-ini -o yaml > uat-secrets.yml
```

You can copy the base64 secret content from the `uat-secrets.yml` file. Decode it into a new `override.ini` file:

```
echo '[Paste in the long base64 string here]' | base64 --decode > override.ini
```

Edit and adjust the application config as needed for your new site. Then add it as a secret:

```
kubectl -n my-new-env create secret generic atst-config-ini --from-file=override.ini
```

### Add a New htpasswd

Create a new htpasswd to protect the dev login of the new site:

```
htpasswd -c htpasswd atat
```

You'll be prompted for the new password. Then add it as a secret:

```
kubectl -n my-new-env create secret generic atst-nginx-htpasswd --from-file=htpasswd
```

### Duplicate the Rest

You should also the `dhparam-4096` and `nginx-client-ca-bundle` secrets. These can be copied from an existing environment to yours without any changes. The TLS secrets and token will be handled by another service.

## Disable SSL

In order for [kube-lego](https://github.com/jetstack/kube-lego) to generate new certs for your site, you have to temporarily disable SSL for your new load balancers.

For both your LBs, set them to use HTTP/80. Delete the attached nodes for both and re-add them, setting them to use port 32760. This will allow kube-lego to do its job.

To monitor the process, find the pod ID for the kube-lego worker. To find it, look in the output for:

```
kubectl -n kube-system get all
```

Then once you know the pod name:

```
kubectl -n kube-system --kubeconfig ~/.kube/atat log kube-lego-b96b7bc5c-9fmcv -f --tail=10
```

You will see output about kube-lego attempts to create certs for your new site.

Once kube-lego is successful, you should restore your load balancers to the config they had initially. Additionally, you should enable HTTPS redirects.
