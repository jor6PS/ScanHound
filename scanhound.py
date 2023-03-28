from selenium.common.exceptions import TimeoutException
from requests.exceptions import Timeout
from selenium import webdriver
import ipaddress
import datetime
import requests
import time
import json
import nmap
import os

# Obtiene la fecha actual en formato año-mes-día
date_today = datetime.datetime.today().strftime('%Y-%m-%d')

# Subredes privadas de la IANA
private_subnets = [    
          ipaddress.ip_network('10.32.0.0/23'),
          ipaddress.ip_network('10.32.2.0/24'),
          ipaddress.ip_network('10.32.16.0/23'),
          ipaddress.ip_network('10.32.18.0/24'),
          ipaddress.ip_network('10.32.19.0/24'),
          ipaddress.ip_network('10.32.20.0/23'),
          ipaddress.ip_network('10.32.22.0/24'),
          ipaddress.ip_network('10.32.23.0/24'),
          ipaddress.ip_network('10.32.24.0/24'),
          ipaddress.ip_network('10.32.25.0/24'),
          ipaddress.ip_network('10.32.26.0/24'),
          ipaddress.ip_network('10.32.28.0/23'),
          ipaddress.ip_network('10.32.30.0/24'),    
          ipaddress.ip_network('10.32.31.0/24')]

def get_source(host, port):
    url = f"http://{host}:{port}"
    try:
        response = requests.get(url, timeout=5) # Agrega timeout de 5 segundos
        if response.status_code == 200:
            source_file = f"{folder_src_path}/{host}_{port}.txt"
            with open(source_file, "w") as f:
                f.write(response.text)            
            return response.text
        else:
            return "Error: No se pudo obtener el codigo fuente"
    except Timeout: # Maneja la excepción Timeout
        return "Error: La conexion se ha agotado (timeout)"
    except:
        return "Error: No se pudo conectar al servicio web"
    
# Función para tomar una captura de pantalla de una URL
def get_screenshot(host, port):
    try:
        url = f"http://{host}:{port}"
        driver = webdriver.Firefox()
        driver.set_page_load_timeout(15)
        driver.get(url)
        # Establecer un temporizador de 5 segundos para la captura de pantalla
        time.sleep(5)
        image_file = f"{folder_img_path}/{host}_{port}.png"
        driver.save_screenshot(image_file)
        screenshot_binary = driver.get_screenshot_as_png()
        driver.quit()
        return base64.b64encode(screenshot_binary).decode('utf-8')
    except TimeoutException as e:
        print(f"Timeout al cargar la página en {host}:{port}.")
        driver.quit()
        return "Error al tomar la captura de pantalla de la URL."
    except:
        # Si no se puede tomar la captura de pantalla, cerrar el controlador y continuar
        driver.quit()
        return "Error al tomar la captura de pantalla de la URL."

def get_vulns(host, port, vulns):
    try:
        vulns_file = f"{folder_vuln_path}/{host}_{port}.txt"
        with open(vulns_file, 'w') as f:
            f.write(vulns)
        return vulns
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
            # Determinar la subred a la que pertenece la IP
            ip = ipaddress.ip_address(host)
            subnet = None
            for private_subnet in private_subnets:
                if ip in private_subnet:
                    subnet = private_subnet
                    break
            
            # Crear el diccionario de datos para la IP actual
            host_data = {'ports': {}}
            if subnet is not None:
                host_data['subred'] = str(subnet)
            for proto in scanner[host].all_protocols():
                lport = scanner[host][proto].keys()
                for port in lport:
                    host_data['ports'][port] = {
                        'Hostname': scanner[host].hostname(),
                        'Protocol': proto,
                        'State': scanner[host][proto][port]['state'],
                        'Service': scanner[host][proto][port]['name'],
                        'Product': scanner[host][proto][port]['product'],
                        'Version': scanner[host][proto][port]['version'],
                        'Vulners': get_vulns(host, port,scanner[host][proto][port]["script"]["vulners"]) if 'script' in scanner[host]['tcp'][port] and 'vulners' in scanner[host]['tcp'][port]['script'] else "",
                        'Web Source': get_source(host, port) if scanner[host][proto][port]['name'] in ['http', 'https'] else "",
                        'Screenshot': get_screenshot(host, port) if scanner[host][proto][port]['name'] in ['http', 'https'] else ""
                    }
            data[host] = host_data

    # Escribe los datos en formato JSON
    json.dump(data, jsonfile, indent=4)
