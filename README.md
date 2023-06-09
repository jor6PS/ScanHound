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

- Para el dashboard de los activos pivote comprobar el ip.address y el p.hostname y quitar el nodo origen para obtener un grafo asi:  [Seg1]->(ip)<-[Seg2]
- Meter tambien la cuenta del nº total de activos inseguros (con protocolos inseguros)
- Hacer un filtro por ip para el grafo de activos similares en base a las capturas de pantall. De esta manera mostrar solo los equipos iguales a este activo especificado
- Mostrar toda la cantidad de subredes /24 encontradas
- Incluir un departamento nuevo para el control de activos y servicios entre escaneos con fechas diferentes

- Escala logarítmica para el gráfico coparativos entre organiaciones, Para los valores, sacar porcentaje del total de activos por cada organización

## QUERIES

MATCH x=(o:ORG)-[:HAS_SEG]->(s:SEG)-[:HAS_SUBNET]->(sb:Subnet)-[:HAS_IP]->(ip:IP)-[:HAS_PORT]->(p:Port)
Where p.number="80"
RETURN x

![Alt text](https://github.com/jor6PS/ScanHound/blob/main/images/grafo_scanhound_2.png?raw=true "Resultado consulta")
