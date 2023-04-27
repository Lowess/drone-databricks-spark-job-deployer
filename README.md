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
      job_name: demo_job
      job_settings:
        max_retries: -1
        max_concurrent_runs: 2
        spark_python_task:
          python_file: file:/app/run.py
        new_cluster:
          spark_version: 11.3.x-scala2.12
          node_type_id: m5.2xlarge
          num_workers: 1
          docker_image:
            url: registry/demo-spark-job
          cluster_log_conf:
            s3:
              destination: s3://company-databricks/demo/logs
              region: us-east-1
          init_scripts:
            - s3:
                destionation: s3://company-databricks/init_scripts/bootstrap.sh
                region: us-east-1
          spark_env:
            ENV_FOR_DYNACONF: staging
          tags:
            Billing: databricks-stage
            Owner": dev@company.com
            Business: DataEngineering
          aws_attributes:
            first_on_demand: 1
            availability: SPOT_WITH_FALLBACK
            zone_id: us-east-1b
            instance_profile_arn: arn:aws:iam::12345678910:instance-profile/DatabricksSpark
            spot_bid_price_percent: 100
            ebs_volume_type: THROUGHPUT_OPTIMIZED_HDD
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

* `job_name` _(required)_
  * The name of the Databricks job to create. The cluster name will use the job name

* `job_settings` _(required)_
  * The Databricks job settings (follows the spec defined by [Databricks Job API 2.0](https://docs.databricks.com/dev-tools/api/2.0/jobs.html#jobs-api-20))


---

# :beginner: Development

* Run the plugin directly from a built Docker image:

```bash
export DATABRICKS_API_TOKEN=dapi...

docker run -i \
    -v $(pwd)/plugin:/opt/drone/plugin \
    -e PLUGIN_WORKSPACE=https://your-company.cloud.databricks.com \
    -e PLUGIN_CLUSTER_NAME=demo_job \
    -e PLUGIN_API_TOKEN=${DATABRICKS_API_TOKEN} \
    -e PLUGIN_JOB_SETTINGS=$(jq -r tostring /tmp/job-settings.json)  \
    lowess/drone-databricks-spark-job-deployer
```
