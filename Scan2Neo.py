from py2neo import Graph, Node, Relationship

# establecer conexión a la base de datos
graph = Graph("bolt://localhost:7687", auth=("neo4j", "neo4j1"))

# cargar archivo json en una variable
import json

file_path = "/home/kali/TFG/results/Casa/2023-03-24_192.168.15.0\\24/192.168.15.0\\25.json"
with open(file_path) as f:
    data = json.load(f)

# Recorremos los nodos principales (direcciones IP)
for ip, ports in data.items():
    # Merge or create the IP node
    ip_node = Node("IP", address=ip)
    existing_ip = graph.nodes.match("IP", address=ip).first()
    if existing_ip:
        ip_node = existing_ip
    else:
        graph.create(ip_node)

    # Create or merge the port nodes
    for port_number, port_data in ports.items():
        existing_port = graph.nodes.match("Port", number=port_number).first()

        if existing_port is not None:
            # Check if the attributes of the existing port are the same as the new port
            if all(existing_port.get(key) == value for key, value in port_data.items()):
                # If the attributes are the same, use the existing port node
                port_node = existing_port
            else:
                # If the attributes are different, create a new port node
                port_node = Node("Port", number=port_number, **port_data)
                graph.create(port_node)
        else:
            # If there is no existing port, create a new port node
            port_node = Node("Port", number=port_number, **port_data)
            graph.create(port_node)

        # Creamos una relación entre la dirección IP y el puerto
        ip_port_rel = Relationship(ip_node, "HAS_PORT", port_node)
        graph.create(ip_port_rel)
