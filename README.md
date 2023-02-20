# exchange-rate-api

This project contains source code and supporting files for a serverless application that you can deploy with the SAM CLI.

- exchange_rate - Code for the application's Lambda function.
- events - Invocation events that you can use to invoke the function.
- template.yaml - A template that defines the application's AWS resources.

The application uses several AWS resources, including Lambda functions, an API Gateway API, DynamoDB, and Scheduler. These resources are defined in the `template.yaml` file in this project.

## Approach
The appliation cotains one endpoint which will only accept `GET` request and return current exchange rate and their changes to previous day. API will only populate data into Dynamodb if there is no data in it. The only case when Dynamodb will be empty is if stack is deployed for the first time.

There is a function named `get_last_two_days_exchange_rate` which loads data from an API endpoint in XML formate. The data contains last 90 days exchange rate including today rate. From the API only first two days rate is read and processed to generated desired result. The function also stores the data into the DynamoDB to be used by API endpoint. This function is executed by API if stack if deployed for the firs time and once daily by scheduler.



## Deploy the application

1. Create a virtualenv `virtualenv venv`.
2. Install requirements in `exchange_rate` folder.
3. Install aws sam cli in the virtualenv `pip install aws-sam-cli`
4. Install aws cli in the virtualenv `pip install awscli`
5. Set aws Key id and secret key through `aws configure`
6. To build the application run this command `sam build`
7. To deploy the application run this command `sam deploy --guided`. Follow the instruction to complete the deployment.
8. After deployment, check the console for `ExchangeRateApi` output value. It will provide the endpoint for this.