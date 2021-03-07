ifeq ($(OS),Windows_NT)
	CC=python
else
	CC=python3
endif

PFLAGS=-3.8-64

TARGET?=src/main
SOURCES:=$(wildcard src/*.py)

.PHONY: all check docker dockerclean clean

all:
	$(CC) $(TARGET).py

check:
	python -m py_compile $(SOURCES)

docker:
	docker build -t obfuscator:latest .
	docker run -ti obfuscator

dockerclean:
	docker system prune -a

clean:
ifeq ($(OS),Windows_NT)
	@powershell "(Get-ChildItem * -Include *.pyc -Recurse | Remove-Item)"
	@echo Cleaned up .pyc, .cap files and .cache files
else
	@echo "Cleaning up [.pyc, .cap, .cache, carved] files..."
	@find . -type f -name "*.pyc" -delete
	@echo "Cleaning complete!"
endif
