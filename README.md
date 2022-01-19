# mintapi_to_bq

Docker Image for Google Cloud Run that pulls transactions into Google Cloud's petabyte datawarehouse: BigQuery

# Preqrequisites

Prior to deploying this into a container in Google Cloud run, you must configure the following:

## 1. BigQuery

You'll need to set up a bigquery table inside a working project in Google Cloud Services. It's best to set up the table inside the same project the script will be running from (otherwise you will need to customize and configure permissions between projects)


### Bigquery Table and Schema
The easiest way to do this is through the [bigquery console](https://cloud.google.com/bigquery/docs/tables#console). 

Here is a sample schema:
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

  ## 2. SMTP access to Email accounts for MFA

  As referenced in mintapi [README.md](https://github.com/mintapi/mintapi#readme)