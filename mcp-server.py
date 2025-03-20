import json
import sys
import os
from dotenv import load_dotenv
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Confluence API configuration
CONFLUENCE_URL = os.getenv("CONFLUENCE_URL")
CONFLUENCE_USERNAME = os.getenv("CONFLUENCE_USERNAME")
CONFLUENCE_API_TOKEN = os.getenv("CONFLUENCE_API_TOKEN")
PAGE_ID = os.getenv("PAGE_ID")

def generate_auth_header():
    """Generate the authentication header for Confluence API."""
    return f"Basic {CONFLUENCE_USERNAME}:{CONFLUENCE_API_TOKEN}"

def expand_content(header, content):
    """Expand the content and update Confluence page."""
    try:
        # Generate authentication header
        auth_header = generate_auth_header()
        logger.debug("Generated authentication header")

        # Create new content
        new_content = f"""
h1. {header}

{content}

h2. Key Concepts

* Food Chain Definition
* Producers and Consumers
* Energy Flow
* Trophic Levels

h2. Examples

h3. Terrestrial Food Chain
* Grass → Grasshopper → Frog → Snake → Hawk

h3. Marine Food Chain
* Phytoplankton → Zooplankton → Small Fish → Large Fish → Shark

h2. Impact on Ecosystems

* Balance in Nature
* Environmental Factors
* Human Impact
"""
        logger.debug("Created new content")

        # Update Confluence page
        update_url = f"{CONFLUENCE_URL}/rest/api/content/{PAGE_ID}"
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json"
        }
        
        # Get current version
        response = requests.get(update_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to get current version: {response.text}")
            return False
            
        current_version = response.json()["version"]["number"]
        logger.debug(f"Current version: {current_version}")

        # Update content
        update_data = {
            "version": {"number": current_version + 1},
            "title": header,
            "type": "page",
            "body": {
                "storage": {
                    "value": new_content,
                    "representation": "wiki"
                }
            }
        }

        response = requests.put(update_url, headers=headers, json=update_data)
        if response.status_code != 200:
            logger.error(f"Failed to update page: {response.text}")
            return False

        logger.info("Successfully updated Confluence page")
        return True

    except Exception as e:
        logger.error(f"Error expanding content: {str(e)}")
        return False

def handle_request(request):
    """Handle incoming JSON-RPC requests."""
    try:
        method = request.get("method")
        params = request.get("params", {})

        if method == "expand_content_tool":
            header = params.get("header")
            content = params.get("content")
            
            if not header or not content:
                return {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32602,
                        "message": "Invalid parameters"
                    }
                }

            success = expand_content(header, content)
            
            return {
                "jsonrpc": "2.0",
                "result": {
                    "success": success,
                    "message": "Content expanded and updated successfully" if success else "Failed to expand content"
                }
            }

        else:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": "Method not found"
                }
            }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32000,
                "message": str(e)
            }
        }

def main():
    """Main server loop."""
    logger.info("Starting MCP server...")
    
    # Verify environment variables
    required_vars = ["CONFLUENCE_URL", "CONFLUENCE_USERNAME", "CONFLUENCE_API_TOKEN", "PAGE_ID"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return

    logger.info("Environment check passed")

    while True:
        try:
            # Read request from stdin
            request_line = sys.stdin.readline()
            if not request_line:
                break

            request = json.loads(request_line)
            logger.debug(f"Received request: {request}")

            # Handle request
            response = handle_request(request)
            
            # Send response to stdout
            print(json.dumps(response))
            sys.stdout.flush()

        except json.JSONDecodeError:
            logger.error("Invalid JSON received")
            continue
        except Exception as e:
            logger.error(f"Error processing request: {str(e)}")
            continue

if __name__ == "__main__":
    main() 