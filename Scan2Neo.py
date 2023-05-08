import argparse
from py2neo import Graph, Node, Relationship
import json
import os

############################################################# CONEXIÓN BBDD ##############################################################################################################################


parser = argparse.ArgumentParser(description='Conectar a la base de datos Neo4j')
parser.add_argument('-r', '--ip', type=str, help='Dirección IP de la base de datos Neo4j', required=True)

args = parser.parse_args()

# Establecer conexión a la base de datos
graph = Graph("bolt://" + args.ip + ":7687", auth=("neo4j", "neo4j"))

try:
    graph.run("MATCH (n) RETURN count(n)")
except Exception as e:
    if "Failed to authenticate" in str(e):
        username = input("Introduzca su nombre de usuario: ")
        password = input("Introduzca su contraseña: ")
        graph = Graph("bolt://" + args.ip + ":7687", auth=(username, password))
    else:
        raise e

############################################################# BÚSQUEDA ITERATIVA DE JSONs ##############################################################################################################################

#Busca y mergea todos los ficheros json.new creados en cada directorio
def search_json_files(folder_path):
    json_files = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('json'):
                file_path = os.path.join(root, file)
                folder_name = os.path.dirname(file_path).replace(folder_path, '').lstrip(os.path.sep).split(os.path.sep)[0]
                json_files[folder_name] = json_files.get(folder_name, []) + [file_path]
    return json_files

json_files = search_json_files('results/')

############################################################# CREACIÓN DE LA BBDD ##############################################################################################################################

for organismo, files in json_files.items():
    print(f"Creando nodos de {organismo} en la BBDD Neo4j")
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)

            #Recorremos los nodos (Organismos)
            for org, org_data in data.items():
                #Create the ORG node
                org_node = Node("ORG", org=org)
                existing_org = graph.nodes.match("ORG", org=org).first()
                if existing_org:
                    org_node = existing_org
                else:
                    graph.create(org_node)

                #Recorremos los nodos (Segmentos)
                for seg, seg_data in org_data.items():
                    #Create the SEG node
                    seg_node = Node("SEG", seg=seg, org=org)
                    existing_seg = graph.nodes.match("SEG", seg=seg, org=org).first()
                    if existing_seg:
                        seg_node = existing_seg
                    else:
                        graph.create(seg_node)
                    # Create a relationship between the ORG and the SEG node
                    org_seg_rel = Relationship(org_node, "HAS_SEG", seg_node)
                    graph.create(org_seg_rel)

                    #Recorremos los nodos (Subred)
                    for subred, subred_data in seg_data.items():
                        #Create the subred node
                        subred_node = Node("Subred", range=subred, seg=seg, org=org)
                        existing_subred = graph.nodes.match("Subred", range=subred, seg=seg, org=org).first()
                        if existing_subred:
                            subred_node = existing_subred
                        else:
                            graph.create(subred_node)
                        # Create a relationship between the SEG and the Subred node
                        seg_sub_rel = Relationship(seg_node, "HAS_VISIBILITY", subred_node)
                        graph.create(seg_sub_rel)

                        #Recorremos los nodos (Ips)
                        for ip, ip_data in subred_data.items():
                            #Create the IP node
                            ip_node = Node("IP", address=ip, range=subred, seg=seg, org=org)
                            existing_ip = graph.nodes.match("IP", address=ip, range=subred, seg=seg, org=org).first()
                            if existing_ip:
                                ip_node = existing_ip
                            else:
                                graph.create(ip_node)
                            # Create a relationship between the Subred and the IP
                            sub_ip_rel = Relationship(subred_node, "HAS_IP", ip_node)
                            graph.create(sub_ip_rel)

                            #Recorremos los nodos (Port)
                            for port_number, port_data in ip_data["ports"].items():
                                #Create ports nodes
                                port_node = Node("Port", number=port_number, **port_data)
                                existing_port = graph.nodes.match("Port", number=port_number, **port_data).first()
                                if existing_port:
                                    port_node = existing_port
                                else:
                                    graph.create(port_node)
                                # Creamos una relación entre la dirección IP y el puerto
                                ip_port_rel = Relationship(ip_node, "HAS_PORT", port_node, Date=port_data["Date"])
                                graph.create(ip_port_rel)
                                
                                # Recorremos los puertos en busca de vulnerabilidades
                                if ("Error: No se pudieron capturar las vulnerabilidades" not in port_data["Vulners"]) and (port_data["Vulners"] != ""):
                                    vulners_node = Node("Vulners", vulns=port_data["Vulners"])
                                    existing_vulners = graph.nodes.match("Vulners", vulns=port_data["Vulners"]).first()
                                    if existing_vulners:
                                        vulners_node = existing_vulners
                                    else:
                                        graph.create(vulners_node)
                                    # Creamos una relación entre el puerto y las vulnerabilidades
                                    ports_vulns_rel = Relationship(port_node, "HAS_VULNS", vulners_node)
                                    graph.create(ports_vulns_rel)

                                # Recorremos los puertos en busca de códigos fuente
                                if ("Error: No se pudo obtener el codigo fuente" not in port_data["Web Source"]) and ("Error: La conexion se ha agotado" not in port_data["Web Source"]) and ("Error: No se pudo conectar al servicio web" not in port_data["Web Source"]) and (port_data["Web Source"] != ""):
                                    websource_node = Node("Web Source", websource=port_data["Web Source"])
                                    existing_websource= graph.nodes.match("Web Source", websource=port_data["Web Source"]).first()
                                    if existing_websource:
                                        websource_node = existing_websource
                                    else:
                                        graph.create(websource_node)
                                    # Creamos una relación entre el puerto y los códigos fuente
                                    ports_websource_rel = Relationship(port_node, "HAS_WEBSOURCE", websource_node)
                                    graph.create(ports_websource_rel)

                                # Recorremos los puertos en busca de capturas de pantalla
                                if ("Error al tomar la captura de pantalla de la URL" not in port_data["Screenshot"]) and (port_data["Screenshot"] != ""):
                                    Screenshot_node = Node("Screenshot", Screenshot=port_data["Screenshot"])
                                    existing_screenshot= graph.nodes.match("Screenshot", Screenshot=port_data["Screenshot"]).first()
                                    if existing_screenshot:
                                        Screenshot_node = existing_screenshot
                                    else:
                                        graph.create(Screenshot_node)
                                    # Creamos una relación entre el puerto y las capturas de pantalla
                                    ports_Screenshot_rel = Relationship(port_node, "HAS_SCREENSHOT", Screenshot_node)
                                    graph.create(ports_Screenshot_rel)
