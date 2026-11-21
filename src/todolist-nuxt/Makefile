# Build and push the todolist-nuxt image.
#
#   make                         # show settings and targets
#   make build VERSION=1.0       # build the image
#   make push  VERSION=1.0       # build and push it
#
# Settings (environment variables or make arguments):
#   CONTAINER_TOOL  build/push tool          (default: podman; docker works the same)
#   REGISTRY        registry host            (default: ghcr.io)
#   OWNER           registry owner/namespace (required, no default)
#   VERSION         image tag                (required, no default)
#
# The image is tagged $(REGISTRY)/$(OWNER)/todolist-nuxt:$(VERSION). `make push` is the same as:
#   podman build -t ghcr.io/<you>/todolist-nuxt:1.0 src/todolist-nuxt
#   podman push ghcr.io/<you>/todolist-nuxt:1.0
#
#   OWNER=bennyro-mta VERSION=1.0 make push
#   CONTAINER_TOOL=docker OWNER=me VERSION=1.0 make -C src/todolist-nuxt push

CONTAINER_TOOL ?= podman
REGISTRY       ?= ghcr.io
OWNER          ?=
VERSION        ?=
IMAGE          := todolist-nuxt
IMAGE_REF       = $(REGISTRY)/$(OWNER)/$(IMAGE):$(VERSION)

# The build context is this folder, so `make -C src/todolist-nuxt ...` works from anywhere.
SRC_DIR := $(patsubst %/,%,$(dir $(abspath $(lastword $(MAKEFILE_LIST)))))

.DEFAULT_GOAL := help
.PHONY: help check build push

help:
	@echo "Targets:"
	@echo "  build   build the image"
	@echo "  push    build and push the image"
	@echo "Image:    $(REGISTRY)/$(or $(OWNER),<OWNER>)/$(IMAGE):$(or $(VERSION),<VERSION>)"
	@echo "Tool:     $(CONTAINER_TOOL)"
	@echo "Example:  OWNER=bennyro-mta VERSION=1.0 make push"

check:
	@test -n "$(OWNER)"   || { echo "OWNER is not set (e.g. OWNER=bennyro-mta VERSION=1.0 make push)" >&2; exit 1; }
	@test -n "$(VERSION)" || { echo "VERSION is not set (e.g. OWNER=bennyro-mta VERSION=1.0 make push)" >&2; exit 1; }

build: check
	$(CONTAINER_TOOL) build -t $(IMAGE_REF) $(SRC_DIR)

push: build
	$(CONTAINER_TOOL) push $(IMAGE_REF)
