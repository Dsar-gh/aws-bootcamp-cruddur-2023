# Week 4 — Postgres and RDS

## Required Homework

### Creating RDS DB Instance

Using the following command, an RDS Instance is created.

```shell
aws rds create-db-instance \
  --db-instance-identifier cruddur-db-instance \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --engine-version 14.6 \
  --master-username root \
  --master-user-password ****** \
  --allocated-storage 20 \
  --availability-zone us-east-1a\
  --backup-retention-period 0 \
  --port 5432 \
  --no-multi-az \
  --db-name cruddur \
  --storage-type gp2 \
  --publicly-accessible \
  --storage-encrypted \
  --enable-performance-insights \
  --performance-insights-retention-period 7 \
  --no-deletion-protection
```
![create rds](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/create-rds.PNG)

Once the RDS Instance is running, I changed its status to temporarily stop to avoid extra cost. This is valid only for 7 days, so it needs to be in check.

![create rds](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/2create-rds.PNG)

### Configuring and using Postgres

This command is used to connect to `psql` via the psql client cli tool.

```
psql -Upostgres --host localhost
```

These are some common PSQL commands will be needed in the following steps.

```sql
\x on -- expanded display when looking at data
\q -- Quit PSQL
\l -- List all databases
\c database_name -- Connect to a specific database
\dt -- List all tables in the current database
\d table_name -- Describe a specific table
\du -- List all users and their roles
\dn -- List all schemas in the current database
CREATE DATABASE database_name; -- Create a new database
DROP DATABASE database_name; -- Delete a database
CREATE TABLE table_name (column1 datatype1, column2 datatype2, ...); -- Create a new table
DROP TABLE table_name; -- Delete a table
SELECT column1, column2, ... FROM table_name WHERE condition; -- Select data from a table
INSERT INTO table_name (column1, column2, ...) VALUES (value1, value2, ...); -- Insert data into a table
UPDATE table_name SET column1 = value1, column2 = value2, ... WHERE condition; -- Update data in a table
DELETE FROM table_name WHERE condition; -- Delete data from a table

```

### Creating a local database

To create a local Database named cruddur inside postgres locally we can directly type the following command.
```sh
createdb cruddur -h localhost -U postgres
```
Or we can first connect to psql then using `sql` command create the DB as follows.

```sh
psql -U postgres -h localhost
```
![create db](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/create-db-local.PNG)

We can create the DB within the PSQL client.

```sql
CREATE database cruddur;
```
To list the DBs or to drop one we can use the following commands.

```sql
\l
DROP database cruddur;
```
![list](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/list-DBs.PNG)


### Adding UUID Extension

- A new SQL file called [`schema.sql`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/db/schema.sql) is created under `backend-flask/db`
- Postgres will generate out UUIDs. Therefore the extension called "uuid-ossp" is added inside the `schema.sql` file as follows.

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

- Running the following command will execute the `SQL` commands in the `db/schema.sql `file on the `cruddur` DB, using the `postgres` user and connecting to the PostgreSQL server running on `localhost`.

```sh
psql cruddur < db/schema.sql -h localhost -U postgres
```

### Setting up the `CONNECTION_URL` and `PROD_CONNECTION_URL` environment variables

 These variables are needed to connect our Cruddur with the DB.
 
```sh
export CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"
gp env CONNECTION_URL="postgresql://postgres:password@localhost:5432/cruddur"

export PROD_CONNECTION_URL="postgresql://root:******@cruddur-db-instance.c26ykveazyqw.us-east-1.rds.amazonaws.com:5432/cruddur"
gp env PROD_CONNECTION_URL="postgresql://root:******@cruddur-db-instance.c26ykveazyqw.us-east-1.rds.amazonaws.com:5432/cruddur"

```

To try connecting with the local DB 
```sh
psql $CONNECTION_URL
# The output should be like this
cruddur=#
```

### Writing Bash Scripts to connect to DB

I created a new folder called [`bin`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/tree/main/backend-flask/bin) to hold all our bash scripts under `backend-flask/`. These Bash Scripts are used to create the cruddur DB, to drop it or to load the schema on the cruddur DB. 

