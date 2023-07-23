.PHONY: all clean build test install

build:
	@pdm build

test: build
	@pytest

install: test
	@pdm install --dev

clean:
	@find . -name "__pycache__" -type d | xargs rm -v -rf
	@find . -name "*.pyc" -type f | xargs rm -v -rf
	@rm -v -rf .*_cache/ build/ dist/ *.log cover/ .coverage

all: clean install
