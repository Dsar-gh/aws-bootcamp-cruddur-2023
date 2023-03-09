# Week 2 — Distributed Tracing

## Required Homework

### HoneyComb

- We added the following packages in [`requirements.txt`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/requirements.txt) to instrument our Flask app with OpenTelemetry.
```txt
opentelemetry-api 
opentelemetry-sdk 
opentelemetry-exporter-otlp-proto-http 
opentelemetry-instrumentation-flask 
opentelemetry-instrumentation-requests
```
To install these packages, we run the following command :

```sh
pip install -r requirements.txt
```
- To create and initialize a tracer and Flask instrumentation to send data to Honeycomb we added the following lines in the [`app.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/app.py) file.
```python
# HoneyComb 
from opentelemetry import trace
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
```

```python
# Initialize tracing and an exporter that can send data to Honeycomb
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter())
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

app = Flask(__name__)

# HoneyComb
# Initialize automatic instrumentation with Flask
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()
```
- We added the following Environment Variables to the `backend-flask` service in the [`docker-compose.yml`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) file. 

```yml
OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
OTEL_SERVICE_NAME: "${HONEYCOMB_SERVICE_NAME}"
```

- We can find The `HONEYCOMB_API_KEY` in our Honeycomb account. Then we should export it as follows: 
```sh
export HONEYCOMB_API_KEY=""
export HONEYCOMB_SERVICE_NAME="Cruddur"
gp env HONEYCOMB_API_KEY=""
gp env HONEYCOMB_SERVICE_NAME="Cruddur"
```
I faced a problem while trying to run the containers in the `docker-compose.yml` file using the right click on `compose up`. The HONEYCOMB environment variables are not found. 
![The env Vars not found](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week2/can%20not%20send%20to%20honeycomb.PNG)

The Gitpod documentation [here](https://www.gitpod.io/docs/configure/projects/environment-variables) tells us to beware that `gp env`command does not modify our current terminal session, but rather persists this variable for the next workspace on this repository. Therefore, I run the command `gp env` in a terminal using `-e`. 
```sh
gp env -e HONEYCOMB_API_KEY=""
```
- After that I was able to see the data sent to Honeycomb.
![Working Honeycomb](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week2/working%20honeycomb.PNG)


### AWS X-Ray

#### Instrumenting AWS X-Ray for Backend Flask Application
We added the following package to the [`requirements.txt`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/requirements.txt) and installed it using `pip install -r requirements.txt`.

```py
aws-xray-sdk
```

Then modified the [`app.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/app.py) file to import and configure AWS X-Ray .

```py
from aws_xray_sdk.core import xray_recorder
from aws_xray_sdk.ext.flask.middleware import XRayMiddleware 
```
```py
xray_url = os.getenv("AWS_XRAY_URL")
xray_recorder.configure(service='backend-flask', dynamic_naming=xray_url)
```
```py
app = Flask(__name__)
XRayMiddleware(app, xray_recorder)
```

We added the [`aws/json/xray-sampling-rule.json`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/aws/json/xray.json) file.

```json
{
  "SamplingRule": {
      "RuleName": "Cruddur",
      "ResourceARN": "*",
      "Priority": 9000,
      "FixedRate": 0.1,
      "ReservoirSize": 5,
      "ServiceName": "backend-flask",
      "ServiceType": "*",
      "Host": "*",
      "HTTPMethod": "*",
      "URLPath": "*",
      "Version": 1
  }
}
```

We run this command to create a log group inside AWS X-Ray.
```sh
aws xray create-group \
   --group-name "Cruddur" \
   --filter-expression "service(\"backend-flask\")"
```
To create the sampling rule we run this command.
```sh
aws xray create-sampling-rule --cli-input-json file://aws/json/xray-sampling-rule.json
```
Verfiying within the AWS Console.
![create sampling](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week2/sampling-rule-created.PNG)

#### Configuring and provisioning X-Ray daemon within docker-compose and send data back to X-Ray API
We added a `xray-daemon` Service in the [`docker-compose.yml`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) file.
```yml
  xray-daemon:
    image: "amazon/aws-xray-daemon"
    environment:
      AWS_ACCESS_KEY_ID: "${AWS_ACCESS_KEY_ID}"
      AWS_SECRET_ACCESS_KEY: "${AWS_SECRET_ACCESS_KEY}"
      AWS_REGION: "eu-south-1"
    command:
      - "xray -o -b xray-daemon:2000"
    ports:
      - 2000:2000/udp
```
We added the following Environment Variables to the `backend-flask` service in the  [`docker-compose.yml`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) file.
```yml
      AWS_XRAY_URL: "*4567-${GITPOD_WORKSPACE_ID}.${GITPOD_WORKSPACE_CLUSTER_HOST}*"
      AWS_XRAY_DAEMON_ADDRESS: "xray-daemon:2000"
```

#### Observing X-Ray traces within the AWS Console
![working x-ray](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week2/traces-xray.PNG)

#### Adding AWS X-Ray subsegmnets
- By adding a line of code with the capture method in the [`app.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/app.py) file which creates X-Ray subsegment for synchronous functions
```py
@xray_recorder.capture('activities_home')
``` 

## Homework Challenges 

### Honeycomb Manual Instrumentation
 In the required homework, we initialized an automatic instrumentation with our Flask-app. Here we added a manual instrumentation by modifying the [`home_activities.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/home_activities.py) file creating a Tracer then adding attributes and adding a custom span as follows:
 
 ```py
from opentelemetry import trace
tracer = trace.get_tracer("home.Activities") 
```
```py
with tracer.start_as_current_span("home-activites-mock-data"):
    span = trace.get_current_span() 
    now = datetime.now(timezone.utc).astimezone()
    span.set_attribute("app.now", now.isoformat()) 
```
```py
span.set_attribute("app.result_length", len(results))
```
![added span](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week2/added-span.PNG)

I tried as well to Run Query.
![run query](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week2/run-query.PNG)
