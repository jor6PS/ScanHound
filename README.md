# ScanHound

## MODO DE USO

### ESCANEO

Simplemente ejecutar el archivo **scanhound.py** con los parámetros requeridos y seguir las isntrucciones.

Esto generará un escaneo y guardará los resultados en una estructura de carpetas y un fichero JSON.

### IMPORTAR RESULTADO A LA BBDD NEO4J

Para cargar los resultados en la BBDD Neo4j simplemente ejecutar el script **Scan2Neo.py**

El resultado en Neo4 por el momento se muestar de la sigueitne manera:

![Alt text](https://github.com/jor6PS/ScanHound/blob/main/images/grafo_scanhound_4.png?raw=true "Estado actual")

### DEPENDENCIAS

Para instalar las dependencias, estos son los únicos pasos 
- isntalar la libreria 'python-nmap'
- instalar el driver de Selenium, que se puede encontrar en la url 'https://github.com/mozilla/geckodriver/releases' y moverlo a la ruta /usr/local/bin

## TODO

- Gestionar la carga de los ficheros de vulnerabilidades, código fuente y capturas de pantalla en la BBDD Neo4j.

## QUERIES

MATCH x=(o:ORG)-[:HAS_SEG]->(s:SEG)-[:HAS_SUBNET]->(sb:Subnet)-[:HAS_IP]->(ip:IP)-[:HAS_PORT]->(p:Port)
Where p.number="80"
RETURN x

![Alt text](https://github.com/jor6PS/ScanHound/blob/main/images/grafo_scanhound_2.png?raw=true "Resultado consulta")
