from flask import Flask, render_template, request, redirect, url_for
import pyodbc
import os

# Obtener la ruta absoluta del directorio donde se encuentra este script
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Ruta donde se guardarán los archivos de respaldo
BACKUP_DIR = os.path.join(BASE_DIR, 'backup_files')

app = Flask(__name__)

# Función para conectar a la base de datos SQL Server
def connect_to_database():
    server = 'LAPTOP-DAQBQR90'
    username = 'sa'
    password = 'Lechexd0206'
    conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';UID='+username+';PWD='+password)
    return conn
# Función para obtener una lista de todas las bases de datos en el servidor
def get_database_list():
    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sys.databases WHERE database_id > 4")  # Excluir bases de datos del sistema
    databases = [row[0] for row in cursor.fetchall()]

    conn.close()
    return databases

# Página principal con botones para cada sección
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para la sección de crear usuario
@app.route('/crear_usuario', methods=['GET', 'POST'])
def crear_usuario():
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form['password']

        conn = connect_to_database()
        cursor = conn.cursor()

        # Código SQL para crear un nuevo usuario
        sql_create_user = f"CREATE LOGIN {new_username} WITH PASSWORD = '{new_password}'"

        try:
            cursor.execute(sql_create_user)
            conn.commit()
            message = {"Crear Usuario" : "Nuevo usuario creado con éxito."}
        except Exception as e:
            message = {f"Error al crear el usuario:  {str(e)}"}
        finally:
            conn.close()
            
        return render_template('result.html', messages=message)  # Devuelve una plantilla con el mensaje de resultado
    else:
        return render_template('crear_usuario.html')  # Devuelve la plantilla del formulario de creación de usuario

@app.route('/modificar_usuario', methods=['GET', 'POST'])
def modificar_usuario():
    if request.method == 'POST':
        current_username = request.form['username']
        new_username = request.form['new_username']
        new_password = request.form['new_password']

        conn = connect_to_database()
        cursor = conn.cursor()

        try:
            # Si se proporciona un nuevo nombre de usuario, cambiar el nombre de login
            if new_username:
                sql_rename_login = f"ALTER LOGIN [{current_username}] WITH NAME = [{new_username}]"
                cursor.execute(sql_rename_login)
            
            # Si se proporciona una nueva contraseña, cambiar la contraseña
            if new_password:
                sql_change_password = f"ALTER LOGIN [{new_username or current_username}] WITH PASSWORD = '{new_password}'"
                cursor.execute(sql_change_password)

            conn.commit()
            message = {"Modificar Usuario": "Usuario modificado correctamente."}
        except Exception as e:
            message = {"Error al modificar el usuario": str(e)}
        finally:
            conn.close()

        return render_template('result.html', messages=message)
    else:
        return render_template('modificar_usuario.html')



# Ruta para la página de eliminación de usuario
@app.route('/eliminar_usuario', methods=['GET', 'POST'])
def eliminar_usuario():
    if request.method == 'POST':
        username = request.form['username']

        conn = connect_to_database()
        cursor = conn.cursor()

        # Código SQL para eliminar un usuario
        sql_delete_user = f"DROP LOGIN {username}"

        try:
            cursor.execute(sql_delete_user)
            conn.commit()
            message = {"Eliminar Usuario" : "Usuario eliminado correctamente"}
        except Exception as e:
            message = {f"Error al eliminar el usuario: {str(e)}"}
        finally:
            conn.close()

        return render_template('result.html', messages=message)
    else:
        return render_template('eliminar_usuario.html')
    
    # Ruta para la sección de crear rol
@app.route('/crear_rol', methods=['GET', 'POST'])
def crear_rol():
    if request.method == 'POST':
        new_role_name = request.form['rolename']

        conn = connect_to_database()
        cursor = conn.cursor()

        # Código SQL para crear un nuevo rol a nivel de servidor
        sql_create_role = f"CREATE SERVER ROLE [{new_role_name}]"

        try:
            cursor.execute(sql_create_role)
            conn.commit()
            message = {"Crear Rol" : "Rol creado correctamente"}
        except Exception as e:
            message = {"Error al crear el rol": str(e)}
        finally:
            conn.close()

        return render_template('result.html', messages=message)
    else:
        return render_template('crear_rol.html')

    
