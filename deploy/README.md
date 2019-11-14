# Kubernetes Deployment Configuration

This folder contains Kubernetes deployment configuration for Azure. The following assumes that you have `kubectl` installed and configured with permissions to a Kubernetes cluster.

## Applying K8s configuration

Applying the K8s config relies on a combination of kustomize and envsubst. Kustomize comes packaged with kubectl v0.14 and higher. envsubst is part of the gettext package. It can be installed with `brew install gettext` for MacOS users.

The production configuration (azure.atat.code.mil, currently) is reflected in the configuration found in the `deploy/azure` directory. Configuration for a staging environment relies on kustomize to overwrite the production config with values appropriate for that environment. You can find more information about using kustomize [here](https://kubernetes.io/docs/tasks/manage-kubernetes-objects/kustomization/). Kustomize does not manage templating, and certain values need to be templated. These include:

- CONTAINER_IMAGE: the ATAT container image to use
- PORT_PREFIX: "8" for production, "9" for staging
- MAIN_DOMAIN: the host domain for the environment
- AUTH_DOMAIN: the host domain for the authentication endpoint for the environment

We use envsubst to substitute values for these variables.

To apply config to the main environment, you should first do a diff to determine whether your new config introduces unexpected changes:

```
kubectl kustomize deploy/azure | CONTAINER_IMAGE=myregistry.io/atat-some-commit-sha PORT_PREFIX=8 MAIN_DOMAIN=azure.atat.code.mil AUTH_DOMAIN=auth-azure.atat.code.mil envsubst '$CONTAINER_IMAGE $PORT_PREFIX $MAIN_DOMAIN $AUTH_DOMAIN' | kubectl diff -f -
```

Here, `kubectl kustomize` assembles the config and streams it to STDOUT. We specify environment variables for envsubst to use and pass the names of those env vars as a string argument to envsubst. This is important, because envsubst will override NGINX variables in the NGINX config if you don't limit its scope. Finally, we pipe the result from envsubst to `kubectl diff`, which reports a list of differences. Note that some values tracked by K8s internally might have changed, such as [`generation`](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.16/#objectmeta-v1-meta). This is fine and expected.

If you are satisfied with the output from the diff, you can apply the new config the same way:

```
kubectl kustomize deploy/azure | CONTAINER_IMAGE=myregistry.io/atat-some-commit-sha PORT_PREFIX=8 MAIN_DOMAIN=azure.atat.code.mil AUTH_DOMAIN=auth-azure.atat.code.mil envsubst '$CONTAINER_IMAGE $PORT_PREFIX $MAIN_DOMAIN $AUTH_DOMAIN' | kubectl apply -f -
```

**Note:** Depending on how your `kubectl` config is set up, these commands may need to be adjusted. If you have configuration for multiple clusters, you may need to specify the `kubectl` context for each command with the `--context` flag (something like `kubectl --context=my-cluster [etc.]` or `kubectl --context=azure [etc.]`).

## Secrets and Configuration

### atst-overrides.ini

Production configuration values are provided to the ATAT Flask app by writing an `atst-overrides.ini` file to the running Docker container. This file is stored as a Kubernetes secret. It contains configuration information for the database connection, mailer, etc.

To update the configuration, you can do the following:

```
kubectl -n atat get secret atst-config-ini -o=jsonpath='{.data.override\.ini}' | base64 --decode > override.ini
```

This base64 decodes the secret and writes it to a local file called `override.ini`. Make any necessary config changes to that file.

To apply the new config, first delete the existing copy of the secret:

```
kubectl -n atat delete secret atst-config-ini
```

Then create a new copy of the secret from your updated copy:

```
kubectl -n atat create secret generic atst-config-ini --from-file=./override.ini
```

Notes:

- Be careful not to check the override.ini file into source control.
- Be careful not to overwrite one CSP cluster's config with the other's. This will break everything.

### nginx-htpasswd

If the site is running in dev mode, the `/login-dev` endpoint is available. This endpoint is protected by basic HTTP auth. To create a new password file, run:

```
htpasswd -c ./htpasswd atat
```

Enter a new password string when prompted. Then create the secret:

```
kubectl -n atat create secret generic nginx-htpasswd --from-file=./htpasswd
```

## SSL/TLS

(NOTE: We should get cert-manager working for automatic updates of the certificates.)

The NGINX instance in the ATAT pod handles SSL/TLS termination for both the main domain and authentication domain. The certificates are stored as a k8s TLS secret. Currently, certs are obtained from Let's Encrypt by running certbot in manual mode. This section will walk through that process.

For context, you should be familiar with [ACME HTTP-01 challenge](https://letsencrypt.org/docs/challenge-types/) method for proving ownership of a domain.

To proceed, you will need to install [certbot](https://certbot.eff.org/docs/install.html). If you are on macOs and have `homebrew` installed, `brew install certbot`. These instructions assume a baseline familiarity with NGINX config, Kubernetes, and `kubectl`.

As a broad overview, we will:

- Ask certbot for certificates for the two domains
- Get ACME challenge data from certbot
- Make that data available to the NGINX container in the ATAT pod in our cluster

Once this is done, certbot will be able to confirm that we own the domains and will issue certificates. Then we can make those certs available as TLS secrets in the cluster.

These steps should work for updating an existing site. If you are setting up HTTPS for a new site, make sure DNS is assigned for your two domains.

### Start certbot

First start certbot in manual mode:

```
certbot --manual
```

(You may need to supply `--config-dir`, `--work-dir`, and `--logs-dir` options; certbot may try to write to directories that require root privileges by default.)

You will be prompted to enter the domain names you want a cert for. Enter **both** the main and auth domains. For instance:

```
jedi.atat.code.mil,jedi-auth.atat.code.mil
```

You must agree to have your IP logged to proceed.

### The ACME challenge files

First you will be presented with an ACME challenge for the main domain.

The ACME challenges are managed as a Kubernetes ConfigMap resource. An example ConfigMap can be found in `deploy/azure/acme-challenges.yml`. It contains a sample ACME challenge (where "foo" is the file name and "bar" is the secret data). Certbot will present you with a file name and path. Add these as a key and a value to the ConfigMap. As an example, certbot may present a challenge like this:

```
Create a file containing just this data:

ty--Ip1l5bAE1RWk3aL5EnI76OKL-iueFtkRLheugUw.nqBL619amlBbWsSSfB8zqcZowwEI-sFdok57VDkxTmk

And make it available on your web server at this URL:

http://auth-staging.atat.code.mil/.well-known/acme-challenge/ty--Ip1l5bAE1RWk3aL5EnI76OKL-iueFtkRLheugUw
```

You would then update the acme-challenges.yml file to look like this:

```
data:
  foo: |
    bar
  ty--Ip1l5bAE1RWk3aL5EnI76OKL-iueFtkRLheugUw: |
    ty--Ip1l5bAE1RWk3aL5EnI76OKL-iueFtkRLheugUw.nqBL619amlBbWsSSfB8zqcZowwEI-sFdok57VDkxTmk
```

Apply the updated ConfigMap using the kubectl commands discussed in the "Applying K8s Configuration" section above.

Once the updated ConfigMap is applied, you can roll the deployment with some version of:

```
kubectl -n atat rollout restart deployment atst
```

This will start new pods for the web service, and the new ACME challenge will be available from the NGINX web server. You can verify this by clicking the link certbot provides and verifying that you get the ACME challenge content you expect.

Repeat this process for the second domain. If the validation is successful, certbot will write new certificates to your host machine.

### Create the TLS secret

Once you have obtained the certs, you can create the new TLS secret in the cluster. First delete the existing secret:

```
kubectl -n atat delete secret azure-atat-code-mil-tls
```

Then:

```
kubectl -n atat create secret tls azure-atat-code-mil-tls --key="[path to the private key]" --cert="[path to the full chain]"
```
