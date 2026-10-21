# 🚀 Deployment Guide for Snowflake

This guide provides detailed instructions for deploying the RDF/OWL Visualizer to Snowflake.

## Prerequisites

- Snowflake account with appropriate permissions
- SnowSQL CLI installed (optional, for command-line deployment)
- Access to create:
  - Databases and schemas
  - Stages
  - Streamlit applications
  - Warehouses (or access to existing warehouse)

## Deployment Methods

### Method 1: Using Snowflake UI (Recommended for First-Time Users)

#### Step 1: Prepare Snowflake Environment

1. Log into Snowflake UI
2. Navigate to **Worksheets**
3. Create a new worksheet
4. Copy and paste contents of `snowflake_setup.sql`
5. Execute the script section by section
6. Verify the following are created:
   - Database: `RDF_DB`
   - Schema: `PUBLIC`
   - Warehouse: `RDF_WAREHOUSE`
   - Stage: `RDF_APP_STAGE`

#### Step 2: Upload Application Files

1. In Snowflake UI, navigate to:
   ```
   Data → Databases → RDF_DB → PUBLIC → Stages → RDF_APP_STAGE
   ```
2. Click **+ Files** or **Upload Files** button
3. Select and upload these files:
   - `streamlit_app.py`
   - `rdf_reader.py`
   - `graph_visualizer.py`
   - `rdf_converter.py`
   - `snowflake_writer.py`
   - `requirements.txt`
4. Wait for upload to complete
5. Verify all files are listed

#### Step 3: Create Streamlit Application

1. In the worksheet, execute:
   ```sql
   CREATE STREAMLIT RDF_OWL_VISUALIZER
       ROOT_LOCATION = '@RDF_DB.PUBLIC.RDF_APP_STAGE'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'RDF_WAREHOUSE';
   ```
2. Wait for creation to complete

#### Step 4: Launch Application

1. Navigate to **Apps** → **Streamlit** in Snowflake UI
2. Find **RDF_OWL_VISUALIZER** in the list
3. Click on the application name to launch
4. Wait for initialization (first launch may take 1-2 minutes)

### Method 2: Using SnowSQL CLI

#### Step 1: Connect to Snowflake

```bash
snowsql -a <your_account> -u <your_username>
```

Enter your password when prompted.

#### Step 2: Run Setup Script

```sql
-- Execute setup
!source snowflake_setup.sql
```

Or copy-paste the SQL commands from the file.

#### Step 3: Upload Files

From SnowSQL prompt:

```sql
USE DATABASE RDF_DB;
USE SCHEMA PUBLIC;

PUT file://streamlit_app.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://rdf_reader.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://graph_visualizer.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://rdf_converter.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://snowflake_writer.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file://requirements.txt @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

-- Verify upload
LIST @RDF_APP_STAGE;
```

#### Step 4: Create Application

```sql
CREATE STREAMLIT RDF_OWL_VISUALIZER
    ROOT_LOCATION = '@RDF_DB.PUBLIC.RDF_APP_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'RDF_WAREHOUSE';
```

#### Step 5: Access Application

Launch from Snowflake UI: **Apps** → **Streamlit** → **RDF_OWL_VISUALIZER**

### Method 3: Using Snowflake Python Connector

```python
import snowflake.connector
import os

# Connect
conn = snowflake.connector.connect(
    account='your_account',
    user='your_username',
    password='your_password',
    warehouse='RDF_WAREHOUSE',
    database='RDF_DB',
    schema='PUBLIC'
)

cursor = conn.cursor()

# Create stage if not exists
cursor.execute("CREATE STAGE IF NOT EXISTS RDF_APP_STAGE")

# Upload files
files = [
    'streamlit_app.py',
    'rdf_reader.py',
    'graph_visualizer.py',
    'rdf_converter.py',
    'snowflake_writer.py',
    'requirements.txt'
]

for file in files:
    cursor.execute(f"PUT file://{os.path.abspath(file)} @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE")

# Create Streamlit app
cursor.execute("""
CREATE STREAMLIT IF NOT EXISTS RDF_OWL_VISUALIZER
    ROOT_LOCATION = '@RDF_DB.PUBLIC.RDF_APP_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'RDF_WAREHOUSE'
""")

cursor.close()
conn.close()

print("Deployment complete!")
```

## Post-Deployment Configuration

