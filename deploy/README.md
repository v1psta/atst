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

A rough example of the necessary config changes can be found at this commit: [`d81b8a03b2bb407e04cd4265fa90f4cf7ab82b9e`](https://github.com/dod-ccpo/atst/commit/d81b8a03b2bb407e04cd4265fa90f4cf7ab82b9e)

To proceed, you will need to install [certbot](https://certbot.eff.org/docs/install.html). If you are on macOs and have `homebrew` installed, `brew install certbot`. These instructions assume a baseline familiarity with NGINX config, Kubernetes, and `kubectl`.

As a broad overview, we will:

- Ask certbot for certificates for the two domains
- Get ACME challenge data from certbot
- Make that data available to the NGINX container in the ATAT pod in our cluster
- Update the NGINX config so that it can server the ACME challenge

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

First you will be presented with an ACME challenge for the main domain. Create a file with the challenge. The file should be named for the last part of the URL path and contain the challenge data.

Create a k8s secret from the challenge file:

```
kubectl -n atat create secret generic acme --from-file=./dpYfQi4C2qgH1WW_XZmFPbahqOsXJKh64ZOqJCWB4q0
```

(Substitute your challenge file name for the `dpY` string in the example.)

Refer to the sample commit mentioned above for examples of Kubernetes config necessary to make the secret available as a file to the NGINX container. Once the YAML has been updated, apply it to the cluster.

You will repeat this process for the auth domain. Note that the secret name for the auth domain should be `acme-auth`.

### NGINX config

Next, apply NGINX config to allow NGINX to server the ACME challenges. The NGINX config can be found in `deploy/{aws,azure}/atst-nginx-configmap.yml`.

There are two server blocks at the beginning of the config that redirect HTTP requests to the domains to their HTTPS equivalents. Temporarily alter these blocks so that they serve the ACME challenge:

```
server {
    listen 8342;
    server_name jedi.atat.code.mil;
    return 301 https://$host$request_uri;
}
```

becomes:

```
server {
    listen 8342;
    server_name jedi.atat.code.mil;
    root /usr/share/nginx/html;
    location /.well-known/acme-challenge/ {
      try_files $uri =404;
    }
}
```

Do this for both the 8342 and 8342 blocks. Apply the config changes to the cluster. (You may have to rebuild the pods, since they will not inherit the updated NGINX config automatically.)

You can confirm that the cluster is serving the ACME challenges successfully by hitting the URLs certbot lists for the challenges. You should get your challenge file back when hitting the URL. You can hit [enter] in the certbot prompt, and it should issue certificates to a location on your machine.

### Create the TLS secret

Once you have obtained the certs, you can create the new TLS secret in the cluster. First delete the existing secret. (It should be named something like `csp-atat-code-mil-tls`, where `csp` is the name of the CSP.)

Then:

```
kubectl -n atat create secret tls csp-atat-code-mil-tls --key="[path to the private key]" --cert="[path to the full chain]"
```
