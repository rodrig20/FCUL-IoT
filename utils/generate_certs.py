#!/usr/bin/env python3
import subprocess
import os
from pathlib import Path

def run(cmd):
    subprocess.run(cmd, shell=True, check=True)

# Generate all certificates in a single directory relative to the script
certs_dir = Path(__file__).parent / "certs"
certs_dir.mkdir(exist_ok=True)

# Generate CA
run(f"openssl genrsa -out {certs_dir}/ca.key 4096")
run(f"openssl req -new -x509 -days 3650 -key {certs_dir}/ca.key -out {certs_dir}/ca.crt -subj '/C=PT/ST=Lisbon/L=Lisbon/O=FCUL/OU=DI/CN=IoT-CA'")

# Generate server key and cert for mosquitto
run(f"openssl genrsa -out {certs_dir}/server.key 2048")
run(f"openssl req -new -key {certs_dir}/server.key -out {certs_dir}/server.csr -subj '/C=PT/ST=Lisbon/L=Lisbon/O=FCUL/OU=DI/CN=mosquitto'")
run(f"openssl x509 -req -days 3650 -in {certs_dir}/server.csr -CA {certs_dir}/ca.crt -CAkey {certs_dir}/ca.key -out {certs_dir}/server.crt -CAcreateserial")
os.remove(f"{certs_dir}/server.csr")

# Generate client certificates (for utils publisher)
run(f"openssl genrsa -out {certs_dir}/client.key 2048")
run(f"openssl req -new -key {certs_dir}/client.key -out {certs_dir}/client.csr -subj '/C=PT/ST=Lisbon/L=Lisbon/O=FCUL/OU=DI/CN=Client'")
run(f"openssl x509 -req -days 3650 -in {certs_dir}/client.csr -CA {certs_dir}/ca.crt -CAkey {certs_dir}/ca.key -out {certs_dir}/client.crt -CAcreateserial")
os.remove(f"{certs_dir}/client.csr")

# Cleanup
os.remove(f"{certs_dir}/ca.key")  # Keep CA private key secure
os.remove(f"{certs_dir}/ca.srl")