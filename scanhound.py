import csv
import os
import nmap
import requests
from selenium import webdriver
import time

# Método para obtener el código fuente de un servicio web
def get_source(host, port, service):
    url = f"{service}://{host}:{port}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return "Error: No se pudo obtener el código fuente"
    except:
        return "Error: No se pudo conectar al servicio web"
    
# Función para tomar una captura de pantalla de una URL
def get_screenshot(host, port, service):
    try:
        url = f"{service}://{host}:{port}"
        driver = webdriver.Firefox()
        driver.get(url)
        time.sleep(5)
        image_file = f"/home/kali/TFG/{organizacion}/img/{host}_{port}.png"
        driver.save_screenshot(image_file)
        driver.quit()
        return image_file
    except:
        print("Error al tomar la captura de pantalla de la URL.")

# Pide al usuario que ingrese el nombre de la organización para la creación de directorios
organizacion = input("Ingresa el nomnbre de la organizacion (Ej. UOC, Google): ")
folder_path = f"/home/kali/TFG/{organizacion}"
folder_img_path = f"/home/kali/TFG/{organizacion}/img"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)
if not os.path.exists(folder_img_path):
    os.makedirs(folder_img_path)

# Pide al usuario que ingrese el rango de IP a escanear
ip_range = input("Ingresa el rango de IP a escanear (Ej. 192.168.1.0/24): ")

# Crea un objeto de tipo nmap.PortScanner()
scanner = nmap.PortScanner()

# Pide al usuario que ingrese el nombre del archivo CSV para guardar los resultados
filename = input("Ingresa el nombre del archivo CSV para guardar los resultados: ")
csv_path = f"/home/kali/TFG/{organizacion}/{filename}"

# Escaneo completo con información detallada
scanner.scan(hosts=ip_range, arguments='-sn')
all_hosts = len(scanner.all_hosts())

# Abre el archivo CSV en modo escritura y escribe los resultados
with open(csv_path, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')
    writer.writerow(['IP', 'Hostname', 'Protocol', 'Port', 'State', 'Service', 'Product', 'Version', 'Web Source', 'Screenshot'])

    # Escanea cada host de la red y muestra el progreso
    for i, host in enumerate(scanner.all_hosts()):
        print(f"Escaneando host {i+1}/{all_hosts}: {host}")
        scanner.scan(hosts=host, arguments='-A -Pn -n -T4 -sT -sV --version-intensity=5 --reason')
        for proto in scanner[host].all_protocols():
            lport = scanner[host][proto].keys()
            for port in lport:
                writer.writerow([
                host,
                scanner[host].hostname(),
                proto,
                port,
                scanner[host][proto][port]['state'],
                scanner[host][proto][port]['name'],
                scanner[host][proto][port]['product'],
                scanner[host][proto][port]['version'],
                get_source(host, port, scanner[host][proto][port]['name']) if scanner[host][proto][port]['name'] in ['http', 'https'] else "",
                get_screenshot(host, port, scanner[host][proto][port]['name']) if scanner[host][proto][port]['name'] in ['http', 'https'] else ""
                ])
