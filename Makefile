# Thin wrapper over scripts/dev.py (which works without make, e.g. on Windows).
PY ?= python
M ?=

.PHONY: env api up down migrate seed sim test lint contracts web-operator web-admin
env:          ; $(PY) scripts/dev.py env
api:          ; $(PY) scripts/dev.py api
up: env       ; $(PY) scripts/dev.py up
down:         ; $(PY) scripts/dev.py down
migrate:      ; $(PY) scripts/dev.py migrate
seed:         ; $(PY) scripts/dev.py seed
sim:          ; $(PY) scripts/dev.py sim $(ARGS)
test:         ; $(PY) scripts/dev.py test $(M)
lint:         ; $(PY) scripts/dev.py lint
contracts:    ; $(PY) scripts/dev.py contracts
web-operator: ; $(PY) scripts/dev.py web operator
web-admin:    ; $(PY) scripts/dev.py web admin
