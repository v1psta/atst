# Ghost Inspector Readme

The suite of Ghost Inspector tests that runs as part of the CI/CD workflow
can be found [here](https://app.ghostinspector.com/suites/5d9e3d303ab5d56633c11598). Its current status is https://api.ghostinspector.com/v1/suites/5d9e3d303ab5d56633c11598/status-badge

[Another suite](https://app.ghostinspector.com/suites/5d9603f1af31210914da04ca) of Ghost Inspector tests runs once daily against the Staging site. Status: https://api.ghostinspector.com/v1/suites/5d9603f1af31210914da04ca/status-badge

## Testing philosophy

The tests have been created to traverse the most common user flows in AT-AT. There are a few tests (e.g. "New Portfolio - no optional fields")
that check for regressions. Others (e.g. "Remove Portfolio Member") check less-common, "negative path" flows. Tests are added as necessary
to ensure fairly thorough checking of AT-AT.

The tests are constructed in a "stepwise" fashion; that is, no individual test depends upon another, and each test checks one step in complex
user flows. As an example, there are six tests for creating a new Task Order, one corresponding to each screen in the process plus one
for adding a second CLIN to a TO. These tests rely on Ghost Inspector's "Import steps from Test X" functionality to perform all the
necessary setup for the current test. This also ensures that tests can be run in any sequence because Ghost Inspector launches up to four
tests simultaneously.

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
