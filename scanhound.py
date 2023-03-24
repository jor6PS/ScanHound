import json
import os
import nmap
import requests
from selenium import webdriver
import time
import datetime

# Obtiene la fecha actual en formato año-mes-día
date_today = datetime.datetime.today().strftime('%Y-%m-%d')

# Método para obtener el código fuente de un servicio web
def get_source(host, port, service):
    if service not in ["http", "https"] and ('4' in str(port)):
        url = f"https://{host}:{port}"
    elif service not in ["http", "https"] and ('4' not in str(port)):
        url = f"http://{host}:{port}"
    else:
        url = f"{service}://{host}:{port}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            source_file = f"{folder_src_path}/{host}_{port}.txt"
            with open(source_file, "w") as f:
                f.write(response.text)            
            return source_file
        else:
            return "Error: No se pudo obtener el codigo fuente"
    except:
        return "Error: No se pudo conectar al servicio web"
    
# Función para tomar una captura de pantalla de una URL
def get_screenshot(host, port, service):
    try:
        if service not in ["http", "https"] and ('4' in str(port)):
            url = f"https://{host}:{port}"
        elif service not in ["http", "https"] and ('4' not in str(port)):
            url = f"http://{host}:{port}"
        else:
            url = f"{service}://{host}:{port}"
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(5)
        image_file = f"{folder_img_path}/{host}_{port}.png"
        driver.save_screenshot(image_file)
        driver.quit()
        return image_file
    except:
        return "Error al tomar la captura de pantalla de la URL."

def get_vulns(host, port, vulns):
    try:
        vulns_file = f"{folder_vuln_path}/{host}_{port}.txt"
        with open(vulns_file, 'w') as f:
            f.write(vulns)
        return vulns_file
    except:
        return "Error: No se pudieron capturar las vulnerabilidades"
        
        
# Pide al usuario que ingrese el nombre de la organización para la creación de directorios
organizacion = input("Ingresa el nomnbre de la organizacion (Ej. UOC, Google): ")
folder_path = f"results/{organizacion}"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# Pide al usuario que ingrese el rango de IP a escanear y crea los directorios
ip_range = input("Ingresa el rango de IP a escanear (Ej. 192.168.1.0/24): ")
if '/' in ip_range:
    ip_range_name = ip_range.replace('/', ':')
else:
    ip_range_name = ip_range
scan_path = f"{folder_path}/{date_today}_{ip_range_name}"
json_path = f"{scan_path}/{ip_range_name}.json"
folder_img_path = f"{scan_path}/img"
folder_src_path = f"{scan_path}/source"
folder_vuln_path = f"{scan_path}/vuln"

if not os.path.exists(scan_path):
    os.makedirs(scan_path)
if not os.path.exists(folder_img_path):
    os.makedirs(folder_img_path)
if not os.path.exists(folder_src_path):
    os.makedirs(folder_src_path)
if not os.path.exists(folder_vuln_path):
    os.makedirs(folder_vuln_path)
    
    
# Crea un objeto de tipo nmap.PortScanner()
scanner = nmap.PortScanner()

# Comienza el escaneo
print("Comienza el escaneo!!!")

# Escaneo completo con información detallada
scanner.scan(hosts=ip_range, arguments='--min-rate 5000 -n -p-')
# Crear una lista para almacenar los puertos abiertos de cada host
hosts = {}
# Recorremos los resultados del escaneo
for host in scanner.all_hosts():
    # Obtenemos los puertos abiertos del host
    open_ports = []
    print('Host : %s (%s)' % (host, scanner[host].state()))
    for proto in scanner[host].all_protocols():
        lport = scanner[host][proto].keys()
        for port in lport:
            if scanner[host][proto][port]['state'] == 'open':
                open_ports.append(port)
    # Agregamos la relación entre el host y sus puertos abiertos al diccionario
    hosts[host] = open_ports
    if open_ports:
        print('Host : %s, Ports : %s' % (host, open_ports))

# Abre el archivo JSON en modo escritura y escribe los resultados
with open(json_path, 'w') as jsonfile:
    data = {}

    # Escaneo de puertos específicos en los hosts obtenidos
    num_host = 0
    for host in hosts:
        num_host += 1
        print(f"Escaneando host {num_host}/{len(hosts.keys())}: {host}")
        ports = ','.join(map(str, hosts[host]))
        scanner.scan(hosts=host, ports=ports, arguments='-A -Pn --script vulners')
        if host in scanner.all_hosts():
            host_data = {}
            for proto in scanner[host].all_protocols():
                lport = scanner[host][proto].keys()
                for port in lport:
                    host_data[port] = {
                        'Hostname': scanner[host].hostname(),
                        'Protocol': proto,
                        'State': scanner[host][proto][port]['state'],
                        'Service': scanner[host][proto][port]['name'],
                        'Product': scanner[host][proto][port]['product'],
                        'Version': scanner[host][proto][port]['version'],
                        'Vulners': get_vulns(host, port,scanner[host][proto][port]["script"]["vulners"]) if 'script' in scanner[host]['tcp'][port] and 'vulners' in scanner[host]['tcp'][port]['script'] else '',
                        'Web Source': get_source(host, port, scanner[host][proto][port]['name']) if scanner[host][proto][port]['name'] in ['http', 'https'] or port in [80, 443, 8080] else "",
                        'Screenshot': get_screenshot(host, port, scanner[host][proto][port]['name']) if scanner[host][proto][port]['name'] in ['http', 'https'] or port in [80, 443, 8080] else ""
                    }
            data[host] = host_data

    # Escribe los datos en formato JSON
    json.dump(data, jsonfile, indent=4)

