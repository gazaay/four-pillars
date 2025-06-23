def test_gcp_credentials():
    """Test GCP credentials setup based on config.yaml."""
    print(f"\n{'='*50}")
    print("Testing GCP Credentials from Config")
    print(f"{'='*50}")
    
    try:
        import os
        import yaml
        from google.auth import default
        
        # Load config.yaml to get the credential path
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'config.yaml')
        
        if not os.path.exists(config_path):
            print(f"❌ Config file not found: {config_path}")
            return False
            
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
        
        # Check if credential file exists (try relative to project root)
        possible_paths = [
            credentials_path,  # As specified in config
            os.path.join(os.path.dirname(config_path), '..', credentials_path),  # Relative to project root
            os.path.join(os.path.dirname(__file__), '..', credentials_path),  # Relative to test directory
        ]
        
        found_path = None
        for path in possible_paths:
            if os.path.exists(path):
                found_path = path
                print(f"✅ Found credential file: {path}")
                break
            else:
                print(f"❌ Not found: {path}")
        
        if not found_path:
            print(f"❌ Credential file '{credentials_path}' not found in any expected location")
            return False
        
        # Set environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = found_path
        print(f"🔧 Set GOOGLE_APPLICATION_CREDENTIALS to: {found_path}")
        
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
        return False 