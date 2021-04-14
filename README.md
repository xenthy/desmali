# desmali <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->
- [Setting Up](#setting-up)
- [Running Project using Make](#running-project-using-make)
- [Running Project using Docker](#running-project-using-docker)
- [Obfuscation Methods](#obfuscation-methods)
  - [Purge Logs [Remove]](#purge-logs-remove)
  - [String Encryption [Replace]](#string-encryption-replace)
  - [Rename Methods [Rename]](#rename-methods-rename)
  - [Rename Class [Rename]](#rename-class-rename)
  - [Goto Injector [Restructure]](#goto-injector-restructure)
  - [Boolean Arithmetic [Restructure]](#boolean-arithmetic-restructure)
  - [Randomise Labels [Restructure]](#randomise-labels-restructure)
- [Viewing Debug Logs](#viewing-debug-logs)

## Setting Up
1. Build/Install dependencies
```console
➜ ./configure
```

## Running Project using Make
1. To run the program
```console
➜ cd desmali
➜ make server
```
2. To clean compiled files (.pyc, \_\_pycache\_\_/, .tmp/)
```console
➜ make clean
```

## Running Project using Docker
```console
➜ cd desmali
➜ make docker
```

## Obfuscation Methods
### Purge Logs [Remove]
> Remove logs that may contain sensitive information

### String Encryption [Replace]
> Encrypt strings with AES

### Rename Methods [Rename]
> Rename method declarations and invocations

### Rename Class [Rename]
> Rename classes and their packages

### Goto Injector [Restructure]
> Modify the CFG by wrapping each method with 2 nodes

### Boolean Arithmetic [Restructure]
> Inject an always true/false clause into the CFG

### Randomise Labels [Restructure]
> Alter the CFG by randomly reordering & abusing goto instructions

## Viewing Debug Logs
Logs with the level of verbose and higher will be printed to stdout, to view debug logs, navigate to logs/program.log