# Parcial #3 - informática I
# Isabella Arrieta Pacheco 
# Gabriela Guevara Murcia

import json
import os
import csv
import xml.etree.ElementTree as ET
from xml.dom import minidom

# Rutas de carpetas
CARPETA_INGRESOS = "IngresosURG"
CARPETA_NUEVO_FORMATO = "NuevoFormato"
ARCHIVO_CSV = os.path.join(CARPETA_NUEVO_FORMATO, "PacientesURG.csv")

def crear_carpeta_nuevo_formato():
    #Si no existe la carpeta NuevoFormato, la creamos
    if not os.path.exists(CARPETA_NUEVO_FORMATO):
        os.makedirs(CARPETA_NUEVO_FORMATO)
        print(f"Carpeta '{CARPETA_NUEVO_FORMATO}' creada exitosamente.")

def leer_archivo_json(ruta_archivo):
    #Leemos un archivo JSON y extraemos la info del paciente
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            datos = json.load(archivo)
            if datos and len(datos) > 0:
                paciente = datos[0]
                return {
                    'id': paciente.get('Cedula', ''),
                    'Nombre': paciente.get('Nombre', '').strip(),
                    'Apellido': paciente.get('Apellido', '').strip(),
                    'Cedula': paciente.get('Cedula', ''),
                    'Edad': paciente.get('Edad', ''),
                    'Sexo': paciente.get('Sexo', ''),
                    'Talla': paciente.get('Talla', ''),
                    'Peso': paciente.get('Peso', ''),
                    'Turno': paciente.get('Triaje', {}).get('Turno', ''),
                    'Valoracion': paciente.get('Triaje', {}).get('valoracion', ''),
                    'Presion_Diastolica': paciente.get('Presion', {}).get('Diastolica', ''),
                    'Presion_Sistolica': paciente.get('Presion', {}).get('Sistolica', ''),
                    'Frec_Cardiaca': paciente.get('Frec Cardiaca', ''),
                    'Estado': 'Activo'
                }
    except Exception as e:
        print(f"Error al leer {ruta_archivo}: {e}")
    return None

def leer_archivo_dicom(ruta_archivo):
    #Leemos un archivo DICOM y extraemos la info del paciente
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
            lineas = archivo.readlines()
            
            paciente = {
                'id': '',
                'Nombre': '',
                'Apellido': '',
                'Cedula': '',
                'Edad': '',
                'Sexo': '',
                'Talla': '',
                'Peso': '',
                'Turno': '',
                'Valoracion': '',
                'Presion_Diastolica': '',
                'Presion_Sistolica': '',
                'Frec_Cardiaca': '',
                'Estado': 'Activo'
            }
            
            # Buscamos la línea PAD que contiene info del paciente
            for linea in lineas:
                if linea.startswith('PAD'):
                    partes = linea.split('¬')
                    if len(partes) >= 8:
                        # Formato: PAD¬1¬¬^^^CEXTERNA¬¬APELLIDO^NOMBRE^¬¬CEDULA¬SEXO¬EDAD
                        nombre_completo = partes[7] if len(partes) > 7 else ''
                        if '^' in nombre_completo:
                            nombre_parts = nombre_completo.split('^')
                            paciente['Apellido'] = nombre_parts[0].strip() if len(nombre_parts) > 0 else ''
                            paciente['Nombre'] = nombre_parts[1].strip() if len(nombre_parts) > 1 else ''
                        paciente['Cedula'] = partes[8].strip() if len(partes) > 8 else ''
                        paciente['Sexo'] = 'Masculino' if partes[9].strip() == 'M' else 'Femenino' if len(partes) > 9 else ''
                        paciente['Edad'] = partes[10].strip() if len(partes) > 10 else ''
                        paciente['id'] = paciente['Cedula']
                
                # Buscamos líneas TRI para obtener los datos médicos
                if linea.startswith('TRI'):
                    partes = linea.split('¬')
                    if len(partes) >= 5:
                        tipo = partes[4] if len(partes) > 4 else ''
                        valor = partes[6] if len(partes) > 6 else ''
                        
                        if 'HR^Heart rate' in tipo:
                            # Extraemos la frecuencia cardíaca del formato CD:XX
                            if 'CD:' in valor:
                                paciente['Frec_Cardiaca'] = valor.split('CD:')[1].split('^')[0].strip()
                        elif 'SP^Systolic pressure' in tipo:
                            if 'CD:' in valor:
                                paciente['Presion_Sistolica'] = valor.split('CD:')[1].split('^')[0].strip()
                        elif 'DP^Diastolic pressure' in tipo:
                            if 'CD:' in valor:
                                paciente['Presion_Diastolica'] = valor.split('CD:')[1].split('^')[0].strip()
                        elif 'W^Weight' in tipo:
                            if 'CD:' in valor:
                                peso = valor.split('CD:')[1].split('^')[0].strip()
                                paciente['Peso'] = peso.replace('kg', '').strip()
                        elif 'H^Height' in tipo and 'Valoration' not in tipo:
                            if 'CD:' in valor:
                                talla = valor.split('CD:')[1].split('^')[0].strip()
                                paciente['Talla'] = talla.replace('m', '').strip()
                        elif 'H^Valoration' in tipo:
                            paciente['Valoracion'] = partes[5].strip() if len(partes) > 5 else ''
            
            return paciente if paciente['Cedula'] else None
    except Exception as e:
        print(f"Error al leer {ruta_archivo}: {e}")
    return None

