#!/usr/bin/env python3
"""
Simple script to run msfconsole command without starting GUI.
"""
import subprocess
def run_msf_command(command):
    """Run single msfconsole command."""
    
    # Build the complete command string
    cmd = f"msfconsole -q -x '{command}'"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(result.stdout.strip())
        else:
            print(f"Error ({result.returncode}): {result.stderr}")
            
    except Exception as e:
        print(f"Execution error: {e}")
def main():
    # Example commands
    run_msf_command("db_status")          # Check database status
    run_msf_command("search ssh")         # Search for SSH modules
    
if __name__ == "__main__":
    main()
