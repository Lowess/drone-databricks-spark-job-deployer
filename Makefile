.PHONY: plugin release

VERSION ?= latest
REPO ?= lowess/drone-databricks-spark-job-deployer

plugin:
	@echo "Building Drone plugin (export VERSION=<version> if needed)"
	docker buildx build --platform linux/amd64 . -t $(REPO):$(VERSION)

	@echo "\nDrone plugin successfully built! You can now execute it with:\n"
	@sed -n '/docker run/,/drone-databricks-spark-job-deployer/p' README.md

release:
	@echo "Pushing Drone plugin to the registry"
	docker buildx build --platform linux/amd64 . -t $(REPO):$(VERSION) --push
