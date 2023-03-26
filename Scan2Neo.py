from py2neo import Graph, Node, Relationship
import json
import os

# establecer conexión a la base de datos
graph = Graph("bolt://localhost:7687", auth=("neo4j", "neo4j1"))

def search_json_files(folder_path):
    json_files = {}
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith('.json'):
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
        date_str = file.split('_')[0]
        date_str = date_str.split('/')[2]
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
                    existing_port = graph.nodes.match("Port", number=port_number, date=date_str).first()
                    if existing_port is not None:
                        # Check if the attributes of the existing port are the same as the new port
                        if all(existing_port.get(key) == value for key, value in port_data.items()):
                            # If the attributes are the same, use the existing port node
                            port_node = existing_port
                        else:
                            # If the attributes are different, create a new port node
                            port_node = Node("Port", number=port_number, date=date_str, **port_data)
                            graph.create(port_node)
                    else:
                        # If there is no existing port, create a new port node
                        port_node = Node("Port", number=port_number, date=date_str, **port_data)
                        graph.create(port_node)
                    
                    # Creamos una relación entre la dirección IP y el puerto
                    ip_port_rel = Relationship(ip_node, "HAS_PORT", port_node)
                    graph.create(ip_port_rel)
