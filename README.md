drone-databricks-spark-job-deployer
===================================

Deploy a Spark Job to Databricks

# :notebook: Usage

* At least one example of usage

```yaml
---

pipeline:
    step:
        name: Deploy a Spark Job to Databricks
        image: lowess/drone-databricks-spark-job-deployer
        settings:
            workspace: https://your-company.cloud.databricks.com
            api_token:
                from_secret: databricks_api_token
            cluster_name: STAGE_demo_job
            job_settings:
                spark_version: "11.3.x-scala2.12",
                node_type_id: "m5.2xlarge",
                num_workers: 1,
                docker_image: "",
                log_destination_s3: "s3://company-databricks/demo/logs",
                init_scripts_destination_s3: "s3://company-databricks/init_scripts/bootstrap.sh"
                spark_env:
                    ENV_FOR_DYNACONF: "staging",
                    CLUSTER_NAME: "STAGE_demo_job"
                    DATABRICKS_API_TOKEN:
                        from_secret: databricks_api_token
                tags:
                    Billing: "STAGE_va_tapas_inference_page_ctc"
                    Owner": "dev@company.com"
                    Business: "DataEngineering"
                aws_attributes:
                    first_on_demand: 1,
                    availability: "SPOT_WITH_FALLBACK"
                    zone_id: "us-east-1b"
                    instance_profile_arn: "arn:aws:iam::12345678910:instance-profile/DatabricksSpark"
                    spot_bid_price_percent: 100
                    ebs_volume_type: "THROUGHPUT_OPTIMIZED_HDD"
                    ebs_volume_count: 1
                    ebs_volume_size: 500

...
```

---

# :gear: Parameter Reference


* `workspace` _(required)_
  * The Databricks workspace to deploy to (eg. https://your-company.cloud.databricks.com)

* `api_token` _(required)_ (:lock: secret)
  * The Databricks API Token to interract with your workspace

* `cluster_name` _(required)_
  * The Databricks cluster to deploy the job to

* `job_settings` _(required)_
  * The Databricks job settings (follows the spec defined by [Databricks Job API 2.0](https://docs.databricks.com/dev-tools/api/2.0/jobs.html#jobs-api-20))

    * `spark_version` (_str_)
    * `node_type_id` (_str_)
    * `num_workers` (_str_)
    * `docker_image` (_str_)
    * `log_destination_s3` (_str_)
    * `init_scripts_destination_s3` (_str_)
    * `spark_env` (_object_)
      * `key` is used as environment variable name and `value` its value)
    * `tags` (_object_)
      * `key` is the tag name and `value` its value
    * `aws_attributes` (_object_)
      * Follows Databricks [AwsAttributes](https://docs.databricks.com/dev-tools/api/latest/clusters.html#awsattributes) settings
    * `spark_python_task` (_optional str_ defaults to `file:/app/run.py`)
    * `max_retries` (_optional int_ defaults to `-1`)
    * `max_concurrent_runs` (_optional int_ defaults to `2`)

---

# :beginner: Development

* Run the plugin directly from a built Docker image:

```bash
export DATABRICKS_API_TOKEN=dapi...

docker run -i \
    -v $(pwd)/plugin:/opt/drone/plugin \
    -e PLUGIN_WORKSPACE=https://your-company.cloud.databricks.com \
    -e PLUGIN_CLUSTER_NAME=STAGE_va_tapas_inference_page_ctc \
    -e PLUGIN_API_TOKEN=${DATABRICKS_API_TOKEN} \
    -e PLUGIN_JOB_SETTINGS='{"spark_version": "11.3.x-scala2.12", ... }'
    lowess/drone-databricks-spark-job-deployer
```