#### [`db-create`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/db-create)

In the new `db-create` file, the following lines are added.

```sh
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-create"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "create database cruddur;"

```
To execute the script.

```sh
./bin/db-create
```

#### [`db-drop`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/db-drop)

In the new `db-drop` file, the following lines are added.

```sh
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-drop"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

NO_DB_CONNECTION_URL=$(sed 's/\/cruddur//g' <<<"$CONNECTION_URL")
psql $NO_DB_CONNECTION_URL -c "drop database cruddur;"
```
To execute the script.

```sh
./bin/db-drop
```

#### [`db-schema-load`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/db-schema-load)

In the new `db-schema-load` file, the following lines are added.

```sh
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-schema-load"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

#schema_path="$(realpath .)/db/schema.sql"
SCRIPT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
schema_path="$SCRIPT_DIR/db/schema.sql"

echo $schema_path

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL cruddur < $schema_path
```

To run the script.
```sh
./bin/db-schema-load
```
![schema-script](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/psql-schema.PNG)


#### [`db-seed`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/db-seed)

In the new `db-seed` file, the following lines are added, to fill the tables in our Cruddur DB with some mock data.

```sh
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-seed"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

#seed_path="$(realpath .)/db/seed.sql"
SCRIPT_DIR="$(dirname "$(dirname "$(readlink -f "$0")")")"
seed_path="$SCRIPT_DIR/db/seed.sql"

echo $seed_path

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL cruddur < $seed_path
```

To run the script.
```sh
./bin/db-seed
```

![seed-script](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/psql-seed.PNG)


#### [`db-connect`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/db-connect)

In the new `db-connect` file, the following lines are added.

```sh
#! /usr/bin/bash

CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-connect"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

psql $URL
```

To run the script.
```sh
./bin/db-connect
```

Now we can inquire information about our Cruddur DB as follows.

```sql
-- To list the tables in our Cruddur DB
\dt
```

```sql
-- To print out all records from the activities table in our Cruddur DB in an expanded display
\x auto
SELECT * FROM activities;
```

#### [`db-sessions`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/db-sessions)

Executing this script will retrieve information about the active connections to the Cruddur DB, including the process ID, the username, the database name, the client IP address, the application name, and the connection state.

```sh
#! /usr/bin/bash
CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-sessions"
printf "${CYAN}== ${LABEL}${NO_COLOR}\n"

if [ "$1" = "prod" ]; then
  echo "Running in production mode"
  URL=$PROD_CONNECTION_URL
else
  URL=$CONNECTION_URL
fi

NO_DB_URL=$(sed 's/\/cruddur//g' <<<"$URL")
psql $NO_DB_URL -c "select pid as process_id, \
       usename as user,  \
       datname as db, \
       client_addr, \
       application_name as app,\
       state \
from pg_stat_activity;"
```

#### [`db-setup`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/db-setup)

Executing this script will setup (reset) everything for our Cruddur DB.

```sh
#! /usr/bin/bash
-e # stop if it fails at any point


CYAN='\033[1;36m'
NO_COLOR='\033[0m'
LABEL="db-setup"
printf "${CYAN}==== ${LABEL}${NO_COLOR}\n"

bin_path="$(realpath .)/bin"


source "$bin_path/db-drop"
source "$bin_path/db-create"
source "$bin_path/db-schema-load"
source "$bin_path/db-seed"
```

To make all these Scripts exeutable the permissions need to be changed to `rwxr--r--` as follows.

```sh
chmod u+x db-create 
chmod u+x db-drop 
chmod u+x db-schema-load 
chmod u+x db-connect 
chmod u+x db-seed 
chmod u+x db-sessions
chmod u+x db-setup
```
### Creating tables in Cruddur DB and adding Seed Data

- The [`schema.sql`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/db/schema.sql) is modified to create tables inside our Cruddur DB as follows.

