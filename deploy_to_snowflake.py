#!/usr/bin/env python3
"""
Automated Deployment Script for RDF/OWL Visualizer to Snowflake
This script automates the deployment process to Snowflake
"""

import snowflake.connector
import os
import sys
from pathlib import Path


class SnowflakeDeployer:
    """Automates deployment of Streamlit app to Snowflake"""
    
    def __init__(self, account, user, password, database='RDF_DB', 
                 schema='PUBLIC', warehouse='RDF_WAREHOUSE'):
        """
        Initialize deployer with connection parameters
        
        Args:
            account: Snowflake account identifier
            user: Username
            password: Password
            database: Target database (default: RDF_DB)
            schema: Target schema (default: PUBLIC)
            warehouse: Warehouse to use (default: RDF_WAREHOUSE)
        """
        self.account = account
        self.user = user
        self.password = password
        self.database = database
        self.schema = schema
        self.warehouse = warehouse
        self.connection = None
        self.cursor = None
        
        # Files to deploy
        self.app_files = [
            'streamlit_app.py',
            'rdf_reader.py',
            'graph_visualizer.py',
            'rdf_converter.py',
            'snowflake_writer.py',
            'requirements.txt'
        ]
        
    def connect(self):
        """Establish connection to Snowflake"""
        try:
            print(f"Connecting to Snowflake account: {self.account}")
            self.connection = snowflake.connector.connect(
                account=self.account,
                user=self.user,
                password=self.password,
                warehouse=self.warehouse
            )
            self.cursor = self.connection.cursor()
            print("✅ Connected successfully")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {str(e)}")
            return False
    
    def execute_sql(self, sql, description=""):
        """Execute SQL command"""
        try:
            if description:
                print(f"  {description}...")
            self.cursor.execute(sql)
            return True
        except Exception as e:
            print(f"  ❌ Failed: {str(e)}")
            return False
    
    def setup_environment(self):
        """Create database, schema, warehouse, and stage"""
        print("\n📦 Setting up Snowflake environment...")
        
        # Create database
        if not self.execute_sql(
            f"CREATE DATABASE IF NOT EXISTS {self.database}",
            "Creating database"
        ):
            return False
        
        # Use database
        self.execute_sql(f"USE DATABASE {self.database}")
        
        # Create schema
        if not self.execute_sql(
            f"CREATE SCHEMA IF NOT EXISTS {self.schema}",
            "Creating schema"
        ):
            return False
        
        # Use schema
        self.execute_sql(f"USE SCHEMA {self.schema}")
        
        # Create warehouse
        if not self.execute_sql(
            f"""CREATE WAREHOUSE IF NOT EXISTS {self.warehouse}
                WAREHOUSE_SIZE = 'SMALL'
                AUTO_SUSPEND = 300
                AUTO_RESUME = TRUE
                INITIALLY_SUSPENDED = TRUE""",
            "Creating warehouse"
        ):
            return False
        
        # Create stage
        if not self.execute_sql(
            "CREATE STAGE IF NOT EXISTS RDF_APP_STAGE",
            "Creating stage"
        ):
            return False
        
        print("✅ Environment setup complete")
        return True
    
    def upload_files(self):
        """Upload application files to Snowflake stage"""
        print("\n📤 Uploading application files...")
        
        # Check if files exist
        missing_files = []
        for file in self.app_files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print(f"❌ Missing files: {', '.join(missing_files)}")
            return False
        
        # Upload each file
        for file in self.app_files:
            try:
                abs_path = os.path.abspath(file)
                sql = f"PUT file://{abs_path} @RDF_APP_STAGE AUTO_COMPRESS=FALSE OVERWRITE=TRUE"
                print(f"  Uploading {file}...")
                self.cursor.execute(sql)
                print(f"  ✅ {file} uploaded")
            except Exception as e:
                print(f"  ❌ Failed to upload {file}: {str(e)}")
                return False
        
        print("✅ All files uploaded successfully")
        return True
    
    def verify_files(self):
        """Verify files are in the stage"""
        print("\n🔍 Verifying uploaded files...")
        
        try:
            self.cursor.execute("LIST @RDF_APP_STAGE")
            files = self.cursor.fetchall()
            
            if len(files) >= len(self.app_files):
                print(f"✅ Found {len(files)} files in stage")
                for file_info in files:
                    print(f"  - {file_info[0]}")
                return True
            else:
                print(f"⚠️  Expected {len(self.app_files)} files, found {len(files)}")
                return False
        except Exception as e:
            print(f"❌ Verification failed: {str(e)}")
            return False
    
    def create_streamlit_app(self, app_name='RDF_OWL_VISUALIZER'):
        """Create the Streamlit application"""
        print(f"\n🚀 Creating Streamlit application: {app_name}...")
        
        sql = f"""
        CREATE OR REPLACE STREAMLIT {app_name}
            ROOT_LOCATION = '@{self.database}.{self.schema}.RDF_APP_STAGE'
            MAIN_FILE = 'streamlit_app.py'
            QUERY_WAREHOUSE = '{self.warehouse}'
        """
        
        try:
            self.cursor.execute(sql)
            print(f"✅ Streamlit application '{app_name}' created successfully")
            print(f"\n🎉 Deployment complete!")
            print(f"\n📱 Access your app:")
            print(f"   1. Log into Snowflake UI")
            print(f"   2. Navigate to Apps → Streamlit")
            print(f"   3. Click on '{app_name}'")
            return True
        except Exception as e:
            print(f"❌ Failed to create Streamlit app: {str(e)}")
            return False
    
    def create_sample_tables(self):
        """Create sample table structures"""
        print("\n📊 Creating sample table structures...")
        
        tables = [
            (
                "RDF_TRIPLES",
                """CREATE TABLE IF NOT EXISTS RDF_TRIPLES (
                    SUBJECT VARCHAR(16777216),
                    PREDICATE VARCHAR(16777216),
                    OBJECT VARCHAR(16777216),
                    OBJECT_TYPE VARCHAR(20),
                    DATATYPE VARCHAR(1000),
                    LANGUAGE VARCHAR(10),
                    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )"""
            ),
            (
                "RDF_NAMESPACES",
                """CREATE TABLE IF NOT EXISTS RDF_NAMESPACES (
                    PREFIX VARCHAR(100),
                    NAMESPACE_URI VARCHAR(16777216),
                    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
                )"""
            ),
            (
                "RDF_ONTOLOGY_METADATA",
                """CREATE TABLE IF NOT EXISTS RDF_ONTOLOGY_METADATA (
                    ONTOLOGY_ID VARCHAR(100),
                    ONTOLOGY_NAME VARCHAR(500),
                    FORMAT VARCHAR(50),
                    TRIPLE_COUNT INTEGER,
                    LOADED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP(),
                    SOURCE_URL VARCHAR(16777216)
                )"""
            )
        ]
        
        for table_name, sql in tables:
            if self.execute_sql(sql, f"Creating {table_name}"):
                print(f"  ✅ {table_name} created")
            else:
                return False
        
        print("✅ Sample tables created")
        return True
    
    def deploy(self):
        """Run full deployment process"""
        print("=" * 60)
        print("RDF/OWL Visualizer - Snowflake Deployment")
        print("=" * 60)
        
        # Connect
        if not self.connect():
            return False
        
        # Setup environment
        if not self.setup_environment():
            return False
        
        # Upload files
        if not self.upload_files():
            return False
        
        # Verify files
        if not self.verify_files():
            return False
        
        # Create sample tables
        if not self.create_sample_tables():
            return False
        
        # Create Streamlit app
        if not self.create_streamlit_app():
            return False
        
        return True
    
    def cleanup(self):
        """Clean up connections"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("\n👋 Connection closed")


def main():
    """Main function"""
    print("RDF/OWL Visualizer - Snowflake Deployment Script")
    print("=" * 60)
    
    # Get connection parameters
    if len(sys.argv) < 4:
        print("\nUsage: python deploy_to_snowflake.py <account> <user> <password> [database] [schema] [warehouse]")
        print("\nExample:")
        print("  python deploy_to_snowflake.py myaccount myuser mypassword")
        print("\nOr set environment variables:")
        print("  SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_PASSWORD")
        
        # Try environment variables
        account = os.getenv('SNOWFLAKE_ACCOUNT')
        user = os.getenv('SNOWFLAKE_USER')
        password = os.getenv('SNOWFLAKE_PASSWORD')
        
        if not (account and user and password):
            print("\n❌ Missing required parameters")
            sys.exit(1)
        
        print("\n✅ Using environment variables")
    else:
        account = sys.argv[1]
        user = sys.argv[2]
        password = sys.argv[3]
    
    # Optional parameters
    database = sys.argv[4] if len(sys.argv) > 4 else 'RDF_DB'
    schema = sys.argv[5] if len(sys.argv) > 5 else 'PUBLIC'
    warehouse = sys.argv[6] if len(sys.argv) > 6 else 'RDF_WAREHOUSE'
    
    # Create deployer
    deployer = SnowflakeDeployer(
        account=account,
        user=user,
        password=password,
        database=database,
        schema=schema,
        warehouse=warehouse
    )
    
    try:
        # Run deployment
        success = deployer.deploy()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ DEPLOYMENT SUCCESSFUL")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ DEPLOYMENT FAILED")
            print("=" * 60)
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        deployer.cleanup()


if __name__ == "__main__":
    main()

