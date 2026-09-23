# Thin wrapper over scripts/dev.py (which works without make, e.g. on Windows).
PY ?= python
AREA ?=

.PHONY: setup env api web up down migrate seed sim test lint contracts check
setup:     ; $(PY) scripts/dev.py setup
env:       ; $(PY) scripts/dev.py env
api:       ; $(PY) scripts/dev.py api
web:       ; $(PY) scripts/dev.py web
up:        ; $(PY) scripts/dev.py up
down:      ; $(PY) scripts/dev.py down
migrate:   ; $(PY) scripts/dev.py migrate
seed:      ; $(PY) scripts/dev.py seed
sim:       ; $(PY) scripts/dev.py sim $(ARGS)
test:      ; $(PY) scripts/dev.py test $(AREA)
lint:      ; $(PY) scripts/dev.py lint
contracts: ; $(PY) scripts/dev.py contracts
check:     ; $(PY) scripts/dev.py check
