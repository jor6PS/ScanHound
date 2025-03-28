#!/usr/bin/env python3
# getvulns.py

import requests
import os

def get_vulns(host, port, vulns):
    try:
        vulns_file = f"{folder_vuln_path}/{host}_{port}.txt"
        with open(vulns_file, 'w') as f:
            f.write(vulns)
        return vulns
    except:
        return "Error: No se pudieron capturar las vulnerabilidades"
