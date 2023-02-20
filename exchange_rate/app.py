import json
from datetime import datetime
import uuid
import boto3
from flask_lambda import FlaskLambda
import xml.etree.ElementTree as ET
import requests

DATE_FORMATE = "%Y-%m-%d"

app = FlaskLambda(__name__)
ddb = boto3.resource('dynamodb')
table = ddb.Table('exchange')

@app.route('/exchange_rate')
def index():
    '''
        Simple API to return exchange rate with difference in json format.`
    '''
    current_date = datetime.now().date()
    table_data = table.scan()
    if table_data.get("Count") == 0:
        # For the first time only when stack is initialized and there is no data in the db.
        get_last_two_days_exchange_rate()
    
    table_data = table.scan()

    resposne_payload = filter(lambda x: datetime.strptime(x.get('created_at'), DATE_FORMATE).date() == current_date, table_data.get('Items'))
    
    return {
        "response": json.dumps(list(resposne_payload)),
        "status_code": 200,
        'Content-Type': 'application/json'
    }
    

def lambda_exchange_rate_udpate(event, context):
    ''' 
        Lambda function to update the exchange rate. This function will be called by Perodic task to udpate the exchange rate.

        Parameters
        --------------
        event: dict requied
        context: object required

        Return
        -------------
        API Gateway
    '''
        
    get_last_two_days_exchange_rate()
    return {
        "status_code": 200,
        "message": "Exchange rate updated successfully"
    }

def get_last_two_days_exchange_rate():
    '''
        Make API call to retirve 90 days data and prase different between currnet and last day exchange rate.
        This method also inserts record into Dynamo db.
        Returns
         None
    '''
    # This endpoint provides 90 days exchange rate in xml format
    exchange_rate_request = requests.get("https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist-90d.xml?ec753c46f8ac370650a1e9f44584d93b")

    exchange_rate_request.raise_for_status()

    exchange_rate_root = ET.fromstring(exchange_rate_request.content)

    previous_90_days_rate = list(exchange_rate_root.find('{http://www.ecb.int/vocabulary/2002-08-01/eurofxref}Cube'))

    current_day_rate = previous_90_days_rate[0]
    last_day_rate = previous_90_days_rate[1]

    exchange_rate_time_stamp = current_day_rate.attrib['time']
    today_date = datetime.now().strftime(DATE_FORMATE)

    for current_rate, last_rate in zip(current_day_rate, last_day_rate):
        parsed_last_rate = float(last_rate.attrib['rate'])
        parsed_current_rate = float(current_rate.attrib['rate'])
        diff = parsed_current_rate - parsed_last_rate
        table.put_item(Item={
            "id": str(uuid.uuid4()),
            "currency": current_rate.attrib["currency"],
            "current_rate": current_rate.attrib["rate"],
            "diff_from_last_day": f"{diff:.3f}",
            "created_at": today_date,
            "api_time_stamp": exchange_rate_time_stamp
        })