```sql
CREATE TABLE public.users (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  display_name text,
  handle text,
  cognito_user_id text,
  created_at TIMESTAMP default current_timestamp NOT NULL
);

CREATE TABLE public.activities (
  uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  user_uuid UUID NOT NULL,
  message text NOT NULL,
  replies_count integer DEFAULT 0,
  reposts_count integer DEFAULT 0,
  likes_count integer DEFAULT 0,
  reply_to_activity_uuid integer,
  expires_at TIMESTAMP,
  created_at TIMESTAMP default current_timestamp NOT NULL
);
```

- To add Seed Data into our Cruddur DB a new file [`seed.sql`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/db/seed.sql) under `backend-flask/db` is created as follows.

```sql
INSERT INTO public.users (display_name, handle, cognito_user_id)
VALUES
  ('Andrew Brown', 'andrewbrown' ,'MOCK'),
  ('Andrew Bayko', 'bayko' ,'MOCK');

INSERT INTO public.activities (user_uuid, message, expires_at)
VALUES
  (
    (SELECT uuid from public.users WHERE users.handle = 'andrewbrown' LIMIT 1),
    'This was imported as seed data!',
    current_timestamp + interval '10 day'
  )
```

### Installing the PostgreSQL Adapter for Python (`Psycopg3`)

- I added the following package in [`requirements.txt`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/requirements.txt) and installed it using `pip install -r requirements.txt`. This way the `backend-flask` will be able to run SQL commands on the Cruddur DB.

```txt
psycopg[binary]
psycopg[pool]
```
`psycopg[binary]` and `psycopg[pool]` are installation options for `Psycopg3` that provide additional functionality:

`psycopg[binary]`: This installation option includes support for working with large binary objects (BLOBs) in PostgreSQL, such as images or audio files. If you need to store and retrieve large binary objects in a PostgreSQL database using `Psycopg3`, you should install `psycopg[binary]`.

`psycopg[pool]`: This installation option includes support for connection pooling in PostgreSQL, which can help improve the performance and scalability of your Python application. Connection pooling allows you to reuse database connections across multiple requests, rather than creating a new connection for every request. If you are developing a web application or other high-traffic Python application that needs to interact with a PostgreSQL database, you should consider using `psycopg[pool]`.

- I created a new file under `/backend-flask/lib` called [`db.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/lib/db.py). this will be the connection for your backend

```py
from psycopg_pool import ConnectionPool
import os

def query_wrap_object(template):
  sql = f"""
  (SELECT COALESCE(row_to_json(object_row),'{{}}'::json) FROM (
  {template}
  ) object_row);
  """
  return sql

def query_wrap_array(template):
  sql = f"""
  (SELECT COALESCE(array_to_json(array_agg(row_to_json(array_row))),'[]'::json) FROM (
  {template}
  ) array_row);
  """
  return sql

connection_url = os.getenv("CONNECTION_URL")
pool = ConnectionPool(connection_url)

```

- Then I imported the `psycopg_pool` through our library `db.py` in the [`home_activities.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/home_activities.py) file as follows. 

```py
from lib.db import pool,query_wrap_array
```

And added the following code as well.

```py
sql = """
      SELECT
        activities.uuid,
        users.display_name,
        users.handle,
        activities.message,
        activities.replies_count,
        activities.reposts_count,
        activities.likes_count,
        activities.reply_to_activity_uuid,
        activities.expires_at,
        activities.created_at
      FROM public.activities
      LEFT JOIN public.users ON users.uuid = activities.user_uuid
      ORDER BY activities.created_at DESC
      """
      print(sql)
      span.set_attribute("app.result_length", len(results))
      with pool.connection() as conn:
        with conn.cursor() as cur:
          cur.execute(sql)
          # this will return a tuple
          # the first field being the data
          json = cur.fetchall()
      return json[0]
```

- In the [`docker-compose.yml`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) file I added the `CONNECTIONS_URL` environment variable for the `backend-flask` service as follows.

```yml
      CONNECTION_URL: "postgresql://postgres:password@db:5432/cruddur"
```

### Connecting our Cruddur to RDS DB via Gitpod

- Starting our RDS instance from AWS RDS console.
- Editing security group for our RDS DB instance to accept traffic coming from Gitpod ID by adding `inbound rule`.
- Now verify that the connection is working using `psql $PROD_CONNECTION_URL`

