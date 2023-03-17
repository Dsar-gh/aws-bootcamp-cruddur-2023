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



