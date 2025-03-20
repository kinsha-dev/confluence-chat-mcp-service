import json
import sys

def send_request():
    request = {
        "jsonrpc": "2.0",
        "method": "expand_content_tool",
        "params": {
            "header": "Understanding Animal Food Chains",
            "content": "Create a comprehensive guide about animal food chains."
        }
    }
    print(json.dumps(request))
    sys.stdout.flush()

if __name__ == "__main__":
    send_request() 