-- ========================================
-- Snowflake Setup Script for RDF/OWL Visualizer
-- ========================================

-- 1. Create database and schema for the application
CREATE DATABASE IF NOT EXISTS RDF_DB;
USE DATABASE RDF_DB;
CREATE SCHEMA IF NOT EXISTS PUBLIC;
USE SCHEMA PUBLIC;

-- 2. Create a warehouse for the application (if needed)
-- Adjust size based on your needs
CREATE WAREHOUSE IF NOT EXISTS RDF_WAREHOUSE
    WAREHOUSE_SIZE = 'SMALL'
    AUTO_SUSPEND = 300
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
    COMMENT = 'Warehouse for RDF/OWL Visualizer application';

-- 3. Create a stage for uploading application files
CREATE STAGE IF NOT EXISTS RDF_APP_STAGE
    COMMENT = 'Stage for RDF/OWL Visualizer Streamlit application files';

-- 4. List files in the stage (after upload)
-- LIST @RDF_APP_STAGE;

-- 5. Create the Streamlit application
-- Note: Run this AFTER uploading all files to the stage
CREATE STREAMLIT IF NOT EXISTS RDF_OWL_VISUALIZER
    ROOT_LOCATION = '@RDF_DB.PUBLIC.RDF_APP_STAGE'
    MAIN_FILE = 'streamlit_app.py'
    QUERY_WAREHOUSE = 'RDF_WAREHOUSE'
    COMMENT = 'RDF/OWL Visualizer and Editor application';

-- 6. Grant permissions (adjust roles as needed)
-- GRANT USAGE ON DATABASE RDF_DB TO ROLE YOUR_ROLE;
-- GRANT USAGE ON SCHEMA RDF_DB.PUBLIC TO ROLE YOUR_ROLE;
-- GRANT USAGE ON WAREHOUSE RDF_WAREHOUSE TO ROLE YOUR_ROLE;
-- GRANT USAGE ON STREAMLIT RDF_OWL_VISUALIZER TO ROLE YOUR_ROLE;

-- ========================================
-- Sample Table Structures
-- ========================================

