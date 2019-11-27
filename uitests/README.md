# Ghost Inspector Readme

To run the Ghost Inspector tests against a local instance of AT-AT,
you will need the following:

- [docker](https://docs.docker.com/v17.12/install/)
- [circleci CLI tool](https://circleci.com/docs/2.0/local-cli/#installation)
- the prerequisite variable information listed [here](https://ghostinspector.com/docs/integration/circle-ci/)

The version of our CircleCI config (2.1) is incompatible with the
`circleci` tool. First run:

```
circleci config process .circleci/config.yml > local-ci.yml
```

Then run the job:

```
circleci local execute -e GI_SUITE=<SUITE_ID> -e GI_API_KEY=<API KEY> -e NGROK_TOKEN=<NGROK TOKEN> --job integration-tests -c local-ci.yml
```

If the job fails and you want to re-run it, you may receive errors
about running docker containers or the network already existing.
Some version of the following should reset your local docker state:

```
docker container stop redis postgres test-atat; docker container rm redis postgres test-atat ; docker network rm atat
```
