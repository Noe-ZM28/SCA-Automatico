<h2>Menú</h2>

- [Instalación](#instalación)
  - [1. Instalación de Librerías del Sistema](#1-instalación-de-librerías-del-sistema)
  - [2. Instalación y Configuración de MariaDB](#2-instalación-y-configuración-de-mariadb)
  - [3. Creación de Usuario y Base de Datos](#3-creación-de-usuario-y-base-de-datos)
  - [4. Carga de Estructura Base de la Base de Datos](#4-carga-de-estructura-base-de-la-base-de-datos)

<h2 id="instalación">Instalación</h2>

<h3 id="1-instalación-de-librerías-del-sistema">1. Instalación de Librerías del Sistema</h3>

<p>Para instalar las librerías del sistema necesarias, ejecuta el siguiente comando:</p>

<pre><code>pip3 install -r requirements.txt</code></pre>

<p>Si surge algún error durante la instalación, instala manualmente cada librería según las especificaciones del archivo <code>requirements.txt</code> segun la versión indicada con el comando: </p>

<pre><code>pip3 install nombre_libreria==version</code></pre>

<h3 id="2-instalación-y-configuración-de-mariadb">2. Instalación y Configuración de MariaDB</h3>

<p>Asegúrate de tener MariaDB instalado en tu sistema ejecutando el siguiente comando:</p>

<pre><code>sudo apt install mariadb-server</code></pre>

<p>Después, ejecuta el siguiente comando para realizar la configuración inicial siguiendo las instrucciones del asistente de instalación:</p>

<pre><code>sudo mysql_secure_installation</code></pre>

<h3 id="3-creación-de-usuario-y-base-de-datos">3. Creación de Usuario y Base de Datos</h3>

<p>Para crear un usuario para la base de datos y la base de datos "Parqueadero1", sigue estos pasos:</p>

<pre><code>
-- Conéctate a MariaDB
sudo mysql -uUsuario -pContraseña

-- Crea un usuario (reemplaza 'nombre_usuario' y 'contraseña' con tu elección)
CREATE USER 'nombre_usuario'@'localhost' IDENTIFIED BY 'contraseña';

-- Crea la base de datos "Parqueadero1"
CREATE DATABASE Parqueadero1;

-- Otorga permisos al usuario sobre la base de datos
GRANT ALL PRIVILEGES ON Parqueadero1.* TO 'nombre_usuario'@'localhost';

-- Actualiza los privilegios
FLUSH PRIVILEGES;

-- Sal de MariaDB
exit;
</code></pre>

<p>Recuerda cambiar 'nombre_usuario' y 'contraseña' según tus preferencias de seguridad y configurar las credenciales correctamente para el funcionamiento del sistema.</p>

<h3 id="4-carga-de-estructura-base-de-la-base-de-datos">4. Carga de Estructura Base de la Base de Datos</h3>

<p>Para cargar la estructura base de la base de datos <code>DB\db_base.sql</code>, utiliza el siguiente comando:</p>

<pre><code>sudo mysql -unombre_usuario -pParqueadero1 &lt; DB/db_base.sql</code></pre>

<p>Reemplaza 'nombre_usuario' con el nombre de usuario que creaste durante la configuración de la base de datos, así como la contraseña. Se te pedirá ingresar la contraseña del usuario.</p>
