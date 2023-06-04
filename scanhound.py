from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from requests.exceptions import Timeout
from selenium import webdriver
import ipaddress
import datetime
import requests
import argparse
import base64
import time
import json
import nmap
import os

############################################################# VARIABLES GLOBALES ##############################################################################################################################

#Fecha actual en formato año-mes-día
date_today = datetime.datetime.today().strftime('%Y-%m-%d')
# Subredes privadas
private_subnets = [    
          ipaddress.ip_network('10.0.0.0/8'),
          ipaddress.ip_network('172.16.0.0/12'),
          ipaddress.ip_network('192.168.0.0/16'),
          ipaddress.ip_network('169.254.0.0/16')]

############################################################# FUNCTIONS ##################################################################################################################################

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
    url = f"http://{host}:{port}"
    # Configurar las opciones del navegador en modo headless
    options = Options()
    options.add_argument("--headless")
    # Crear una instancia del navegador con las opciones configuradas
    driver = webdriver.Firefox(options=options)
    driver.set_page_load_timeout(10)
    try:
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda driver: driver.execute_script('return document.readyState') == 'complete')
    except Exception as e:
        print(f"Error al tomar la captura de pantalla de la URL: {str(url)}")
        driver.quit()
        return ""
    finally:
        try:
            time.sleep(1)
            image_file = f"{folder_img_path}/{host}_{port}.png"
            driver.save_screenshot(image_file)
            screenshot_binary = driver.get_screenshot_as_png()
            print(f"Captura de pantalla guardada en {image_file}")
            driver.quit()
            return base64.b64encode(screenshot_binary).decode('utf-8')
        except Exception as e:
            print("Error al guardar la captura de pantalla de la URL: {str(url)}")
            driver.quit()
            return ""

def get_vulns(host, port, vulns):
    try:
        vulns_file = f"{folder_vuln_path}/{host}_{port}.txt"
        with open(vulns_file, 'w') as f:
            f.write(vulns)
        return vulns
    except:
        return "Error: No se pudieron capturar las vulnerabilidades"

############################################################# PARAMETROS COMMAND LINE #########################################################################################################################

# Definimos los argumentos que queremos recibir desde la línea de comandos
parser = argparse.ArgumentParser(description='Ejemplo de escaneo Nmap en Python')
parser.add_argument('-r', '--rango', type=str, help='IP o rango de IPs a escanear', required=True)
parser.add_argument('-o', '--org', type=str, help='Organizacion desde donde se lleva a cabo la auditoria', required=True)
parser.add_argument('-s', '--segmento', type=str, help='Segmento desde el que se ejecuta el escaneo', required=True)
parser.add_argument('--min-rate', action='store_true', help='Incluir un min-rate de 5000 en el escaneo')
# Creamos un grupo mutuamente excluyente para -a y --min-rate
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-a', '--argumentos', type=str, help='Argumentos a pasar a Nmap')
group.add_argument('--industrial', action='store_true', help='Tipo de escaneo (normal o industrial)')
# Parseamos los argumentos
args = parser.parse_args()
organizacion = args.org
segmento = args.segmento

############################################################# FOLDER CREATION ##################################################################################################################################

folder_path = f"results/{organizacion}/{segmento}"

if not os.path.exists(folder_path):
    os.makedirs(folder_path)

#Tratamiento de la ip o rango en caso de que contenga le simbolo /
if '/' in args.rango:
    ip_range_name = args.rango.replace('/', ':')
else:
    ip_range_name = args.rango
    
# Creacion de directorios
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

############################################################# FIRST SCAN ##################################################################################################################################

# Crea un objeto de tipo nmap.PortScanner()
scanner = nmap.PortScanner()
# Comienza el escaneo
print("Comienza el escaneo!!!")

# Si se incluyó el parámetro --industrial, escaneamos de la siguietne manera
if args.industrial:
    args.argumentos = '-Pn -n --open -p 21,22,23,25,53,80,88,102,104,110,111,135,137,138,139,143,389,443,445,502,636,993,995,1089,1090,1091,1234,1433,1541,1723,1883,8883,3306,3389,3480,4000,4840,4843,5050,5051,5052,5065,5450,5800,5900,5901,8080,9600,10307,10311,10364,10407,10409,10410,10412,10414,10415,10428,10431,10432,10447,10449,11001,12135,12136,12137,12316,12645,12647,12648,13722,13724,13782,13783,18000,1911,1962,20000,34962,34963,34964,34980,38000,38011,38014,38200,38210,38301,38400,38589,38593,38600,38700,38971,39129,39278,44818,45678,47808,50000,50001,50002,50003,50004,50005,50006,50007,50008,50009,50010,50011,50012,50013,50014,50015,50016,50018,50019,50020,50025,50026,50027,50028,50110,50111,55000,55003,55555,56001,56002,56003,56004,56005,56006,56007,56008,56009,56010,56011,56012,56013,56014,56015,56016,56017,56018,56019,56020,56021,56022,56023,56024,56025,56026,56027,56028,56029,56030,56031,56032,56033,56034,56035,56036,56037,56038,56039,56040,56041,56042,56043,56044,56045,56046,56047,56048,56049,56050,56051,56052,56053,56054,56055,56056,56057,56058,56059,56060,56061,56062,56063,56064,56065,56066,56067,56068,56069,56070,56071,56072,56073,56074,56075,56076,56077,56078,56079,56080,56081,56082,56083,56084,56085,56086,56087,56088,56089,56090,56091,56092,56093,56094,56095,56096,56097,56098,56099,62540,62544,62546,62547,62900,62911,62924,62930,62938,62956,62957,62963,62981,62982,62985,62992,63012,63027,63028,63029,63030,63031,63032,63033,63034,63035,63036,63041,63075,63079,63082,63088,63094,65443'

# Si se incluyó el parámetro --min-rate, agregamos la opción al escaneo
if args.min_rate:
    args.argumentos += ' --min-rate 5000'

# Escaneo para sacar los puertos abiertos
scanner.scan(hosts=args.rango, arguments=args.argumentos)

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

############################################################# SECOND SCAN ##################################################################################################################################

# Abre el archivo JSON en modo escritura y escribe los resultados
with open(json_path, 'w') as jsonfile:
    data = {organizacion: {segmento: {}}}
    # Escaneo de puertos específicos en los hosts obtenidos
    num_host = 0
    for host in hosts:
        num_host += 1
        print(f"Escaneando host {num_host}/{len(hosts.keys())}: {host}")
        ports = ','.join(map(str, hosts[host]))
        if args.industrial:
            scanner.scan(hosts=host, ports=ports, arguments='-Pn --open')
        else:
            scanner.scan(hosts=host, ports=ports, arguments='-A -Pn --script vulners --open')
        if host in scanner.all_hosts():
            # Determinar la subred a la que pertenece la IP
            ip = ipaddress.ip_address(host)
            subnet = None
            for private_subnet in private_subnets:
                if ip in private_subnet:
                    subnet = str(private_subnet)
                    break
                else:
                    subnet = "Public ip"
            
            # Crear el diccionario de datos para la IP actual
            host_data = {'ports': {}}
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
                        'Screenshot':  get_screenshot(host, port) if scanner[host][proto][port]['name'] in ['http', 'https'] else "",
                        'Date': date_today
                    }
            if subnet not in data[organizacion][segmento]:
                data[organizacion][segmento][subnet] = {}
            data[organizacion][segmento][subnet][host] = host_data

    # Escribe los datos en formato JSON
    json.dump(data, jsonfile, indent=4)