### 1. Grant Permissions

Grant access to users/roles:

```sql
-- Grant database access
GRANT USAGE ON DATABASE RDF_DB TO ROLE <YOUR_ROLE>;
GRANT USAGE ON SCHEMA RDF_DB.PUBLIC TO ROLE <YOUR_ROLE>;

-- Grant warehouse access
GRANT USAGE ON WAREHOUSE RDF_WAREHOUSE TO ROLE <YOUR_ROLE>;

-- Grant Streamlit access
GRANT USAGE ON STREAMLIT RDF_OWL_VISUALIZER TO ROLE <YOUR_ROLE>;

-- Grant table creation permissions
GRANT CREATE TABLE ON SCHEMA RDF_DB.PUBLIC TO ROLE <YOUR_ROLE>;
GRANT CREATE VIEW ON SCHEMA RDF_DB.PUBLIC TO ROLE <YOUR_ROLE>;
```

### 2. Configure Warehouse Size

Adjust based on expected workload:

```sql
-- For small ontologies (< 10,000 triples)
ALTER WAREHOUSE RDF_WAREHOUSE SET WAREHOUSE_SIZE = 'SMALL';

-- For medium ontologies (10,000 - 100,000 triples)
ALTER WAREHOUSE RDF_WAREHOUSE SET WAREHOUSE_SIZE = 'MEDIUM';

-- For large ontologies (> 100,000 triples)
ALTER WAREHOUSE RDF_WAREHOUSE SET WAREHOUSE_SIZE = 'LARGE';
```

### 3. Set Auto-Suspend

To reduce costs:

```sql
ALTER WAREHOUSE RDF_WAREHOUSE SET AUTO_SUSPEND = 300; -- 5 minutes
ALTER WAREHOUSE RDF_WAREHOUSE SET AUTO_RESUME = TRUE;
```

## Updating the Application

### When You Make Changes to Code

1. **Upload Updated Files:**
   ```sql
   PUT file://streamlit_app.py @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
   -- Repeat for any other modified files
   ```

2. **Recreate the Streamlit App:**
   ```sql
   DROP STREAMLIT RDF_OWL_VISUALIZER;
   
   CREATE STREAMLIT RDF_OWL_VISUALIZER
       ROOT_LOCATION = '@RDF_DB.PUBLIC.RDF_APP_STAGE'
       MAIN_FILE = 'streamlit_app.py'
       QUERY_WAREHOUSE = 'RDF_WAREHOUSE';
   ```

3. **Or Use ALTER (if supported):**
   ```sql
   ALTER STREAMLIT RDF_OWL_VISUALIZER REFRESH;
   ```

## Monitoring and Maintenance

### Check Application Status

```sql
-- Show Streamlit apps
SHOW STREAMLIT IN SCHEMA RDF_DB.PUBLIC;

-- Check warehouse usage
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.WAREHOUSE_METERING_HISTORY
WHERE WAREHOUSE_NAME = 'RDF_WAREHOUSE'
ORDER BY START_TIME DESC
LIMIT 100;
```

### Monitor Query Performance

```sql
-- Check query history
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.QUERY_HISTORY
WHERE USER_NAME = CURRENT_USER()
  AND START_TIME >= DATEADD(DAY, -1, CURRENT_TIMESTAMP())
ORDER BY START_TIME DESC
LIMIT 50;
```

### Clean Up Old Data

```sql
-- Clean up data older than 30 days
CALL CLEANUP_OLD_ONTOLOGIES(30);

-- Or manually
DELETE FROM RDF_TRIPLES WHERE CREATED_AT < DATEADD(DAY, -30, CURRENT_TIMESTAMP());
```

## Troubleshooting Deployment

### Issue: Stage Not Found

**Solution:**
```sql
-- Verify stage exists
SHOW STAGES IN SCHEMA RDF_DB.PUBLIC;

-- Recreate if needed
CREATE OR REPLACE STAGE RDF_APP_STAGE;
```

### Issue: Permission Denied

**Solution:**
```sql
-- Check current role
SELECT CURRENT_ROLE();

-- Switch to appropriate role
USE ROLE ACCOUNTADMIN; -- or appropriate role

-- Grant necessary permissions
GRANT CREATE STREAMLIT ON SCHEMA RDF_DB.PUBLIC TO ROLE YOUR_ROLE;
```

