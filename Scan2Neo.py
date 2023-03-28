from py2neo import Graph, Node, Relationship
import json
import os

# establecer conexión a la base de datos
graph = Graph("bolt://localhost:7687", auth=("neo4j", "neo4j1"))

#Busca y mergea todos los ficheros json
def update_json_files(path):
    folders = []
    with os.scandir(path) as entries:
        for entry in entries:
            if entry.is_dir():
                folders.append(entry.name)
    for directory_path in folders:
        output = {}
        for subdir, dirs, files in os.walk(os.path.join(path, directory_path)):
            for file_name in files:
                if file_name.endswith('.json'):
                    with open(os.path.join(subdir, file_name)) as f:
                        data = json.load(f)
                        for ip, ip_data in data.items():
                            if ip not in output:
                                output[ip] = {}
                                output[ip]['ports'] = {}
                                output[ip]['subred'] = ip_data['subred']
                            for port, port_data in ip_data['ports'].items():
                                if port not in output[ip]['ports']:
                                    output[ip]['ports'][port] = {}
                                for key, value in port_data.items():
                                    if value == '' or 'Error' in value:
                                        output[ip]['ports'][port][key] = value
                                    else:
                                        output[ip]['ports'][port][key] = value
        with open(os.path.join(path, directory_path, 'output.json.new'), 'w') as f:
            json.dump(output, f, indent=4)

update_json_files('results/')

def search_json_files(folder_path):
    json_files = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json.new'):
                file_path = os.path.join(root, file)
                folder_name = os.path.dirname(file_path).replace(folder_path, '').lstrip(os.path.sep).split(os.path.sep)[0]
                json_files[folder_name] = json_files.get(folder_name, []) + [file_path]
    return json_files

json_files = search_json_files('results/')

for folder, files in json_files.items():
    # Creamos el nodo del folder y lo agregamos a la base de datos
    folder_node = Node("Folder", name=folder)
    existing_folder = graph.nodes.match("Folder", name=folder).first()
    if existing_folder:
        folder_node = existing_folder
    else:
        graph.create(folder_node)
    
    for file in files:
        with open(file, 'r') as f:
            data = json.load(f)

            # Recorremos los nodos principales (direcciones IP)
            for ip, ip_data in data.items():
                # Merge or create the IP node
                ip_node = Node("IP", address=ip)
                existing_ip = graph.nodes.match("IP", address=ip).first()
                if existing_ip:
                    ip_node = existing_ip
                else:
                    graph.create(ip_node)
                    
                # Create or merge the subnet nodes
                if "subred" in ip_data:
                    subnet = ip_data["subred"]
                    subnet_node = Node("Subnet", address=subnet)
                    existing_subnet = graph.nodes.match("Subnet", address=subnet).first()
                    if existing_subnet:
                        subnet_node = existing_subnet
                    else:
                        graph.create(subnet_node)

                    # Creamos una relación entre el folder y la dirección IP
                    folder_subnet_rel = Relationship(folder_node, "HAS_SUBNET", subnet_node)
                    graph.create(folder_subnet_rel)
                    
                    # Creamos una relación entre el folder y la dirección IP
                    folder_ip_rel = Relationship(subnet_node, "HAS_IP", ip_node)
                    graph.create(folder_ip_rel)
                else:
                    # Creamos una relación entre el folder y la dirección IP
                    folder_ip_rel = Relationship(folder_node, "HAS_IP", ip_node)
                    graph.create(folder_ip_rel)
                        
                # Create or merge the port nodes
                for port_number, port_data in ip_data["ports"].items():
                    port_node = Node("Port", number=port_number, **port_data)
                    existing_port = graph.nodes.match("Port", number=port_number, **port_data).first()
                    if existing_port:
                        port_node = existing_port
                    else:
                        graph.create(port_node)
                        
                    # Creamos una relación entre la dirección IP y el puerto
                    ip_port_rel = Relationship(ip_node, "HAS_PORT", port_node)
                    graph.create(ip_port_rel)
                    
                    # Recorremos los puertos en busca de vulnerabilidades
                    if ("Error: No se pudieron capturar las vulnerabilidades" not in port_data["Vulners"]) or (port_data["Vulners"] != ""):
                        vulners = port_data["Vulners"]
                        vulners_node = Node("Vulners", vulns=vulners)
                        existing_vulners = graph.nodes.match("Vulners", vulns=vulners).first()
                        if existing_vulners:
                            vulners_node = existing_vulners
                        else:
                            graph.create(vulners_node)
                            
                        # Creamos una relación entre el puerto y las vulnerabilidades
                        ports_vulns_rel = Relationship(port_node, "HAS_VULNS", vulners_node)
                        graph.create(ports_vulns_rel)

                    # Recorremos los puertos en busca de códigos fuente
                    if ("Error: No se pudo obtener el codigo fuente" not in port_data["Web Source"]) and ("Error: No se pudo conectar al servicio web" not in port_data["Web Source"]) and ("Error: La conexion se ha agotado (timeout)" not in port_data["Web Source"]) and (port_data["Web Source"] != ""):
                        WebSource = port_data["Web Source"]
                        websource_node = Node("Web Source", websource=WebSource)
                        existing_websource = graph.nodes.match("Web Source", websource=WebSource).first()
                        if existing_websource:
                            websource_node = existing_websource
                        else:
                            graph.create(websource_node)
                            
                        # Creamos una relación entre el puerto y los códigos fuente
                        ports_websource_rel = Relationship(port_node, "HAS_WEBSOURCE", websource_node)
                        graph.create(ports_websource_rel)

                    # Recorremos los puertos en busca de capturas de pantalla
                    if ("Error al tomar la captura de pantalla de la URL." not in port_data["Screenshot"]) and (port_data["Screenshot"] != ""):
                        Screenshot = port_data["Screenshot"]
                        Screenshot_node = Node("Screenshot", Screenshot=Screenshot)
                        existing_Screenshot = graph.nodes.match("Screenshot", Screenshot=Screenshot).first()
                        if existing_Screenshot:
                            Screenshot_node = existing_Screenshot
                        else:
                            graph.create(Screenshot_node)
                            
                        # Creamos una relación entre el puerto y los códigos fuente
                        ports_Screenshot_rel = Relationship(port_node, "HAS_SCREENSHOT", Screenshot_node)
                        graph.create(ports_Screenshot_rel)
