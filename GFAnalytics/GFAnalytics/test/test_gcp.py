#!/usr/bin/env python3
"""
Test script to diagnose GCP import issues
"""

import sys
import time

def test_import(module_name, description=""):
    """Test importing a module and measure time taken."""
    print(f"\n{'='*50}")
    print(f"Testing: {module_name}")
    if description:
        print(f"Description: {description}")
    print(f"{'='*50}")
    
    start_time = time.time()
    try:
        print(f"Importing {module_name}...")
        if module_name == "google.cloud.bigquery":
            from google.cloud import bigquery
            print("✅ google.cloud.bigquery imported successfully")
            
        elif module_name == "google.cloud.storage":
            from google.cloud import storage
            print("✅ google.cloud.storage imported successfully")
            
        elif module_name == "google.auth":
            import google.auth
            print("✅ google.auth imported successfully")
            
        elif module_name == "google.resumable_media":
            import google.resumable_media
            print("✅ google.resumable_media imported successfully")
            
        elif module_name == "google.api_core":
            import google.api_core
            print("✅ google.api_core imported successfully")
            
        elif module_name == "googleapiclient":
            from googleapiclient.discovery import build
            print("✅ googleapiclient imported successfully")
            
        elif module_name == "oauth2client":
            from oauth2client.service_account import ServiceAccountCredentials
            print("✅ oauth2client imported successfully")
            
        else:
            exec(f"import {module_name}")
            print(f"✅ {module_name} imported successfully")
            
        end_time = time.time()
        print(f"⏱️  Import took: {end_time - start_time:.2f} seconds")
        return True
        
    except ImportError as e:
        end_time = time.time()
        print(f"❌ ImportError: {e}")
        print(f"⏱️  Failed after: {end_time - start_time:.2f} seconds")
        return False
        
    except Exception as e:
        end_time = time.time()
        print(f"❌ Error: {e}")
        print(f"⏱️  Failed after: {end_time - start_time:.2f} seconds")
        return False

def test_gcp_credentials():
    """Test GCP credentials setup based on config.yaml."""
    print(f"\n{'='*50}")
    print("Testing GCP Credentials from Config")
    print(f"{'='*50}")
    
    try:
        import os
        import yaml
        from google.auth import default
        
        # Debug: Show current working directory and file locations
        current_dir = os.getcwd()
        test_file_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"🔍 Current working directory: {current_dir}")
        print(f"🔍 Test file directory: {test_file_dir}")
        
        # Try multiple possible config paths
        possible_config_paths = [
            os.path.join(current_dir, 'config', 'config.yaml'),  # From current working dir
            os.path.join(test_file_dir, '..', 'config', 'config.yaml'),  # Relative to test file
            os.path.join(os.path.dirname(test_file_dir), 'config', 'config.yaml'),  # Parent of test dir
            'config/config.yaml',  # Simple relative path
        ]
        
        print(f"🔍 Looking for config.yaml in these locations:")
        config_path = None
        for path in possible_config_paths:
            abs_path = os.path.abspath(path)
            exists = os.path.exists(path)
            print(f"  {'✅' if exists else '❌'} {abs_path}")
            if exists and config_path is None:
                config_path = path
        
        if not config_path:
            print("❌ Config file not found in any expected location")
            return False
            
        print(f"📋 Using config file: {os.path.abspath(config_path)}")
        
        # Load config.yaml
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)
        
        # Get credential path from config
        gcp_config = config.get('gcp', {})
        credentials_path = gcp_config.get('credentials_path', '')
        project_id = gcp_config.get('project_id', '')
        
        print(f"📋 From config.yaml:")
        print(f"  Project ID: {project_id}")
        print(f"  Credentials Path: {credentials_path}")
        
        if not credentials_path:
            print("❌ No credentials_path specified in config.yaml")
            return False
        
        # Check if credential file exists (try multiple locations)
        possible_cred_paths = [
            credentials_path,  # As specified in config
            os.path.join(current_dir, credentials_path),  # From current working dir
            os.path.join(os.path.dirname(config_path), '..', credentials_path),  # Relative to config
            os.path.join(test_file_dir, '..', credentials_path),  # Relative to test
        ]
        
        print(f"🔍 Looking for credential file in these locations:")
        found_path = None
        for path in possible_cred_paths:
            abs_path = os.path.abspath(path)
            exists = os.path.exists(path)
            print(f"  {'✅' if exists else '❌'} {abs_path}")
            if exists and found_path is None:
                found_path = path
        
        if not found_path:
            print(f"❌ Credential file '{credentials_path}' not found in any expected location")
            return False
        
        print(f"🔧 Using credential file: {os.path.abspath(found_path)}")
        
        # Set environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(found_path)
        print(f"🔧 Set GOOGLE_APPLICATION_CREDENTIALS to: {os.path.abspath(found_path)}")
        
        # Test authentication
        credentials, detected_project = default()
        print(f"✅ Authentication successful for project: {detected_project}")
        
        # Verify project matches config
        if project_id and detected_project != project_id:
            print(f"⚠️  Warning: Config project ({project_id}) != credential project ({detected_project})")
        else:
            print(f"✅ Project matches config: {detected_project}")
        
        return True
        
    except Exception as e:
        print(f"❌ Credentials error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_bigquery_connection():
    """Test BigQuery connection."""
    print(f"\n{'='*50}")
    print("Testing BigQuery Connection")
    print(f"{'='*50}")
    
    try:
        from google.cloud import bigquery
        
        # Try to create a client
        print("Creating BigQuery client...")
        client = bigquery.Client()
        print(f"✅ BigQuery client created for project: {client.project}")
        
        # Try to list datasets (this will test actual connectivity)
        print("Testing connectivity by listing datasets...")
        datasets = list(client.list_datasets(max_results=5))
        print(f"✅ Connection successful. Found {len(datasets)} dataset(s)")
        
        if datasets:
            print("Available datasets:")
            for dataset in datasets:
                print(f"  - {dataset.dataset_id}")
        else:
            print("No datasets found (this might be normal for a new project)")
        
        return True
        
    except Exception as e:
        print(f"❌ BigQuery connection error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all GCP tests."""
    print("🔍 GCP Import and Connection Test")
    print("=" * 60)
    
    # Test basic imports first
    basic_modules = [
        ("google", "Base Google package"),
        ("google.auth", "Google authentication"),
        ("google.api_core", "Google API core"),
        ("google.resumable_media", "Resumable media uploads"),
        ("google.cloud", "Google Cloud base package"),
    ]
    
    print("\n🧪 PHASE 1: Testing basic Google packages")
    for module, desc in basic_modules:
        test_import(module, desc)
        time.sleep(0.5)  # Small delay to see progress
    
    # Test specific GCP services
    gcp_services = [
        ("google.cloud.bigquery", "BigQuery client library"),
        ("google.cloud.storage", "Cloud Storage client library"),
        ("googleapiclient", "Google API client library"),
        ("oauth2client", "OAuth2 client library"),
    ]
    
    print("\n🧪 PHASE 2: Testing GCP service libraries")
    for module, desc in gcp_services:
        test_import(module, desc)
        time.sleep(0.5)
    
    # Test credentials
    print("\n🧪 PHASE 3: Testing credentials")
    test_gcp_credentials()
    
    # Test actual connections
    print("\n🧪 PHASE 4: Testing connections")
    test_bigquery_connection()
    
    print(f"\n{'='*60}")
    print("🏁 Test completed!")
    print("If any imports are hanging, press Ctrl+C to stop")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n⚠️  Test interrupted by user")
        print("The hanging import was likely the cause of your main.py issue")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)