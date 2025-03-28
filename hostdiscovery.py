import subprocess
import re
import socket
import ipaddress
import concurrent.futures

def obtener_ip_local():
    """Obtiene la IP local de la máquina."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(('10.254.254.254', 1))
            return s.getsockname()[0]
    except Exception:
        return '127.0.0.1'

def escanear_arp_scan(interfaz, rango):
    """Ejecuta un escaneo ARP en la interfaz y rango especificado."""
    comando = ["sudo", "arp-scan", "--interface", interfaz, rango]
    try:
        return subprocess.check_output(comando, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error ejecutando el comando: {' '.join(comando)}\nSalida de error: {e.output}")
        return e.output

def escanear_ping_concurrente(rango, num_threads=10):
    """Escanea una red mediante ping de forma concurrente."""
    def ping_ip(ip):
        try:
            output = subprocess.check_output(['ping', '-c', '1', '-W', '1', str(ip)], stderr=subprocess.STDOUT, text=True)
            return str(ip) if "1 packets transmitted, 1 received, 0% packet loss" in output else None
        except subprocess.CalledProcessError:
            return None
    
    network = ipaddress.IPv4Network(rango, strict=False)
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        return {ip for ip in executor.map(ping_ip, network.hosts()) if ip}

def extraer_ips(output):
    """Extrae direcciones IP de una cadena de salida."""
    return set(re.findall(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', output))