def exportar_a_csv():
    #Exportamos todos los archivos de IngresosURG a un único archivo CSV
    crear_carpeta_nuevo_formato()
    
    pacientes = []
    
    # Leemos todos los archivos de la carpeta IngresosURG
    if os.path.exists(CARPETA_INGRESOS):
        archivos = os.listdir(CARPETA_INGRESOS)
        
        for archivo in archivos:
            ruta_completa = os.path.join(CARPETA_INGRESOS, archivo)
            
            if archivo.endswith('.json'):
                paciente = leer_archivo_json(ruta_completa)
                if paciente:
                    pacientes.append(paciente)
            elif archivo.endswith('.txt'):
                paciente = leer_archivo_dicom(ruta_completa)
                if paciente:
                    pacientes.append(paciente)
    
    # Escribimos al CSV
    if pacientes:
        campos = ['id', 'Nombre', 'Apellido', 'Cedula', 'Edad', 'Sexo', 'Talla', 'Peso', 
                 'Turno', 'Valoracion', 'Presion_Diastolica', 'Presion_Sistolica', 
                 'Frec_Cardiaca', 'Estado']
        
        with open(ARCHIVO_CSV, 'w', newline='', encoding='utf-8') as archivo_csv:
            escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
            escritor.writeheader()
            escritor.writerows(pacientes)
        
        print(f"\n✓ Se exportaron {len(pacientes)} pacientes al archivo CSV.")
        print(f"✓ Archivo guardado en: {ARCHIVO_CSV}\n")
    else:
        print("\n No se encontraron pacientes para exportar.\n")

def buscar_paciente():
    #Buscamos un paciente en el CSV por cédula, nombre o apellido
    if not os.path.exists(ARCHIVO_CSV):
        print("\n El archivo CSV no existe. Primero debe exportar los datos.\n")
        return
    
    termino_busqueda = input("\nIngrese la cédula, nombre o apellido del paciente: ").strip()
    
    if not termino_busqueda:
        print("\n Debe ingresar un término de búsqueda.\n")
        return
    
    encontrados = []
    
    try:
        with open(ARCHIVO_CSV, 'r', encoding='utf-8') as archivo_csv:
            lector = csv.DictReader(archivo_csv)
            for fila in lector:
                cedula = fila.get('Cedula', '').lower()
                nombre = fila.get('Nombre', '').lower()
                apellido = fila.get('Apellido', '').lower()
                termino = termino_busqueda.lower()
                
                if termino in cedula or termino in nombre or termino in apellido:
                    encontrados.append(fila)
    except Exception as e:
        print(f"\n Error al leer el archivo CSV: {e}\n")
        return
    
    if encontrados:
        print("\n" + "="*60)
        print("PACIENTES ENCONTRADOS:")
        print("="*60)
        for paciente in encontrados:
            print(f"ID: {paciente.get('id', 'N/A')}")
            print(f"Nombre: {paciente.get('Nombre', 'N/A')}")
            print(f"Apellido: {paciente.get('Apellido', 'N/A')}")
            print(f"Estado: {paciente.get('Estado', 'N/A')}")
            print("-"*60)
    else:
        print(f"\n No se encontraron pacientes con el término '{termino_busqueda}'.\n")