### Issue: Files Not Uploading

**Solution:**
- Check file paths are correct
- Ensure files are not compressed
- Verify you have write permissions on the stage
- Try uploading files one at a time

### Issue: Streamlit App Won't Start

**Solutions:**
1. Check `requirements.txt` for incompatible packages
2. Verify `MAIN_FILE` path is correct
3. Check warehouse is running
4. Review application logs in Snowflake UI

### Issue: Application Runs Slowly

**Solutions:**
- Increase warehouse size
- Optimize queries with appropriate filters
- Reduce visualization node limits
- Consider clustering tables:
  ```sql
  ALTER TABLE RDF_TRIPLES CLUSTER BY (SUBJECT, PREDICATE);
  ```

## Cost Optimization

### 1. Warehouse Management
```sql
-- Auto-suspend after 5 minutes of inactivity
ALTER WAREHOUSE RDF_WAREHOUSE SET AUTO_SUSPEND = 300;

-- Use smaller warehouse for development
ALTER WAREHOUSE RDF_WAREHOUSE SET WAREHOUSE_SIZE = 'X-SMALL';
```

### 2. Resource Monitors

Create a resource monitor to control costs:

```sql
CREATE RESOURCE MONITOR RDF_APP_MONITOR
  WITH CREDIT_QUOTA = 100
  FREQUENCY = MONTHLY
  START_TIMESTAMP = IMMEDIATELY
  TRIGGERS
    ON 80 PERCENT DO NOTIFY
    ON 100 PERCENT DO SUSPEND;

ALTER WAREHOUSE RDF_WAREHOUSE SET RESOURCE_MONITOR = RDF_APP_MONITOR;
```

### 3. Data Retention

Set retention policy on tables:

```sql
ALTER TABLE RDF_TRIPLES SET DATA_RETENTION_TIME_IN_DAYS = 7;
```

## Security Best Practices

### 1. Use Dedicated Role

```sql
-- Create dedicated role for RDF app
CREATE ROLE IF NOT EXISTS RDF_APP_ROLE;

-- Grant minimal necessary permissions
GRANT USAGE ON DATABASE RDF_DB TO ROLE RDF_APP_ROLE;
GRANT USAGE ON SCHEMA RDF_DB.PUBLIC TO ROLE RDF_APP_ROLE;
GRANT USAGE ON WAREHOUSE RDF_WAREHOUSE TO ROLE RDF_APP_ROLE;
GRANT USAGE ON STREAMLIT RDF_OWL_VISUALIZER TO ROLE RDF_APP_ROLE;

-- Grant to users
GRANT ROLE RDF_APP_ROLE TO USER <username>;
```

### 2. Network Policies (if applicable)

```sql
-- Create network policy to restrict access
CREATE NETWORK POLICY RDF_APP_POLICY
  ALLOWED_IP_LIST = ('192.168.1.0/24', '10.0.0.0/8');

ALTER USER <username> SET NETWORK_POLICY = RDF_APP_POLICY;
```

### 3. Audit Logging

Enable query logging for compliance:

```sql
-- View access logs
SELECT * FROM SNOWFLAKE.ACCOUNT_USAGE.ACCESS_HISTORY
WHERE OBJECT_NAME = 'RDF_TRIPLES'
ORDER BY QUERY_START_TIME DESC;
```

## Backup and Recovery

### Export Configuration

```sql
-- Export table structures
SELECT GET_DDL('TABLE', 'RDF_DB.PUBLIC.RDF_TRIPLES');

-- Export view definitions
SELECT GET_DDL('VIEW', 'RDF_DB.PUBLIC.RDF_CLASS_HIERARCHY');
```

### Backup Data

```sql
-- Create backup table
CREATE TABLE RDF_TRIPLES_BACKUP CLONE RDF_TRIPLES;

-- Or export to stage
COPY INTO @RDF_APP_STAGE/backup/
FROM RDF_TRIPLES
FILE_FORMAT = (TYPE = 'CSV' COMPRESSION = 'GZIP');
```

## Support and Resources

- [Snowflake Streamlit Documentation](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Snowflake Support Portal](https://support.snowflake.com/)
- Application README.md for feature documentation
- QUICKSTART.md for usage examples

---

**Deployment Complete!** 🎉 Your RDF/OWL Visualizer is now ready to use in Snowflake.

