ifeq ($(OS),Windows_NT)
	CC=python
else
	CC=python3
endif

PFLAGS=-3.8-64

TARGET?=src/main
CHECK?=src/test
SOURCES:=$(wildcard src/*.py)

.PHONY: all check docker dockerclean clean

all:
	$(CC) $(TARGET).py

check:
	python -m py_compile $(SOURCES)
	python $(CHECK).py

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
	@echo "Cleaning up [.pyc, __pycache__, apktool/, junk apk] files..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete
	@$(RM) modified-aligned.apk
	@$(RM) modified.apk
	@$(RM) signed.apk
	@$(RM) -rf ./apktool
endif
