<h2>Menú</h2>

- [Instalación](#instalación)
  - [1. Instalación de Librerías del Sistema](#1-instalación-de-librerías-del-sistema)
  - [2. Instalación y Configuración de MariaDB](#2-instalación-y-configuración-de-mariadb)
  - [3. Creación de Usuario y Base de Datos](#3-creación-de-usuario-y-base-de-datos)
  - [4. Carga de Estructura Base de la Base de Datos](#4-carga-de-estructura-base-de-la-base-de-datos)
- [Configuración del Entorno de Desarrollo](#5-configuracion-del-entorno-de-desarrollo)

<h2 id="instalación">Instalación</h2>

<h3 id="1-instalación-de-librerías-del-sistema">1. Instalación de Librerías del Sistema</h3>

<p>Antes de instalar las librerías del sistema, es recomendable crear un entorno virtual para evitar conflictos de dependencias. Si no tienes instalado virtualenv, puedes hacerlo ejecutando el siguiente comando:</p>

<pre><code>pip3 install virtualenv</code></pre>

<p>Después de instalar virtualenv, crea un entorno virtual con el siguiente comando:</p>

<pre><code>python3 -m venv .venv</code></pre>

<p>Activa el entorno virtual. La forma de hacerlo varía según tu sistema operativo:</p>

<ul>
  <li>En Linux:</li>
  <pre><code>source .venv/bin/activate</code></pre>

<li>En Windows:</li>
  <pre><code>.venv\Scripts\activate</code></pre>
</ul>

<p>Una vez que el entorno virtual esté activado, puedes proceder con la instalación de las librerías del sistema:</p>

<pre><code>pip install -r requirements.txt</code></pre>

<p>Si surge algún error durante la instalación, instala manualmente cada librería según las especificaciones del archivo <code>requirements.txt</code> según la versión indicada con el comando:</p>

<pre><code>pip install nombre_libreria==version</code></pre>

<h3 id="2-instalación-y-configuración-de-mariadb">2. Instalación y Configuración de MariaDB</h3>

<p>Asegúrate de tener MariaDB instalado en tu sistema ejecutando el siguiente comando:</p>

<pre><code>sudo apt install mariadb-server</code></pre>

<p>Después, ejecuta el siguiente comando para realizar la configuración inicial siguiendo las instrucciones del asistente de instalación:</p>

<pre><code>sudo mysql_secure_installation</code></pre>

<h3 id="3-creación-de-usuario-y-base-de-datos">3. Creación de Usuario y Base de Datos</h3>

<p>Para crear un usuario para la base de datos y la base de datos, sigue los siguientes pasos:</p>

<pre><code>
-- Conéctate a MariaDB con las credenciales de la instalación
sudo mysql -uUsuario -pContraseña

-- Crea un usuario (reemplaza 'nombre_usuario' y 'contraseña' con tu elección)
CREATE USER 'nombre_usuario'@'localhost' IDENTIFIED BY 'contraseña';

-- Crea la base de datos
CREATE DATABASE nombre_base_de_datos;

-- Otorga permisos al usuario sobre la base de datos
GRANT ALL PRIVILEGES ON nombre_base_de_datos.* TO 'nombre_usuario'@'localhost';

-- Actualiza los privilegios
FLUSH PRIVILEGES;

-- Sal de MariaDB
exit;
</code></pre>

<p>Recuerda cambiar 'nombre_usuario' y 'contraseña' según tus preferencias de seguridad y configurar las credenciales correctamente para el funcionamiento del sistema.</p>

<h3 id="4-carga-de-estructura-base-de-la-base-de-datos">4. Carga de Estructura Base de la Base de Datos</h3>

<p>Para cargar la estructura base de la base de datos <code>DB\db_base.sql</code>, utiliza el siguiente comando:</p>

<pre><code>sudo mysql -unombre_usuario -pcontrasea nombre_base_de_datos < ./DB/db_base.sql</code></pre>

<p>Reemplaza 'nombre_usuario' con el nombre de usuario que creaste durante la configuración de la base de datos, así como la contraseña. Se te pedirá ingresar la contraseña del usuario.</p>

<h3 id="5-configuracion-del-entorno-de-desarrollo">5. Configuración del Entorno de Desarrollo</h3>

<p>El punto de entrada del sistema es el archivo <code>main.py</code>. Se recomienda utilizar Visual Studio Code (VS Code) para trabajar en el proyecto.</p>

<p>Para aprovechar las capacidades de depuración, se proporciona una configuración predefinida en el archivo <code>.vscode/launch.json</code>. Asegúrate de tener la extensión "Python" instalada en VS Code y utiliza esta configuración para facilitar el proceso de desarrollo y depuración del sistema.</p>
