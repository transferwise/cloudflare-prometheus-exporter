
DOCKER_IMAGE_TAG  ?= $(subst /,-,$(shell git rev-parse --abbrev-ref HEAD))-$(shell date +%Y-%m-%d)-$(shell git rev-parse --short HEAD)
DOCKER_CI_TAG     ?= test

JB                ?= jb
EMBEDMD           ?= embedmd
JSONNET           ?= jsonnet
GOJSONTOYAML      ?= gojsontoyaml
PROMTOOL          ?= promtool

CLOUDFLARE_MIXIN        ?= mixin
JSONNET_VENDOR_DIR      ?= mixin/vendor


define require_clean_work_tree
	@git update-index -q --ignore-submodules --refresh

	@if ! git diff-files --quiet --ignore-submodules --; then \
		echo >&2 "cannot $1: you have unstaged changes."; \
		git diff-files --name-status -r --ignore-submodules -- >&2; \
		echo >&2 "Please commit or stash them."; \
		exit 1; \
	fi

	@if ! git diff-index --cached --quiet HEAD --ignore-submodules --; then \
		echo >&2 "cannot $1: your index contains uncommitted changes."; \
		git diff-index --cached --name-status -r --ignore-submodules HEAD -- >&2; \
		echo >&2 "Please commit or stash them."; \
		exit 1; \
	fi

endef

.PHONY: build

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache

init:
	pip install -r requirements-dev.txt
	pre-commit install

test: ## run tests quickly with the default Python
	py.test -o log_cli=true -sv --cov=cloudflare_exporter tests/

install: clean ## install the package to the active Python's site-packages
	python setup.py install

dist: clean ## builds source and wheel package
	python setup.py bdist_wheel --universal

build:
	docker build . -t prometheus-exporter/cloudflare-exporter:${DOCKER_IMAGE_TAG}

mixin: jsonnet-vendor
	-mkdir examples
	$(JSONNET) -J ${JSONNET_VENDOR_DIR} ${CLOUDFLARE_MIXIN}/alerts.jsonnet | $(GOJSONTOYAML) > examples/alerts.yaml
	$(JSONNET) -J ${JSONNET_VENDOR_DIR} ${CLOUDFLARE_MIXIN}/rules.jsonnet | $(GOJSONTOYAML) > examples/rules.yaml
	$(JSONNET) -J ${JSONNET_VENDOR_DIR} ${CLOUDFLARE_MIXIN}/dashboards.jsonnet > examples/dashboards.json
	${PROMTOOL} check rules examples/alerts.yaml
	${PROMTOOL} check rules examples/rules.yaml

.PHONY: jsonnet-vendor
jsonnet-vendor:
	rm -rf ${JSONNET_VENDOR_DIR}
	cd ${CLOUDFLARE_MIXIN} && $(JB) install
