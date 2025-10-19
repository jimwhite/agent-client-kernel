#!/usr/bin/env python3
"""
Mock ACP agent for testing purposes.
This simulates an agent that responds to JSON-RPC requests.
"""

import sys
import json
import time


def main():
    """Main loop for the mock agent."""
    print("Mock agent started", file=sys.stderr)
    sys.stderr.flush()
    
    while True:
        try:
            # Read a line from stdin
            line = sys.stdin.readline()
            if not line:
                break
                
            line = line.strip()
            if not line:
                continue
                
            print(f"Received: {line}", file=sys.stderr)
            sys.stderr.flush()
            
            # Parse the JSON-RPC request
            try:
                request = json.loads(line)
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": "Parse error",
                        "data": str(e)
                    }
                }
                print(json.dumps(error_response), flush=True)
                continue
                
            # Process the request
            response = process_request(request)
            
            # Send the response
            print(json.dumps(response), flush=True)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.stderr.flush()


def process_request(request):
    """Process a JSON-RPC request and generate a response."""
    request_id = request.get("id")
    method = request.get("method")
    params = request.get("params", {})
    
    if method == "chat/send":
        # Echo back the message with a friendly response
        user_message = params.get("message", "")
        
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "text": f"Mock agent received: '{user_message}'\nThis is a test response from the mock agent."
            }
        }
        
    elif method == "initialize":
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "capabilities": {
                    "chat": True,
                    "filesystem": True
                },
                "serverInfo": {
                    "name": "mock-agent",
                    "version": "0.1.0"
                }
            }
        }
        
    else:
        # Unknown method
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32601,
                "message": f"Method not found: {method}"
            }
        }
        
    return response


if __name__ == "__main__":
    main()
