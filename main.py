import os
import json
import datetime
import ipaddress
import argparse
import nmap
from protocols.web import take_screenshot, get_source
from protocols.modbus_banner import modbus_banner
from protocols.bacnet_banner import bacnet_banner
import hostdiscovery

# Configuración global
date_today = datetime.datetime.today().strftime('%Y-%m-%d')
private_subnets = [
    ipaddress.ip_network(subnet) for subnet in ['10.0.0.0/8', '172.16.0.0/12', '192.168.0.0/16', '169.254.0.0/16']
]

scan_options = {
    'rapido': '-T4 -Pn --open',
    'normal': '-T3 -Pn --open',
    'lento': '-T2 -Pn --open --min-rate 100',
    'industrial': '--open -Pn --scan-delay 1s --max-parallelism 1 -p 21,22,23,80,102,104,443,445,502,530,593,789,1089-1091,1911,1962,2222,2404,4000,4840,4843,4911,5900,5901,8000,8080,9600,19999,20000,20547,34962-34964,34980,44818,46823,46824,47808,55000-55003',
    'industrial_rapido': '--open -Pn -p 21,22,23,80,102,104,443,445,502,530,593,789,1089-1091,1911,1962,2222,2404,4000,4840,4843,4911,5900,5901,8000,8080,9600,19999,20000,20547,34962-34964,34980,44818,46823,46824,47808,55000-55003',
    'industrial_udp': '--open -Pn -sU -p 21,22,23,80,102,104,443,445,502,530,593,789,1089-1091,1911,1962,2222,2404,4000,4840,4843,4911,5900,5901,8000,8080,9600,19999,20000,20547,34962-34964,34980,44818,46823,46824,47808,55000-55003'
}

# Argumentos
parser = argparse.ArgumentParser(description='Escaneo Nmap en Python')
parser.add_argument('-r', '--rango', type=str, required=True, help='IP o rango a escanear')
parser.add_argument('-o', '--org', type=str.upper, required=True, help='Organización')
parser.add_argument('-s', '--desde', type=str.upper, required=True, help='Ubicación de escaneo')
parser.add_argument('-i', '--interfaz', type=str, default='eth0', help='Interfaz de red')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('--custom', type=str, help='Argumentos personalizados para Nmap')
for key in scan_options:
    group.add_argument(f'--{key}', action='store_true', help=f'Escaneo {key}')
parser.add_argument('--hostdiscovery', action='store_true', help='Descubrimiento de hosts activos')
args = parser.parse_args()

# Creación de directorios
folder_path = f"results/{args.org}/{args.desde}"
os.makedirs(folder_path, exist_ok=True)
for subfolder in ["img", "source", "vuln"]:
    os.makedirs(f"{folder_path}/{subfolder}", exist_ok=True)

# Definir rango de IPs
discovered_ips = set()
if args.hostdiscovery:
    print("Discovering hosts...")
    discovered_ips = hostdiscovery.extraer_ips(hostdiscovery.escanear_arp_scan(args.interfaz, args.rango))
    discovered_ips.update(hostdiscovery.escanear_ping_concurrente(args.rango))
    discovered_ips.discard(hostdiscovery.obtener_ip_local())
    rango_ips = ' '.join(discovered_ips) if discovered_ips else args.rango
else:
    rango_ips = args.rango

# Escaneo Nmap
scanner = nmap.PortScanner()
if args.custom:
    scan_arg = args.custom
else:
    scan_arg = next((scan_options[key] for key in scan_options if getattr(args, key, False)), None)
    if scan_arg is None:
        parser.error("Debe seleccionar un tipo de escaneo o usar --custom para un escaneo personalizado.")

print("Scanning...")
scanner.scan(hosts=rango_ips, arguments=scan_arg)

# Guardado de resultados
json_path = f"{folder_path}/scan_result.json"
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        scan_results = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    scan_results = {}
scan_results.setdefault(args.org, {}).setdefault(args.desde, {})

for host in scanner.all_hosts():
    ip = ipaddress.ip_address(host)
    subnet = next((str(sub) for sub in private_subnets if ip in sub), "Public IP")
    host_data = scan_results[args.org][args.desde].setdefault(subnet, {}).setdefault(host, {})
    
    for proto in scanner[host].all_protocols():
        for port, port_data in scanner[host][proto].items():
            if port_data['state'] == 'open':  # Filtra solo puertos abiertos
                key = f"{port}/{proto}"
                existing_data = host_data.setdefault(key, {})
                
                def update_if_empty(field, value):
                    if existing_data.get(field) in [None, "", "null"]:
                        existing_data[field] = value
                
                update_if_empty('Hostname', scanner[host].hostname())
                update_if_empty('State', port_data['state'])
                update_if_empty('Reason', port_data['reason'])
                update_if_empty('Name', port_data['name'])
                update_if_empty('Product', port_data['product'])
                update_if_empty('Version', port_data['version'])
                update_if_empty('Extrainfo', port_data['extrainfo'])
                update_if_empty('Conf', port_data['conf'])
                update_if_empty('Cpe', port_data['cpe'])
                update_if_empty('Date', date_today)
                
                service_name = port_data['name'].lower()
                if port in {80, 8080, 443, 8000} or 'http' in service_name:
                    print("puerto Web detectado: ", host, ":", port, "Escaneando...")
                    update_if_empty('Screenshot', take_screenshot(host, port, f"{folder_path}/img"))
                    update_if_empty('Websource', get_source(host, port, f"{folder_path}/source"))
                elif port == 502:
                    print("puerto Modbus detectado: ", host, ":", port, "Escaneando...")
                    update_if_empty('modbus_banner', modbus_banner(host))
                elif port == 47808:
                    print("puerto Bacnet detectado: ", host, ":", port, "Escaneando...")
                    update_if_empty('bacnet_banner', bacnet_banner(host))


with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(scan_results, f, indent=4, ensure_ascii=False)

# Mostrar resultados
for subnet, hosts in scan_results[args.org][args.desde].items():
    print(f"Subred: {subnet}")
    for host, data in hosts.items():
        print(f"  Host: {host}")
        for port, details in data.items():
            print(f"    Puerto: {port}, Hostname: {details['Hostname']}, Servicio: {details['Name']}")
