# ScanHound

## Índice
- [Introducción](#introduccion)
- [Modo de uso](#modo-de-uso)
  - [Escaneo](#escaneo)
  - [Ejemplos de uso](#ejemplos-de-uso)
  - [Importar resultados en Neo4j](#importar-resultados-en-neo4j)
- [Preparar el entorno](#preparar-el-entorno)
- [Instalación](#instalacion)
- [TODO](#todo)

## Introducción
ScanHound es una herramienta de escaneo de redes que permite detectar servicios abiertos y representarlos visualmente en Neo4j y en un DashBoard con consultas preestablecidas. Consta de dos componentes principales:
1. **main.py**: Realiza el escaneo de red y almacena los resultados en JSON.
2. **scan2neo.py**: Procesa los archivos JSON y los importa a Neo4j para su análisis visual.

## Modo de uso

### Escaneo
Para ejecutar un escaneo, simplemente ejecuta el script **main.py** con los parámetros requeridos:

```bash
python3 main.py -r <rango_de_IPs> -o <organizacion> -s <ubicacion desde la que se ejecuta el escaneo> [opciones]
```

ScanHound permite dhacer un descubrimiento de activos inicial y diferentes tipos de escaneo según las necesidades del usuario:

Descubrimiento de activos:

- `--hostdiscovery`: Diferentes técnicas de descubrimeinto ARP e ICMP para focalizar el escaneo posterior y reducir tiempo

Descubrimiento de servicios:

- `--rapido`: Escaneo rápido de puertos y servicios '-T4 -Pn --open'
- `--normal`: Escaneo estandard '-T3 -Pn --open'
- `--lento`: Escaneo lento para ocasiones en las que se pueda saturar la red '-T2 -Pn --open --min-rate 100'
- `--industrial`: Escaneo con puertos industriales epecíficos lento y seguro
- `--industrial_rapido`: Escaneo con puertos industriales específicos más rápido
- `--industrial_udp`: Escaneo con puertos industriales epecíficos solo UDP

### Ejemplos de uso

Escaneo normal de una red específica:
```bash
python3 main.py -r 192.168.1.0/24 -o "EmpresaX" -s "Oficina" --hostdiscovery --normal
```

Escaneo rápido:
```bash
python3 main.py -r 10.0.0.0/16 -o "DataCenter" -s "Zona1" --rapido
```

Modo "industrial_rapido" para entornos industriales:
```bash
python3 main.py -r 192.168.100.0/24 --hostdiscovery --industrial_rapido
```

Esto generará un escaneo y guardará los resultados en `results/` en formato JSON. Es posible ejecutar varios tipos de escaneo sobre una misma red, siempre que la organización y la ubicación sea la misma se irán actualizando y combinando los resultados.

### Importar resultados en Neo4j
Para cargar los resultados en la base de datos Neo4j, ejecuta el siguiente comando:

```bash
python3 scan2neo.py -r <IP_Neo4j>
```

Los resultados se representarán en Neo4j de la siguiente manera:

![Estado actual](https://github.com/jor6PS/ScanHound/blob/main/images/grafo_scanhound_4.png?raw=true)

![Estado actual 2](https://github.com/jor6PS/ScanHound/blob/main/images/Captura%20de%20pantalla%202023-06-12%20140444.png?raw=true)

NeoDash mantiene una comunicación constante con Neo4j y ofrece un dashboard interactivo para visualizar los escaneos:

![Dashboard](https://github.com/jor6PS/ScanHound/blob/main/images/NeoDash%20-%20Neo4j%20Dashboard%20Builder%20%E2%80%94%20Mozilla%20Firefox%202023-06-12%2013-56-03.gif)


### Preparar el entorno 

Intalar y Ejecutar Neo4j:
```bash
sudo neo4j console
```
Ejecutar NeoDash y conectarno a nuestra BBDD Neo4j para visualizar los dashboards:
```bash
sudo docker run -it --rm -p 5005:5005 neo4jlabs/neodash
```

Acceder a la web desde http://localhost:5005 e importar el archivo **dashboard.json**

## Instalación

Se ha preparado un fichero con las dependencias requeriments.txt, para intalarlas ejecutar:
```bash
pip install -r requirements.txt
```
Si da error preparar un entorno virtual e instalar las dependencias:

```bash
python3 -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
```

## TODO

- [ ] Guardar información del escaneo ping en CSV para cada escaneo.
- [ ] Incluir el modo `--industrial-hardcore` para realizar solo el escaneo ICMP sin escaneo de servicios.
- [x] Cambiar la detección de subredes en `scan2neo.py` para obtener los /24 de cada IP detectada.
- [ ] Optimizar el grafo de activos pivote eliminando el nodo origen y generando relaciones directas entre segmentos.
- [x] Contabilizar el número total de activos inseguros (con protocolos inseguros).
- [ ] Implementar filtro por IP en el grafo de activos similares en base a capturas de pantalla.
- [ ] Mostrar la cantidad de subredes /24 encontradas.
- [~] Incluir un departamento nuevo para el control de cambios entre escaneos con fechas diferentes.
- [~] Implementar escala logarítmica en el gráfico comparativo entre organizaciones.
- [x] Actualizar el README.

---

¡Gracias por usar ScanHound! 🚀
