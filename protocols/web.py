from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium import webdriver
import base64
import time
import os
import requests

def take_screenshot(host, port, folder_img_path):
    url = f"http://{host}:{port}"
    options = Options()
    options.add_argument("--headless")  # Ejecuta el navegador en modo sin interfaz gráfica
    
    try:
        # Configura el driver de Firefox y carga la página
        driver = webdriver.Firefox(options=options)
        driver.set_page_load_timeout(10)
        driver.get(url)
        WebDriverWait(driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
    except (TimeoutException, WebDriverException) as e:
        # Maneja errores de carga de página
        driver.quit()
        return None
    
    time.sleep(1)  # Espera 1 segundo antes de tomar la captura
    image_file = os.path.join(folder_img_path, f"{host}_{port}.png")
    
    if os.path.exists(image_file):
        # Verifica si el archivo de la captura ya existe
        driver.quit()
        return None
    
    try:
        # Toma la captura de pantalla y la guarda como archivo PNG
        driver.save_screenshot(image_file)
        screenshot_binary = driver.get_screenshot_as_png()
        return base64.b64encode(screenshot_binary).decode('utf-8')
    except Exception as e:
        # Maneja errores al guardar la captura
        return None
    finally:
        driver.quit()  # Cierra el navegador

def get_source(host, port, folder_src_path):
    url = f"http://{host}:{port}"
    try:
        # Realiza una solicitud HTTP para obtener el código fuente
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return None
        
        source_file = os.path.join(folder_src_path, f"{host}_{port}.txt")
        if os.path.exists(source_file):
            # Verifica si el archivo de código fuente ya existe
            return response.text
        
        with open(source_file, "w") as f:
            f.write(response.text)  # Guarda el código fuente en un archivo
        return response.text
    except requests.Timeout:
        # Maneja un error de timeout al intentar obtener el código fuente
        return None
    except requests.RequestException as e:
        # Maneja otros errores de conexión
        return None