def crear_xml_paciente(paciente):
    """Crea un archivo XML para un paciente"""
    raiz = ET.Element("Paciente")
    
    ET.SubElement(raiz, "id").text = paciente['id']
    ET.SubElement(raiz, "Nombre").text = paciente['Nombre']
    ET.SubElement(raiz, "Apellido").text = paciente['Apellido']
    ET.SubElement(raiz, "Cedula").text = paciente['Cedula']
    ET.SubElement(raiz, "Edad").text = paciente['Edad']
    ET.SubElement(raiz, "Sexo").text = paciente['Sexo']
    ET.SubElement(raiz, "Talla").text = paciente['Talla']
    ET.SubElement(raiz, "Peso").text = paciente['Peso']
    ET.SubElement(raiz, "Turno").text = paciente['Turno']
    ET.SubElement(raiz, "Valoracion").text = paciente['Valoracion']
    ET.SubElement(raiz, "Presion_Diastolica").text = paciente['Presion_Diastolica']
    ET.SubElement(raiz, "Presion_Sistolica").text = paciente['Presion_Sistolica']
    ET.SubElement(raiz, "Frec_Cardiaca").text = paciente['Frec_Cardiaca']
    ET.SubElement(raiz, "Estado").text = paciente['Estado']
    
    # Formatear XML de forma legible
    xml_string = ET.tostring(raiz, encoding='utf-8')
    dom = minidom.parseString(xml_string)
    xml_formateado = dom.toprettyxml(indent="  ")
    
    # Nombre del archivo: cedulaApellidos.xml
    nombre_archivo = f"{paciente['Cedula']}{paciente['Apellido'].replace(' ', '')}.xml"
    ruta_xml = os.path.join(CARPETA_NUEVO_FORMATO, nombre_archivo)
    
    with open(ruta_xml, 'w', encoding='utf-8') as archivo:
        archivo.write(xml_formateado)
    
    return ruta_xml

def agregar_paciente_a_csv(paciente):
    """Agrega un nuevo paciente al archivo CSV"""
    campos = ['id', 'Nombre', 'Apellido', 'Cedula', 'Edad', 'Sexo', 'Talla', 'Peso', 
             'Turno', 'Valoracion', 'Presion_Diastolica', 'Presion_Sistolica', 
             'Frec_Cardiaca', 'Estado']
    
    # Verificar si el archivo existe
    archivo_existe = os.path.exists(ARCHIVO_CSV)
    
    with open(ARCHIVO_CSV, 'a', newline='', encoding='utf-8') as archivo_csv:
        escritor = csv.DictWriter(archivo_csv, fieldnames=campos)
        if not archivo_existe:
            escritor.writeheader()
        escritor.writerow(paciente)

def ingreso_manual():
    """Permite ingresar un paciente manualmente"""
    print("\n" + "="*60)
    print("INGRESO MANUAL DE PACIENTE")
    print("="*60)
    
    paciente = {
        'Nombre': input("Nombre: ").strip(),
        'Apellido': input("Apellido: ").strip(),
        'Cedula': input("Cédula: ").strip(),
        'Edad': input("Edad: ").strip(),
        'Sexo': input("Sexo (Masculino/Femenino): ").strip(),
        'Talla': input("Talla (m): ").strip(),
        'Peso': input("Peso (kg): ").strip(),
        'Turno': input("Turno (Diurno/Noche): ").strip(),
        'Valoracion': input("Valoración (1/2/3): ").strip(),
        'Presion_Diastolica': input("Presión Diastólica: ").strip(),
        'Presion_Sistolica': input("Presión Sistólica: ").strip(),
        'Frec_Cardiaca': input("Frecuencia Cardíaca: ").strip(),
        'Estado': 'Activo'
    }
    
    paciente['id'] = paciente['Cedula']
    
    # Crear carpeta si no existe
    crear_carpeta_nuevo_formato()
    
    # Crear archivo XML
    ruta_xml = crear_xml_paciente(paciente)
    print(f"\n✓ Archivo XML creado: {ruta_xml}")
    
    # Agregar al CSV
    agregar_paciente_a_csv(paciente)
    print(f"✓ Paciente agregado al archivo CSV: {ARCHIVO_CSV}\n")

def mostrar_menu():
    """Muestra el menú principal"""
    print("\n" + "="*60)
    print("MENÚ PRINCIPAL - SISTEMA DE PACIENTES URG")
    print("="*60)
    print("1. Exportar información a CSV")
    print("2. Buscar paciente")
    print("3. Ingreso manual de paciente")
    print("4. Salir")
    print("="*60)

def main():
    """Función principal del programa"""
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()
        
        if opcion == '1':
            exportar_a_csv()
        elif opcion == '2':
            buscar_paciente()
        elif opcion == '3':
            ingreso_manual()
        elif opcion == '4':
            print("\n✓ ¡Hasta luego!\n")
            break
        else:
            print("\n Opción no válida. Por favor, seleccione una opción del 1 al 4.\n")

if __name__ == "__main__":
    main()

