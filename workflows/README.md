## Update workflow

You will only need to update the workflow when the cloud-run-job-workflow.yaml file changes

```sh
gcloud workflows deploy score-workflow \
    --location=us-west1 \
    --source=cloud-run-job-workflow.yaml \
    --service-account workflow-runner@openteams-score.iam.gserviceaccount.com
```

# Exec

Run the workflow

```sh
gcloud workflows run score-workflow --data=''
```
