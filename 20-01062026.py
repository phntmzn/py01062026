#!/usr/bin/env python3
#
# Equivalent to:
#   nc -l -p 1337 -vv
#
# Listens on TCP port 1337 with verbose output.
#

import socket

HOST = "0.0.0.0"
PORT = 1337

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(1)

        print(f"[VERBOSE] Listening on {HOST}:{PORT}")

        conn, addr = s.accept()
        with conn:
            print(f"[VERBOSE] Connection received from {addr[0]}:{addr[1]}")

            while True:
                data = conn.recv(4096)
                if not data:
                    print("[VERBOSE] Connection closed by peer")
                    break

                print(f"[VERBOSE] Received {len(data)} bytes:")
                print(data.decode(errors="ignore"))

                # Optional echo to mirror interactive behavior
                conn.sendall(b"ACK\n")

if __name__ == "__main__":
    main()