-- Sample RDF Triples Table
CREATE TABLE IF NOT EXISTS RDF_TRIPLES (
    SUBJECT VARCHAR(16777216),
    PREDICATE VARCHAR(16777216),
    OBJECT VARCHAR(16777216),
    OBJECT_TYPE VARCHAR(20),
    DATATYPE VARCHAR(1000),
    LANGUAGE VARCHAR(10),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Sample Namespace Table
CREATE TABLE IF NOT EXISTS RDF_NAMESPACES (
    PREFIX VARCHAR(100),
    NAMESPACE_URI VARCHAR(16777216),
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

-- Sample Metadata Table for tracking loaded ontologies
CREATE TABLE IF NOT EXISTS RDF_ONTOLOGY_METADATA (
    ONTOLOGY_ID VARCHAR(100),
    ONTOLOGY_NAME VARCHAR(500),
    FORMAT VARCHAR(50),
    TRIPLE_COUNT INTEGER,
    LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
    SOURCE_URL VARCHAR(16777216)
);

-- ========================================
-- Indexes for Performance (optional)
-- ========================================

-- Note: Snowflake handles indexing automatically, but you can cluster tables
-- ALTER TABLE RDF_TRIPLES CLUSTER BY (SUBJECT, PREDICATE);

-- ========================================
-- Sample Views
-- ========================================

-- View to get class hierarchy
CREATE OR REPLACE VIEW RDF_CLASS_HIERARCHY AS
SELECT 
    s.SUBJECT AS CLASS,
    s.OBJECT AS LABEL,
    h.OBJECT AS PARENT_CLASS
FROM RDF_TRIPLES s
LEFT JOIN RDF_TRIPLES h 
    ON s.SUBJECT = h.SUBJECT 
    AND h.PREDICATE = 'http://www.w3.org/2000/01/rdf-schema#subClassOf'
WHERE s.PREDICATE = 'http://www.w3.org/2000/01/rdf-schema#label'
    AND EXISTS (
        SELECT 1 FROM RDF_TRIPLES t
        WHERE t.SUBJECT = s.SUBJECT
        AND t.PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
        AND t.OBJECT IN (
            'http://www.w3.org/2002/07/owl#Class',
            'http://www.w3.org/2000/01/rdf-schema#Class'
        )
    );

-- View to get all properties with their characteristics
CREATE OR REPLACE VIEW RDF_PROPERTIES AS
SELECT 
    t.SUBJECT AS PROPERTY_URI,
    MAX(CASE WHEN t.PREDICATE = 'http://www.w3.org/2000/01/rdf-schema#label' 
        THEN t.OBJECT END) AS LABEL,
    MAX(CASE WHEN t.PREDICATE = 'http://www.w3.org/2000/01/rdf-schema#domain' 
        THEN t.OBJECT END) AS DOMAIN,
    MAX(CASE WHEN t.PREDICATE = 'http://www.w3.org/2000/01/rdf-schema#range' 
        THEN t.OBJECT END) AS RANGE,
    MAX(CASE WHEN t.PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type' 
        THEN t.OBJECT END) AS PROPERTY_TYPE
FROM RDF_TRIPLES t
WHERE EXISTS (
    SELECT 1 FROM RDF_TRIPLES t2
    WHERE t2.SUBJECT = t.SUBJECT
    AND t2.PREDICATE = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#type'
    AND t2.OBJECT IN (
        'http://www.w3.org/2002/07/owl#ObjectProperty',
        'http://www.w3.org/2002/07/owl#DatatypeProperty',
        'http://www.w3.org/2002/07/owl#AnnotationProperty',
        'http://www.w3.org/1999/02/22-rdf-syntax-ns#Property'
    )
)
GROUP BY t.SUBJECT;

-- ========================================
-- Utility Procedures (optional)
-- ========================================

-- Procedure to clean up old ontology data
CREATE OR REPLACE PROCEDURE CLEANUP_OLD_ONTOLOGIES(DAYS_OLD INTEGER)
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    DELETE FROM RDF_TRIPLES 
    WHERE CREATED_AT < DATEADD(DAY, -:DAYS_OLD, CURRENT_TIMESTAMP());
    
    DELETE FROM RDF_NAMESPACES 
    WHERE CREATED_AT < DATEADD(DAY, -:DAYS_OLD, CURRENT_TIMESTAMP());
    
    DELETE FROM RDF_ONTOLOGY_METADATA 
    WHERE LOADED_AT < DATEADD(DAY, -:DAYS_OLD, CURRENT_TIMESTAMP());
    
    RETURN 'Cleanup completed for data older than ' || :DAYS_OLD || ' days';
END;
$$;

-- ========================================
-- Upload Instructions
-- ========================================

/*
To upload files to the stage, use SnowSQL or Snowflake CLI:

snowsql -a <account> -u <username>

Then run:

PUT file:///path/to/streamlit_app.py @RDF_DB.PUBLIC.RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file:///path/to/rdf_reader.py @RDF_DB.PUBLIC.RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file:///path/to/graph_visualizer.py @RDF_DB.PUBLIC.RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file:///path/to/rdf_converter.py @RDF_DB.PUBLIC.RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file:///path/to/snowflake_writer.py @RDF_DB.PUBLIC.RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;
PUT file:///path/to/requirements.txt @RDF_DB.PUBLIC.RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE;

Or use the Snowflake UI:
1. Navigate to Data > Databases > RDF_DB > PUBLIC > Stages
2. Click on RDF_APP_STAGE
3. Click "Upload Files"
4. Select all application files
*/

-- Verify files are uploaded
LIST @RDF_APP_STAGE;

-- ========================================
-- Test Queries (after loading data)
-- ========================================

-- Count triples by type
SELECT OBJECT_TYPE, COUNT(*) as COUNT
FROM RDF_TRIPLES
GROUP BY OBJECT_TYPE;

-- Get top 10 most used predicates
SELECT PREDICATE, COUNT(*) as USAGE_COUNT
FROM RDF_TRIPLES
GROUP BY PREDICATE
ORDER BY USAGE_COUNT DESC
LIMIT 10;

-- Get all namespaces
SELECT * FROM RDF_NAMESPACES
ORDER BY PREFIX;

-- Show ontology metadata
SELECT * FROM RDF_ONTOLOGY_METADATA
ORDER BY LOADED_AT DESC;

