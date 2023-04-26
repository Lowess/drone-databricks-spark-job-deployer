.PHONY: plugin release

VERSION ?= latest

plugin:
	@echo "Building Drone plugin (export VERSION=<version> if needed)"
	docker build . -t lowess/drone-databricks-spark-job-deployer:$(VERSION)

	@echo "\nDrone plugin successfully built! You can now execute it with:\n"
	@sed -n '/docker run/,/drone-databricks-spark-job-deployer/p' README.md

release:
	@echo "Pushing Drone plugin to the registry"
	docker push lowess/drone-databricks-spark-job-deployer:$(VERSION)
