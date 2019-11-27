# Ghost Inspector Readme

The suite of Ghost Inspector tests that runs as part of the CI/CD workflow
can be found [here](https://app.ghostinspector.com/suites/5d9e3d303ab5d56633c11598). Its current status is https://api.ghostinspector.com/v1/suites/5d9e3d303ab5d56633c11598/status-badge

[Another suite](https://app.ghostinspector.com/suites/5d9603f1af31210914da04ca) of Ghost Inspector tests runs once daily against the Staging site. Status: https://api.ghostinspector.com/v1/suites/5d9603f1af31210914da04ca/status-badge

## Running Ghost Inspector tests locally

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
