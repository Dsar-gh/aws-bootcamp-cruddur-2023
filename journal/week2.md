# Week 2 — Distributed Tracing

## Required Homework

### Instrumenting with Honeycomb

- We added the following packages in [`requirements.txt`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/requirements.txt) to instrument our Flask application `app.py` with Honeycomb's OpenTelemetry distributions.
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
I added the following package to the [`requirements.txt`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/requirements.txt) and installed it using `pip install -r requirements.txt`.

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
- By adding a line of code with the `capture` method in the [`app.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/app.py) file which creates X-Ray subsegment for synchronous functions

![capture](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week2/Capture-method.PNG)

- Then I added a subsegment in the run() function in the [`notifications_activities.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/notifications_activities.py) service.
```py
from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder

class NotificationsActivities:
  def run():
    # xray 
      try:
      now = datetime.now(timezone.utc).astimezone()
      results = [{
        'uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
        'handle':  'Lloyd',
        'message': 'I am a Ninja',
        'created_at': (now - timedelta(days=2)).isoformat(),
        'expires_at': (now + timedelta(days=5)).isoformat(),
        'likes_count': 5,
        'replies_count': 1,
        'reposts_count': 0,
        'replies': [{
          'uuid': '26e12864-1c26-5c3a-9658-97a10f8fea67',
          'reply_to_activity_uuid': '68f126b0-1ceb-4a33-88be-d90fa7109eee',
          'handle':  'Worf',
          'message': 'This post has no honor!',
          'likes_count': 0,
          'replies_count': 0,
          'reposts_count': 0,
          'created_at': (now - timedelta(days=2)).isoformat()
        }],
      }
      ]
      
      subsegment = xray_recorder.begin_subsegment('mock-data')
      # xray 
      dict = {
        "now": now.isoformat(),
        "results-size": len(results)
      }
      subsegment.put_metadata('key', dict, 'namespace')
      xray_recorder.end_subsegment()
    finally:  
      # Close the segment
      xray_recorder.end_subsegment()
      
    return results
```
- After adding the the `capture` method and the subsegmnet, we could see that X-Ray traces with segments and subsegments appeared in the AWS X-Ray console.
![xray subsegment](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week2/X-Ray-subsegment.PNG)


### Configuring AWS CloudWatch Logs

#### Installing WatchTower package

- I added the `WatchTower` package to the [`requirements.txt`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/requirements.txt) then installed it using `pip install -r requirements.txt`.
```txt
watchtower
```

- After that I imported the libraries into [`app.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/app.py) file.
```py
import watchtower
import logging
from time import strftime
```
#### Writing a Custom Logger to Send Application Log Data to CloudWatch Log Group.

- Setting up CloudWatch Logs
```py
# Configuring Logger to Use CloudWatch
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
cw_handler = watchtower.CloudWatchLogHandler(log_group='cruddur')
LOGGER.addHandler(console_handler)
LOGGER.addHandler(cw_handler)
LOGGER.info("Test log")
```
- This will log ERRORS to CloudWatch Logs
```py
@app.after_request
def after_request(response):
    timestamp = strftime('[%Y-%b-%d %H:%M]')
    LOGGER.error('%s %s %s %s %s %s', timestamp, request.remote_addr, request.method, request.scheme, request.full_path, response.status)
    return response
```


## Homework Challenges 

### Honeycomb Manual Instrumentation
 In the required homework, I initialized an automatic instrumentation with our Flask-app. Here we added a manual instrumentation by modifying the [`home_activities.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/home_activities.py) file creating a Tracer then adding attributes and adding a custom span as follows:
 
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
