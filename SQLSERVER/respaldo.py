import subprocess
import os
import datetime
import sys

server = 'CHICHO'
username = 'sa'
password = '1234'
ruta_directorio = 'C:/Backups'  # Reemplaza con la ruta de tu directorio de respaldo

def obtener_bases_de_datos():
    try:
        # Comando para obtener la lista de bases de datos
        command = f'sqlcmd -S {server} -U {username} -P {password} -Q "SELECT name FROM sys.databases WHERE database_id > 4"'

        # Ejecutar el comando para obtener las bases de datos
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)

        # Obtener y retornar las bases de datos disponibles
        databases = result.stdout.strip().split('\n')
        return databases

    except subprocess.CalledProcessError as e:
        print(f"Error al obtener las bases de datos: {e}")
        sys.exit(1)

def realizar_respaldo():
    try:
        # Obtener la lista de bases de datos disponibles
        databases = obtener_bases_de_datos()

        # Mostrar las bases de datos disponibles
        print("Bases de datos disponibles:")
        for i, db in enumerate(databases, start=1):
            print(f"{i}. {db}")

        # Solicitar al usuario que seleccione la base de datos a respaldar
        seleccion = int(input("Selecciona el número de la base de datos que deseas respaldar: "))
        if 1 <= seleccion <= len(databases):
            # Respaldar la base de datos seleccionada
            realizar_respaldo_sql(databases[seleccion - 1])
        else:
            print("Selección no válida.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperación cancelada.")

def realizar_respaldo_sql(database):
    try:
        # Nombre del archivo de respaldo
        backup_filename = f'{database}_backup_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.bak'

        # Comando para realizar el respaldo
        backup_command = f'sqlcmd -S {server} -U {username} -P {password} -d {database} -Q "BACKUP DATABASE {database} TO DISK=\'{ruta_directorio}/{backup_filename}\'"'

        # Ejecutar el comando de respaldo desde la línea de comandos
        subprocess.run(backup_command, shell=True, check=True)

        # Definir la ruta completa del archivo de respaldo
        ruta_archivo = os.path.join(ruta_directorio, backup_filename)

        print(f"Respaldo de la base de datos '{database}' completado. El archivo de respaldo se guardó en: {ruta_archivo}")

    except subprocess.CalledProcessError as e:
        print(f"Error al realizar el respaldo: {e}")
        sys.exit(1)

def realizar_restauracion():
    try:
        # Obtener la lista de archivos de respaldo en el directorio
        archivos_respaldo = [archivo for archivo in os.listdir(ruta_directorio) if archivo.endswith('.bak')]

        # Mostrar los archivos de respaldo disponibles
        print("Archivos de respaldo disponibles:")
        for i, archivo in enumerate(archivos_respaldo, start=1):
            print(f"{i}. {archivo}")

        # Solicitar al usuario que seleccione el archivo de respaldo a restaurar
        seleccion = int(input("Selecciona el número del archivo de respaldo que deseas restaurar: "))
        if 1 <= seleccion <= len(archivos_respaldo):
            # Restaurar la base de datos seleccionada
            realizar_restauracion_sql(archivos_respaldo[seleccion - 1])
        else:
            print("Selección no válida.")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\nOperación cancelada.")

def realizar_restauracion_sql(archivo_respaldo):
    try:
        # Solicitar al usuario el nombre de la base de datos a restaurar
        database = input("Ingrese el nombre de la base de datos a restaurar: ")

        # Comando para restaurar la base de datos
        restore_command = f'sqlcmd -S {server} -U {username} -P {password} -Q "RESTORE DATABASE [{database}] FROM DISK=\'{ruta_directorio}/{archivo_respaldo}\' WITH REPLACE;"'

        # Ejecutar el comando de restauración desde la línea de comandos
        subprocess.run(restore_command, shell=True, check=True)

        print(f"Restauración de la base de datos '{database}' completada.")

    except subprocess.CalledProcessError as e:
        print(f"Error al realizar la restauración: {e}")
        sys.exit(1)


# Ejemplo de uso para iniciar la operación de respaldo o restauración
operacion = input("Selecciona la operación a realizar (1 para respaldar, 2 para restaurar): ")
if operacion == '1':
    realizar_respaldo()
elif operacion == '2':
    realizar_restauracion()
else:
    print("Operación no válida.")
