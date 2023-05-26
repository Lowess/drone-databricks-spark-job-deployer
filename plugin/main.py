#!/usr/bin/env python

"""Deploy a Spark Job to Databricks."""

import json
import os
import sys
from json import JSONDecodeError
from typing import List

import requests
from plugin import dronecli, logger


class DatabricksSparkJobDeployerException(Exception):
    """Raised when the spark deployer job fails"""

    pass


class DatabricksInvalidJobSettings(Exception):
    """Raised when Job settings are not valid"""

    pass


class DatabricksSparkJobDeployer:
    """
    DatabricksSparkJobDeployer
    """

    def __init__(self, workspace, api_token):
        """Create a DatabricksSparkJobDeployer."""
        self._workspace = workspace
        self._api_token = api_token

    def _call_job_api(self, method: str, action: str, data=None):
        endpoint = f"{self._workspace}/api/2.0/jobs/{action}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_token}",
        }
        response = None
        if method == "GET":
            response = requests.get(endpoint, headers=headers)
        elif method == "POST":
            response = requests.post(endpoint, headers=headers, data=data)
        response.raise_for_status()
        return response.json()

    def get_job_ids(self, cluster_name: str) -> List[str]:
        """
        Collect Job ids running in a given cluster

        :params str cluster_name: The name of the cluster to retrieve jobs from
        """
        response = self._call_job_api(method="GET", action="list")
        job_ids = []
        for job in response["jobs"]:
            if job["settings"]["name"] == cluster_name:
                job_ids.append(job["job_id"])
        return job_ids

    def reset_job(self, job_id, settings):
        data = {"job_id": job_id, "new_settings": settings}
        return self._call_job_api(method="POST", action="reset", data=json.dumps(data))

    def create_job(self, settings):
        return self._call_job_api(
            method="POST", action="create", data=json.dumps(settings)
        )["job_id"]

    def run_job(self, job_id):
        data = {"job_id": job_id}
        return self._call_job_api(
            method="POST", action="run-now", data=json.dumps(data)
        )

    def expand_environment_variables(self, env_vars_map):
        expanded_env_vars = {}
        for k, v in env_vars_map.items():
            if v[0:1] == "$" and v[1:].isupper():
                try:
                    expanded_env_vars[k] = os.environ[v[1:]]
                    logger.info(
                        f"{k} was expanded successfully from environment variable {v}"
                    )
                except KeyError:
                    raise DatabricksInvalidJobSettings(
                        f"Access to undefined environment variable {v[1:]} while parsing spark_env_vars. "
                        "The variable should be added to the plugin environment definition to be accessible."
                    )

            else:
                expanded_env_vars[k] = v
        return expanded_env_vars

    def configure_job_settings(self, **settings):
        try:
            return {
                "name": settings["name"],
                "new_cluster": settings["new_cluster"],
                "max_retries": settings["max_retries"],
                "max_concurrent_runs": settings["max_concurrent_runs"],
                "spark_python_task": settings["spark_python_task"],
            }

        except KeyError as e:
            raise DatabricksInvalidJobSettings(
                f"{e} is missing from the Job specification and is mandatory, please refer to https://docs.databricks.com/dev-tools/api/2.0/jobs.html#request-structure"
            )

    def __repr__(self):
        """Representation of an DatabricksSparkJobDeployer object."""
        return "<{} 'workspace': {}>".format(self.__class__.__name__, self._workspace)

    def setup(self):
        """Main plugin logic."""
        # TODO
        pass


def main():
    """The main entrypoint for the plugin."""

    try:
        workspace = dronecli.get("PLUGIN_WORKSPACE")
        api_token = dronecli.get("PLUGIN_API_TOKEN")
        dry_run = dronecli.get("PLUGIN_DRY_RUN", False)

        # Spark job name
        job_name = dronecli.get("PLUGIN_JOB_NAME")

        # Spark job settings
        try:
            job_settings = json.loads(dronecli.get("PLUGIN_JOB_SETTINGS"))
            job_settings["name"] = job_name
        except JSONDecodeError:
            raise DatabricksInvalidJobSettings(
                "job_settings is not a valid Json parsable object"
            )

        plugin = DatabricksSparkJobDeployer(  # isort:skip
            workspace=workspace, api_token=api_token
        )

        logger.info(f"The drone plugin has been initialized with: {plugin}")

        logger.info("Parsing job settings...")
        job_settings = plugin.configure_job_settings(**job_settings)
        logger.info(
            f"The job will be submited with the following settings:\n{json.dumps(job_settings, indent=4)}"
        )

        # Expand env vars stored in spark_env_vars
        job_settings["new_cluster"][
            "spark_env_vars"
        ] = plugin.expand_environment_variables(
            job_settings["new_cluster"].get("spark_env_vars", {})
        )

        job_ids = plugin.get_job_ids(cluster_name=job_name)
        job_id = None

        if len(job_ids) == 0:
            # Job Creation
            logger.info(f"No job '{job_name}' found in cluster. Creating new job...")

            if dry_run:
                logger.info("[dry run] create_job would have been exectued")
            else:
                job_id = plugin.create_job(settings=job_settings)

        elif len(job_ids) == 1:
            # Job Reset
            logger.info(
                f"Found job ID {job_ids} in cluster matching '{job_name}'. Resetting job with new settings..."
            )
            job_id = job_ids[0]

            response = None
            if dry_run:
                logger.warning(
                    f"[dry run] reset_job would have been exectued on job {job_id}"
                )
                response = {}
            else:
                response = plugin.reset_job(job_id=job_id, settings=job_settings)

            if response != {}:
                raise DatabricksSparkJobDeployerException(
                    f"Resetting old run failed ({response}) ! New run will not start!"
                )
        else:
            raise DatabricksSparkJobDeployerException(
                f"More than one job named '{job_name}' found in cluster: {job_ids}. Aborting deployment..."
            )

        if dry_run:
            logger.warning(
                f"[dry run] run_job would have been exectued on job {job_id}"
            )
        else:
            run_job_response = plugin.run_job(job_id=job_id)

            logger.info(
                f"New run has been scheduled for {job_id}, run details: {run_job_response}"
            )

    except Exception as e:
        logger.error(f"{type(e).__name__} error raised while executing the plugin: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