![rds](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/connected-rds.PNG)

- Every time we lunch Gitpod, our IP address will change, therefore we need to modify our security group rule using AWS CLI as follows.
1.  Exporting and saving our `DB_SG_ID` and `DB_SG_RULE_ID` Variables
  ```sh
  export DB_SG_ID="sg-090a88a9e495909ef"
  gp env DB_SG_ID="sg-090a88a9e495909ef"
  export DB_SG_RULE_ID="sgr-05daa92137ee73561"
  gp env DB_SG_RULE_ID="sgr-05daa92137ee73561"
  ```
2.  Under `backend-flask/bin/` a new shell script [`rds-update-sg-rule`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/bin/rds-update-sg-rule) is added and made sure that it's executable `chmod u+x ./bin/rds-update-sg-rule`. It will be executed every time Gitpod is launced.
  
  ```sh
  aws ec2 modify-security-group-rules     --group-id $DB_SG_ID     --security-group-rules "SecurityGroupRuleId=$DB_SG_RULE_ID,SecurityGroupRule={Description=GITPOD,IpProtocol=tcp,FromPort=5432,ToPort=5432,CidrIpv4=$GITPOD_IP/32}"
  ```
3.  The following lines are added  to the `.gitpod.yml`file under `postgres` task to send the new Gitpod IP address to AWS RDS when we launch our workspace in Gitpod.
  
  ```yml
      command: |
        export GITPOD_IP=$(curl ifconfig.me)
        source  "$THEIA_WORKSPACE_ROOT/backend-flask/bin/rds-update-sg-rule"
  ```
  
 - Now we need to change the `CONNECTIONS_URL` environment variable for the `backend-flask` service in the [`docker-compose.yml`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) file to our production RDS DB as follows.

```yml
      CONNECTION_URL: "$PROD_CONNECTION_URL"
```

### Setup Cognito post confirmation lambda

To create Lambda-Congito Trigger when an user signed-up and is inserted into our Cruddur RDS DB.

1. At first I created a new lambda function using AWS console. The setup was done as follows:
  - Author from scratch
  - Provide the function name: `cruddur-post-confirmation`
  - Runtime: `Python3.8`
  - Architecture: `x86_64`

2. After creating our `cruddur-post-confirmation` lambda function I changed its code source in AWS Console then deployed it to be saved. The new code source for lambda function [`cruddur-post-confirmation.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/aws/lambdas/cruddur-post-confirmation.py) is saved as well under `aws/lambdas/` in our Repo.

3. In our `cruddur-post-confirmation` lambda function by clicking on Configuration tab I added the environment variable `CONNECTION_URL` and its value is our RDS DB instance (`PROD_CONNECTION_URL`) as follows:

![env-lambda](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/add-env-lambda.PNG)
   

4. In our `cruddur-post-confirmation` lambda function by clicking on Code  tab I added a lambda Layer by specifying an ARN (`arn:aws:lambda:us-east-1:898466741470:layer:psycopg2-py38:2`) from this [repo](https://github.com/jetbridge/psycopg2-lambda-layer).

![lambda-layer](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/lambda-layer.PNG)


5. I added a lambda trigger using AWS Console, therefore I needed to go to  Amazon Cognito-> user pools -> then to  my `cruddur-user-pool` by clicking on `User pool properties` tab. The lambda trigger is  configured as follows:
  - Tigger Type: `Sign-up`
  - Sign-Up: `Post confirmation Trigger`
  - Assign Lambda function: `cruddur-post-confirmation`

  ![lambda-trigger](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week4/lambda-trigger.PNG)


6. The [`schema.sql`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/db/schema.sql) file is modified that each user have an `email` and changed `handle` to `preferred_username` as follows:

    ```sql
    CREATE TABLE public.users (
      uuid UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
      display_name text NOT NULL,
      --handle text NOT NULL, handle is same as preferred_username
      preferred_username text NOT NULL, -- same as handle, make sure to check lambda function
      email text NOT NULL,
      cognito_user_id text NOT NULL,
      created_at TIMESTAMP default current_timestamp NOT NULL
    );
    ```









