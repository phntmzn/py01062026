#!/usr/bin/env python3
"""
Script that maintains connection to msfconsole.
"""
import subprocess
import time
def setup_msf_session():
    """Start msfconsole with specific options."""
    
    try:
        # Start msfconsole in quiet mode (-q) and without GUI (-Q)
        process = subprocess.Popen(
            ["msfconsole", "-q", "-Q"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,  # line-buffered output
            universal_newlines=True,
        )
        
        return process
    
    except Exception as e:
        print(f"Failed to start msfconsole: {e}")
        return None
def send_command(process, command):
    """Send a single command."""
    
    if not process:
        return "Session not established"
    
    try:
        # Each command ends with ';'
        process.stdin.write(command + ';\n')
        
        # Wait for output to appear
        time.sleep(0.5)
        
        # Read available output (non-blocking)
        output = ""
        while True:
            char = process.stdout.read(1)
            if not char or char == "\n":
                break
            output += char
            
        return output.strip()
    
    except Exception as e:
        print(f"Command execution error: {e}")
        return f"Error executing command '{command}'"
def main():
    session = setup_msf_session()
    
    if not session:
        exit(1)
        
    # Interact
    try:
        while True:
            cmd = input("msf> ")
            
            if cmd.lower() in ['exit', 'quit']:
                break
                
            result = send_command(session, cmd)
            print(result)
                
    except KeyboardInterrupt:
        print("\nExiting...")
    
    finally:
        session.terminate()
        session.wait()
if __name__ == "__main__":
    main()
