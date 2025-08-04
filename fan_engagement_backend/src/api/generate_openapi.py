import json
import os
import sys

# Add the parent directory to Python path to import the main app
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.api.main import app

def generate_openapi():
    """Generate OpenAPI JSON specification from the FastAPI application"""
    try:
        # Get the OpenAPI schema
        openapi_schema = app.openapi()
        
        # Ensure the interfaces directory exists
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "interfaces")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "openapi.json")
        
        # Write the schema to file
        with open(output_path, "w") as f:
            json.dump(openapi_schema, f, indent=2)
        
        print(f"OpenAPI schema generated successfully at: {output_path}")
        
        # Print some basic stats
        paths_count = len(openapi_schema.get("paths", {}))
        components_count = len(openapi_schema.get("components", {}).get("schemas", {}))
        print(f"Generated schema contains {paths_count} endpoints and {components_count} components")
        
    except Exception as e:
        print(f"Error generating OpenAPI schema: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_openapi()
