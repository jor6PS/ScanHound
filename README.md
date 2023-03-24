# ScanHound

## MODO DE USO

Simplemente ejecutar el archivo scanhound.py y seguir las isntrucciones. Para instalar las dependencias, estos son los únicos pasos 
- isntalar la libreria 'python-nmap'
- instalar el driver de Selenium, que se puede encontrar en la url 'https://github.com/mozilla/geckodriver/releases' y moverlo a la ruta /usr/local/bin

Esto generará un escaneo y guardará los resultados en una estructura de carpetas

## IMPORTAR NEO4J

Para cargar los archivos json en la base de datos Neo4j, seguir los siguietnes pasos:

1. Abre la consola de Neo4j y asegúrate de que la base de datos en la que deseas cargar el archivo esté activa.

2. Asegúrate de que la biblioteca de apoc esté instalada en la base de datos. Si no lo está, puedes descargarla desde aquí: https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/latest
    - Copia el archivo .jar descargado en la carpeta "plugins" de la instalación de Neo4j. La ruta a esta carpeta puede variar según la instalación, pero comúnmente se encuentra en /var/lib/neo4j/plugins o en C:\Program Files\Neo4j\plugins.
    - Añadir la líne 'apoc.import.file.enabled=true' en el fichero neo4j.conf
    - Reinicia Neo4j.
    - Verifica que la biblioteca APOC se haya cargado correctamente ejecutando el comando CALL dbms.procedures() en la consola de Neo4j. Si la biblioteca se cargó correctamente, deberías ver una lista de procedimientos que incluya los procedimientos APOC.

Para cargar un fichero JSON modificar la línea de código del programa Scan2Neo.py con el Json desado:

```python
file_path = "/home/kali/TFG/results/Casa/2023-03-24_192.168.15.0\\24/192.168.15.0\\25.json"
```

El resultado en Neo4 por el momento se muestar de la sigueitne manera:

## TODO

- Gestionar la carga de los ficheros de vulnerabilidades, código fuente y capturas de pantalla en la BBDD Neo4j.
