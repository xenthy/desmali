# ict2207-assignment-2 <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->
- [Setting Up](#setting-up)
- [Running Project using Make](#running-project-using-make)
- [Running Project using Docker](#running-project-using-docker)
- [Viewing Debug Logs](#viewing-debug-logs)

## Setting Up
1. Build/Install dependencies
```console
➜ ./configure
```

## Running Project using Make
1. To run the program
```console
➜ cd ict2207-assignment-2
➜ make server
```
2. To clean compiled files (.pyc, \_\_pycache\_\_/, .tmp/)
```console
➜ make clean
```

## Running Project using Docker
```console
➜ cd ict2207-assignment-2
➜ make docker
```

## Viewing Debug Logs
Logs with the level of verbose and higher will be printed to stdout, to view debug logs, navigate to logs/program.log