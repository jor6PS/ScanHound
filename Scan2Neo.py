from py2neo import Graph, Node, Relationship
import argparse
import json
import os

def connect_to_neo4j(ip):
    """Conectar a la base de datos Neo4j."""
    try:
        graph = Graph(f"bolt://{ip}:7687", auth=("neo4j", "neo4j1"))
        graph.run("MATCH (n) RETURN count(n)")  # Verificar la conexión
        return graph
    except Exception as e:
        if "Failed to authenticate" in str(e):
            # Si la autenticación falla, pedir credenciales al usuario
            username = input("Usuario: ")
            password = input("Contraseña: ")
            return Graph(f"bolt://{ip}:7687", auth=(username, password))
        raise e

def search_json_files(folder_path):
    """Buscar todos los archivos JSON en una carpeta y sus subcarpetas."""
    json_files = {}
    for root, _, files in os.walk(folder_path):
        folder_name = os.path.relpath(root, folder_path) or "root"
        json_files[folder_name] = [os.path.join(root, f) for f in files if f.endswith('.json')]
        if json_files[folder_name]:
            print(f"Se encontraron archivos JSON en: {folder_name}")
    return json_files

def create_or_merge_node(graph, label, match_props, **properties):
    """Crear o actualizar un nodo en Neo4j."""
    properties = {k: json.dumps(v) if isinstance(v, (dict, list, set)) else v for k, v in properties.items()}
    node = graph.nodes.match(label, **match_props).first()
    if node:
        node.update(properties)
        graph.push(node)
    else:
        properties.update(match_props)
        node = Node(label, **properties)
        graph.create(node)
    return node

def create_or_update_relationship(graph, start_node, end_node, rel_type, **properties):
    """Crear o actualizar una relación entre nodos."""
    if start_node and end_node:
        rel = Relationship(start_node, rel_type, end_node, **properties)
        graph.create(rel)

def process_json(graph, json_files):
    """Procesar los archivos JSON y crear nodos y relaciones correspondientes en Neo4j."""
    ip_ports_map = {}

    for folder_name, files in json_files.items():
        for file in files:
            with open(file, 'r') as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Error al leer el archivo {file}: {e}")
                    continue
                print(f"Procesando archivo {file}...")
                for org, org_data in data.items():
                    org_node = create_or_merge_node(graph, "ORG", {"org": org})
                    for seg, seg_data in org_data.items():
                        seg_node = create_or_merge_node(graph, "SEG", {"org": org, "SEG": seg})
                        create_or_update_relationship(graph, org_node, seg_node, "HAS_SEG")
                        for subnet, subnet_data in seg_data.items():
                            subnet_node = create_or_merge_node(graph, "Subred", {"org": org, "SEG": seg, "Subred": subnet})
                            create_or_update_relationship(graph, seg_node, subnet_node, "HAS_SUBNET")
                            for ip, ip_data in subnet_data.items():
                                ip_node = create_or_merge_node(graph, "IP", {"org": org, "SEG": seg, "Subred": subnet, "IP": ip})
                                create_or_update_relationship(graph, subnet_node, ip_node, "HAS_IP")
                                ip_ports_map[ip] = {}
                                for port, port_data in ip_data.items():
                                    port_node = create_or_merge_node(graph, "Port", {"org": org, "SEG": seg, "Subred": subnet, "IP": ip, "number": port})
                                    create_or_update_relationship(graph, ip_node, port_node, "HAS_PORT")
                                    port_node.update(port_data)
                                    graph.push(port_node)
                                    ip_ports_map[ip][port] = port_data

    return ip_ports_map

def main():
    """Función principal para ejecutar el script."""
    parser = argparse.ArgumentParser(description='Conectar a la base de datos Neo4j')
    parser.add_argument('-r', '--ip', type=str, required=True, help='IP de la base de datos Neo4j')
    args = parser.parse_args()

    # Conectar al servidor Neo4j
    graph = connect_to_neo4j(args.ip)

    # Buscar archivos JSON
    json_files = search_json_files('results/')

    # Procesar los archivos JSON
    ip_port_map = process_json(graph, json_files)

if __name__ == "__main__":
    main()
