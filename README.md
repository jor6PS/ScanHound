# ScanHound

## IMPORTAR NEO4J

Para cargar los archivos json en la base de datos Neo4j, seguir los siguietnes pasos:

1. Abre la consola de Neo4j y asegúrate de que la base de datos en la que deseas cargar el archivo esté activa.

2. Asegúrate de que la biblioteca de apoc esté instalada en la base de datos. Si no lo está, puedes descargarla desde aquí: https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/latest
  2.1 Copia el archivo .jar descargado en la carpeta "plugins" de la instalación de Neo4j. La ruta a esta carpeta puede variar según la instalación, pero comúnmente se encuentra en /var/lib/neo4j/plugins o en C:\Program Files\Neo4j\plugins.
  2.2 Añadir la líne 'apoc.import.file.enabled=true' en el fichero neo4j.conf
  2.2 Reinicia Neo4j.
  2.3 Verifica que la biblioteca APOC se haya cargado correctamente ejecutando el comando CALL dbms.procedures() en la consola de Neo4j. Si la biblioteca se cargó correctamente, deberías ver una lista de procedimientos que incluya los procedimientos APOC.

En la consola de Neo4j, ejecuta el siguiente comando para cargar el archivo JSON en la base de datos:

```sql
// cargar archivo json en una variable
WITH 'file:{path del fichero JSON dentro de la carpeta /import de neo4j}' AS url
CALL apoc.load.json(url) YIELD value AS data

// crear nodos y relaciones
UNWIND keys(data) AS ip
MERGE (node_ip:IP {address: ip})
WITH node_ip, data[ip] AS ports
UNWIND keys(ports) AS port
MERGE (node_port:Port {number: port})
ON CREATE SET 
  node_port.Hostname = ports[port].Hostname,
  node_port.Protocol = ports[port].Protocol,
  node_port.State = ports[port].State,
  node_port.Service = ports[port].Service,
  node_port.Product = ports[port].Product,
  node_port.Version = ports[port].Version,
  node_port.Vulners = ports[port].Vulners,
  node_port.WebSource = ports[port].WebSource,
  node_port.Screenshot = ports[port].Screenshot
MERGE (node_ip)-[:CONNECTED_TO]->(node_port)
```
