ifeq ($(OS),Windows_NT)
	CC=python
else
	CC=python3
endif

PFLAGS=-3.8-64

TARGET?=src/main
SERVER?=src/server
CHECK?=src/test
SOURCES = $(shell find src/ -type f -name '*.py')

.PHONY: all check docker dockerclean clean server

all:
	$(CC) $(TARGET).py

server:
	$(CC) $(SERVER).py

check:
	python -m py_compile $(SOURCES)
	python $(CHECK).py

docker:
	docker build -t obfuscator:latest .
	docker run -ti -p 6969:6969/tcp obfuscator

dockerclean:
	docker system prune -a

clean:
ifeq ($(OS),Windows_NT)
	@powershell "(Get-ChildItem * -Include *.pyc -Recurse | Remove-Item)"
	@echo Cleaned up .pyc, .cap files and .cache files
else
	@echo "Cleaning up [.pyc, __pycache__, .tmp/, junk apk] files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@find ./.tmp/* -type f,d -not -name 'placeholder' -delete
endif
