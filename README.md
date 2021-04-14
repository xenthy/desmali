# desmali <!-- omit in toc -->

## Table of Contents <!-- omit in toc -->
- [Setting Up](#setting-up)
- [Running Project using Make](#running-project-using-make)
- [Running Project using Docker](#running-project-using-docker)
- [Obfuscation Methods](#obfuscation-methods)
  - [Remove](#remove)
    - [Purge Logs](#purge-logs)
  - [Replace](#replace)
    - [String Encryption](#string-encryption)
  - [Rename](#rename)
    - [Rename Methods](#rename-methods)
    - [Rename Class](#rename-class)
  - [Restructure](#restructure)
    - [Goto Injector](#goto-injector)
    - [Boolean Arithmetic](#boolean-arithmetic)
    - [Randomise Labels](#randomise-labels)
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
### Remove
#### Purge Logs
> Remove logs that may contain sensitive information

### Replace
#### String Encryption
> Encrypt strings with AES

### Rename
#### Rename Methods
> Rename method declarations and invocations

#### Rename Class
> Rename classes and their packages

### Restructure
#### Goto Injector
> Modify the CFG by wrapping each method with 2 nodes

#### Boolean Arithmetic
> Inject an always true/false clause into the CFG

#### Randomise Labels
> Alter the CFG by randomly reordering & abusing goto instructions

## Viewing Debug Logs
Logs with the level of verbose and higher will be printed to stdout, to view debug logs, navigate to logs/program.log