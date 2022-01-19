import mintapi
from flask import Flask, request, make_response, jsonify
import os
from datetime import datetime
from pytz import timezone
from google.cloud import bigquery
import pyarrow
#from dotenv import load_dotenv #use for env files

#set timestamps
los_angeles = timezone('America/Los_Angeles')
latime = datetime.now(los_angeles)
servertime = datetime.now()
timestampforpartition = latime

#set globals
# username, password, and imap password stored in Cloud Run Environment Variables, will use split() method to convert to tuples
user1 = os.environ.get('user1','Specified Environment Variable Not Set').split(',')
user2 = os.environ.get('user2','Specified Environment Variable Not Set').split(',')
user3 = os.environ.get('user3','Specified Environment Variable Not Set').split(',')
accounts_to_check = [user1, user2, user3] #store accounts as a list
#name of the big query table
table_id = os.environ.get('bqtableid','Specified Environment Variable Not Set')

#construct a bigquery client
client = bigquery.Client()

#make instance of Flask
app = Flask(__name__)

# route called by user with username
@app.route('/')

def index() : # function called by the '/' route
    print('assigning accounts...')
    print('first, if there is a partition in here for today already, delete it and this new one will replace it.') #allows for multiple refresh of a ledger through the day (e.g. hourly), but only keeps the most current one 
    delete_current_query = '''
        DELETE from `{}` where date(partitiontime) = date('{}')
        '''.format(table_id,timestampforpartition)
    del_query_job = client.query(delete_current_query)

    print('checking the accounts')
    for account in accounts_to_check :
        username = account[0]
        pw = account[1]
        imappw = account[2]
        
        print('creating mint object')
        #create mintapi object
        mint = mintapi.Mint( 
            username,
            pw,
            use_chromedriver_on_path=True, #remove for testing, keep for server use
            headless=True, #remove for testing, keep for server use
            mfa_method='email',
            imap_server='imap.gmail.com',
            imap_account=username,
            imap_password=imappw,
            imap_folder='INBOX'
            )

        #get transactions into a dataframe
        print('getting transactions')
        transactions = mint.get_transactions() #creates a dataframe
        #close mint connection
        mint.close()

        #prep data frame with required columns for import by defining columns of dataframe
        columns = ['date','description','original_description','amount','transaction_type','category','account_name','labels','notes']
        transactions = transactions[columns]
        #add the account field to be the email username of mint account (esp for multiple account)
        transactions['account'] = username

        #<---------upload the dataframe to bigquery------->

        #big query job config
        job_config = bigquery.LoadJobConfig(
            schema = [
                bigquery.SchemaField("date","DATE",mode="NULLABLE"),
                bigquery.SchemaField("description","STRING",mode="NULLABLE"),
                bigquery.SchemaField("original_description","STRING",mode="NULLABLE"),
                bigquery.SchemaField("amount","FLOAT",mode="NULLABLE"),
                bigquery.SchemaField("transaction_type","STRING",mode="NULLABLE"),
                bigquery.SchemaField("category","STRING",mode="NULLABLE"),
                bigquery.SchemaField("account_name","STRING",mode="NULLABLE"),
                bigquery.SchemaField("labels","STRING",mode="NULLABLE"),
                bigquery.SchemaField("notes","STRING",mode="NULLABLE"),
                bigquery.SchemaField("account","STRING",mode="NULLABLE"),
            ],
            write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
        )

        #get before and after table rows
        table = client.get_table(table_id)
        rows_before = table.num_rows #store number of rows before the job completes

        #Make an API request and run the load job
        load_job = client.load_table_from_dataframe(transactions,table_id,job_config=job_config)
        print('Now uploading to bigquery')
        load_job.result() #waits for the job to complete
        rows_after = table.num_rows #store number of rows after the job completes

        success_message = "table {}: Previous ({} Rows) | Current ({} Rows)".format(table_id,rows_before,rows_after)

        #now update partitiontime
        update_partitiontime = '''
            UPDATE `{}` SET partitiontime = '{}' where partitiontime is null
            '''.format(table_id,timestampforpartition)
        update_part_job = client.query(update_partitiontime)

        print(success_message, ' | Now moving on to next account...')

    #return the success messages
    return 'Process Completed!'

if __name__ == "__main__" : #for local testing
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