@app.route('/consultar_usuarios')
def consultar_usuarios():
    conn = connect_to_database()
    cursor = conn.cursor()

    # Consulta SQL para obtener los usuarios
    sql_query = "SELECT name FROM sys.server_principals WHERE type IN ('S', 'U', 'G')"

    try:
        cursor.execute(sql_query)
        users = [row[0] for row in cursor.fetchall()]  # Obtiene solo el primer valor de cada fila (nombre de usuario)
    except Exception as e:
        message = "Error al consultar usuarios: " + str(e)
        users = None
    finally:
        cursor.close()
        conn.close()

    return render_template('consultar_usuarios.html', users=users)

@app.route('/consultar_roles')
def consultar_roles():
    conn = connect_to_database()
    cursor = conn.cursor()

    # Consulta SQL para obtener los roles de servidor
    sql_query = "SELECT name FROM sys.server_principals WHERE type = 'R'"

    try:
        cursor.execute(sql_query)
        roles = [row[0] for row in cursor.fetchall()]  # Obtiene solo el primer valor de cada fila (nombre del rol)
    except Exception as e:
        message = "Error al consultar roles: " + str(e)
        roles = None
    finally:
        conn.close()

    return render_template('consultar_roles.html', roles=roles)


@app.route('/asignar_rol', methods=['GET', 'POST'])
def asignar_rol():
    if request.method == 'POST':
        username = request.form['username']
        rol = request.form['rol']

        conn = connect_to_database()
        cursor = conn.cursor()

        # Código SQL para asignar un rol de servidor a un usuario
        sql_asignar_rol = f"ALTER SERVER ROLE [{rol}] ADD MEMBER [{username}]"

        message = {}
        try:
            cursor.execute(sql_asignar_rol)
            conn.commit()
            message["Asignar Rol"] = "Rol asignado correctamente al usuario"
        except Exception as e:
            message["Error"] = f"Error al asignar el rol: {str(e)}"
        finally:
            cursor.close()
            conn.close()

        return render_template('result.html', messages=message)
    else:
        return render_template('asignar_rol.html')

@app.route('/respaldar_db', methods=['GET', 'POST'])
def respaldar_db():
    if request.method == 'POST':
        db_name = request.form['dbname']
        backup_folder = request.form['backup_folder']
        backup_path = os.path.join(backup_folder, f'{db_name}_backup.bak')

        conn = connect_to_database()
        cursor = conn.cursor()

        # Consulta SQL para realizar el respaldo de la base de datos
        sql_backup = f"BACKUP DATABASE [{db_name}] TO DISK = '{backup_path}'"

        try:
            cursor.execute(sql_backup)
            conn.commit()
            message = {"Respaldar Base de Datos": "Respaldo realizado con éxito."}
        except Exception as e:
            message = {"Error al respaldar la base de datos": str(e)}
        finally:
            conn.close()

        return render_template('result.html', messages=message)
    else:
        databases = get_database_list()
        return render_template('respaldar_db.html', databases=databases)

@app.route('/restaurar_db', methods=['GET', 'POST'])
def restaurar_db():
    if request.method == 'POST':
        db_name = request.form['dbname']
        backup_file = request.files['backup_file']
        backup_path = os.path.join(BACKUP_DIR, backup_file.filename)

        conn = connect_to_database()
        cursor = conn.cursor()

        sql_restore = f"RESTORE DATABASE [{db_name}] FROM DISK = '{backup_path}' WITH REPLACE"

        try:
            backup_file.save(backup_path)
            cursor.execute(sql_restore)
            conn.commit()
            message = {"Restaurar Base de Datos": "Restauración realizada con éxito."}
        except Exception as e:
            message = {"Error al restaurar la base de datos": str(e)}
        finally:
            conn.close()

        return render_template('result.html', messages=message)
    else:
        return render_template('restaurar_db.html')

if __name__ == '__main__':
    app.run(debug=True)
