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

- Modificar el primer escaneo para que haga un barrido por ping como la herramienta ICMP-SCAN. Incluirlo directamente en el json y el siguiente escaneo de servicios que comolemente la información
- Guardar la información del escaneo ping en csv para cada uno de los escaneos
- incluir el modo --idustrial-hardcore para que unicamente realice el primer escaneo icmp sin escanear servicios
---------
- Cambiar en scan2neo la detección de subredes para que obtenga los /24 de cada una de las ips detectadas en vez de especificar los rangos a mano. si es una ip publica, generar un nodo que sea "ips publica"
---------
- Para el dashboard de los activos pivote comprobar el ip.address y el p.hostname y quitar el nodo origen para obtener un grafo asi:  [Seg1]->(ip)<-[Seg2] - DELAYED
- Meter tambien la cuenta del nº total de activos inseguros (con protocolos inseguros) - DONE
- Hacer un filtro por ip para el grafo de activos similares en base a las capturas de pantall. De esta manera mostrar solo los equipos iguales a este activo especificado - DELAYED
- Mostrar toda la cantidad de subredes /24 encontradas - DONE
- Incluir un departamento nuevo para el control de cambios de activos y servicios entre escaneos con fechas diferentes - HALF DONE
- Escala logarítmica para el gráfico coparativos entre organiaciones, Para los valores, sacar porcentaje del total de activos por cada organización - HALF DONE

## QUERIES

MATCH x=(o:ORG)-[:HAS_SEG]->(s:SEG)-[:HAS_SUBNET]->(sb:Subnet)-[:HAS_IP]->(ip:IP)-[:HAS_PORT]->(p:Port)
Where p.number="80"
RETURN x

![Alt text](https://github.com/jor6PS/ScanHound/blob/main/images/grafo_scanhound_2.png?raw=true "Resultado consulta")
