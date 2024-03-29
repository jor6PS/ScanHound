# ScanHound

## MODO DE USO

### ESCANEO

Simplemente ejecutar el archivo **scanhound.py** con los parámetros requeridos y seguir las isntrucciones.

Esto generará un escaneo y guardará los resultados en una estructura de carpetas y un fichero JSON.

### IMPORTAR RESULTADO A LA BBDD NEO4J

Para cargar los resultados en la BBDD Neo4j simplemente ejecutar el script **Scan2Neo.py -r <ip Neo4j>**

El resultado en Neo4j por el momento se muestar de la sigueitne manera:

![Alt text](https://github.com/jor6PS/ScanHound/blob/main/images/grafo_scanhound_4.png?raw=true "Estado actual")
![Alt text](https://github.com/jor6PS/ScanHound/blob/main/images/Captura%20de%20pantalla%202023-06-12%20140444.png?raw=true "Estado actual 2")

La aplicación NeoDash se mantiene en constante comunicación con la BBDD de Neo4j y este es el Dashboard creado para presentar los escaneos realizados:

![Alt text](https://github.com/jor6PS/ScanHound/blob/main/images/NeoDash%20-%20Neo4j%20Dashboard%20Builder%20%E2%80%94%20Mozilla%20Firefox%202023-06-12%2013-56-03.gif "Dashboard")

### INSTALACIÓN (PRIMERA VEZ)

Para instalar las dependencias en **scanhound.py**, estos son los únicos pasos 
- Instalar la librería 'python-nmap' (pip install python-nmap)
- Instalar el driver de Selenium, que se puede encontrar en la url 'https://github.com/mozilla/geckodriver/releases' y moverlo a la ruta /usr/local/bin

Para instalar las dependencias en **scan2neo.py**, estos son los únicos pasos
- Instalar la librería 'py2neo' (pip install py2neo)
- Ejecutar neo4j (sudo neo4j console)
- Ejecutar neodash para visualizar los Dashboards (sudo docker run -it --rm -p 5005:5005 neo4jlabs/neodash)

## TODO

- Modificar el primer escaneo para que haga un barrido por ping como la herramienta ICMP-SCAN. Incluirlo directamente en el json y el siguiente escaneo de servicios que comolemente la información
- Guardar la información del escaneo ping en csv para cada uno de los escaneos
- incluir el modo --idustrial-hardcore para que unicamente realice el primer escaneo icmp sin escanear servicios
---------
- Cambiar en scan2neo la detección de subredes para que obtenga los /24 de cada una de las ips detectadas en vez de especificar los rangos a mano. si es una ip publica, generar un nodo que sea "ips publica" - DONE
---------
- Para el dashboard de los activos pivote comprobar el ip.address y el p.hostname y quitar el nodo origen para obtener un grafo asi:  [Seg1]->(ip)<-[Seg2] - DELAYED
- Meter tambien la cuenta del nº total de activos inseguros (con protocolos inseguros) - DONE
- Hacer un filtro por ip para el grafo de activos similares en base a las capturas de pantall. De esta manera mostrar solo los equipos iguales a este activo especificado - DELAYED
- Mostrar toda la cantidad de subredes /24 encontradas - DONE
- Incluir un departamento nuevo para el control de cambios de activos y servicios entre escaneos con fechas diferentes - HALF DONE
- Escala logarítmica para el gráfico coparativos entre organiaciones, Para los valores, sacar porcentaje del total de activos por cada organización - HALF DONE
---------
- Actualizar el README
