# star-test

This is the blockchain(CLI) automated testing framework

## Dependency

Install the python 3.9+, and execute the following command:

```shell
pip install -r requirements.txt
```

## Configuration

```shell
config/chain.py Depend on nacos-server
```

## Run

```shell
# Show help on command line and config file options
python main.py or pytest --help

# Run with docker
docker build . -t test996/gea-chain-test:v1.0.0
$ docker run -d --name gea-chain-test -v /tmp/docker/gea-chain-report:/app/results  test996/gea-chain-test:v1.0.0
```

## View test report

```shell
# Get the path to the VOLUME
docker inspect chain-test
# Start allure server
allure serve /tmp/docker/gea-chain-report/xxxxxx_xxxxxx
```