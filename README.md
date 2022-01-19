# mintapi_to_bq

A Docker Image for Google Cloud Run that pulls transactions into Google Cloud's petabyte datawarehouse: BigQuery. This uses [mintapi](https://github.com/mintapi/mintapi), a Mint-scraping library to capture the transaction data from Mint.com.

## Preqrequisites

Prior to deploying this into a container in Google Cloud run, you must configure the following:

### 1. BigQuery

You'll need to set up a bigquery table inside a working project in Google Cloud Services. It's best to set up the table inside the same project the script will be running from (otherwise you will need to customize and configure permissions between projects)


#### Bigquery Table and Schema
The easiest way to do this is through the [bigquery console](https://cloud.google.com/bigquery/docs/tables#console) and selecting 'Edit As Text' when creating the schema.

Here is a sample schema (copy and paste into Bigquery)
```
[
      {
        "description": "Timestamp of when this partition was delivered from Mint to Bigquery",
        "name": "partitiontime",
        "type": "TIMESTAMP",
        "mode" : NULLABLE
      },
      {
        "description": "Date of Transaction",
        "name": "date",
        "type": "DATE",
        "mode" : NULLABLE
      },
      {
        "description": "Changed Description of Transaction (edited in Mint)",
        "name": "description",
        "type": "STRING",
        "mode" : NULLABLE
      },
      {
        "description": "Original description of transaction.",
        "name": "original_description",
        "type": "STRING",
        "mode" : NULLABLE
      },
      {
        "description": "amount",
        "name": "amount",
        "type": "FLOAT",
        "mode" : NULLABLE
      },
      {
        "description": "debit or credit",
        "name": "transaction_type",
        "type": "STRING",
        "mode" : NULLABLE
      },
      {
        "description": "category selected",
        "name": "category",
        "type": "STRING",
        "mode" : NULLABLE
      },
      {
        "description": "name of the account",
        "name": "account_name",
        "type": "STRING",
        "mode" : NULLABLE
      },
      {
        "description": "any labels (space delimited)",
        "name": "labels",
        "type": "STRING",
        "mode" : NULLABLE
      },
      {
        "description": "any notes",
        "name": "notes",
        "type": "STRING",
        "mode" : NULLABLE
      },
      {
        "description": "if pulling multiple accounts into this bigquery table, username",
        "name" : "account",
        "type": "STRING",
        "mode" : NULLABLE
      }
]
  ```

  Store the entire table name (eg. `projectname.datasetname.tablename`) in the container environment variable as `bqtableid`.

  ### 2. SMTP access to Email accounts for MFA

  As referenced in mintapi [README.md](https://github.com/mintapi/mintapi#readme)

## Deploying the Image into Google Cloud Run

### Step-by-Step
*many of the following are done in the GCS UX Cloud Console, but you can do many of this from Google Cloud Shell command line*
1. Ensure that Cloud Run, Artifact Registry APIs [are enabled](https://cloud.google.com/endpoints/docs/openapi/enable-api).
2. Open [Google Cloud Shell](https://cloud.google.com/shell/docs/running-gcloud-commands)
3. Clone this repository
4. Navigate into the cloned repository
5. Trigger the deployment with `gcloud run deploy`
6. Hit Enter to select the current source as the directory you are in.
7. Enter a service name (press enter to accept default name provided)
8. After Successful deployment, open the Cloud Run Console
9. Edit your service instance in [Cloud Run Console](https://cloud.google.com/filestore/docs/editing-instances#cloud-console) by clicking **"Edit and Deploy New Version"**
10. Scroll down to *Capacity* and change Memory to **2GiB** and CPU to **2**
11. *Define Env Variables* Select the **Variables and Secrets** tab and enter your Mint Accounts in this format
- **Name** : user1
- **Value** : mintusername,mintpassword,imappassword
- Repeat this for up to 3 mint user accounts (do not use quotes)
12. *Define Env Variables* Create a environment variable for your bigquery table name
- **Name** : bqtableid
- **Value** : projectname.datasetname.table

### Scheduling through Google Cloud Scheduler
Use [Google Cloud Scheduler](https://cloud.google.com/scheduler/docs/quickstart) to trigger Chron Jobs to send a GET command to the service URL provided on deploy.
