# Migración de interfaz de usuario parara matiz insumo producto

En este repositorio se preserva información acerca de la migración de la herramienta de interfaz de usuario para 
simulaciones de la matriz insumo producto. Inicialmente desarrollado en cuaderno de Wolfram Mathematica se busca 
cambiar a un sistema de micro-servicios utilizando Python.

Primero se realizo una traducción línea a línea del lenguaje Mathematica a Python, validando la coincidencia de los 
objetos creados. Con esta traducción se creó una clase en python la cual maneja toda la funcionalidad básica.
Esta clase es usada junto con FastAPI para crear un API REST.

## Instrucciones

### Traducción
Pasos para crear un entorno de desarrollo que permita ejecución tanto de Wolfram language como de Python.
- [Docker](https://www.docker.com) instalado 
- Cuenta de [Wolfram](https://account.wolfram.com/login/oauth2/sign-in)
- Descargar archivo de [Wolfram Engine 12.2.0](https://www.wolfram.com/engine/) para linux y colocarlo en el mismo 
directorio del Dockerfile
  - En caso de que se tenga otra version de Wolfram Engine o Distinto nombre de archivo habrá que cambiar 
  el Dockerfile en la linea 21
- Construir la imagen con `docker build -t jupyter:we .`
- lanzar el contenedor con 
``` docker run -it -v $PWD/scripts:/home/jovyan/scripts -v $PWD/data:/home/jovyan/data --name jupyter_we -p 8888:8888 jupyter:we ```
- Buscar en el log del contenedor lanzado una dirección del tipo http://127.0.0.1:8888/?token=644ac7...
- Abrir en cualquier navegador tal dirección 
- En Jupyter abrir una nueva terminal y ejecutar `wolframscript`, dar credenciales de la cuenta Wolfram
- Abrir el cuaderno en scripts/TestInicial.ipynb para interactuar con un ejemplo de uso

**Nota:** Es muy importante NO destruir el contenedor creado (docker container rm jupyter_we) ya que si se hace es 
necesario volver a autenticarse a Wolfram y la cantidad de licencias es limitada. Para solventar esto se puede crear 
una imagen autenticada con
``` docker commit jupyter_we jupyter:we_licence ```

Con esto podemos lanzar imágenes de la siguiente manera 
```docker run -it -v $PWD/scripts:/home/jovyan/scripts -v $PWD/data:/home/jovyan/data -p 8888:8888 --name jupyter_we_lic jupyter:we_licence start.sh jupyter lab```
