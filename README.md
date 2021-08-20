# Repositorio de addons de homodaba para kodi (homodaba-kodi-repo)

Este proyecto sirve de repo de kodi para los addons para kodi de [homodaba](https://github.com/moz667/homodaba/) y para repo de las [fuentes de estos addons](src/).

## Directorios
 * [leia](leia/), versiones de addons para kodi/leia (18.X.X)
 * [matrix](matrix/), versiones de addons para kodi/matrix (19.X.X)
 * [src](src/), fuentes de los addons

## Construir el repositorio de addons para kodi
He creado un shell script [build.sh](build.sh) que genera los distintos zips y metadatos para las distintas versiones de kodi

## Instalacion del repo en kodi
OJO: Hay que activar la opcion de permitir addons de terceros para poder instalar estos addons.
 * Descargar el zip del repo para tu version de kodi:
    - [leia](https://raw.githubusercontent.com/moz667/homodaba-kodi-repo/main/leia/repository.homodaba-latest.zip)
    - [matrix](https://raw.githubusercontent.com/moz667/homodaba-kodi-repo/main/matrix/repository.homodaba-latest.zip)
 * [Instalar a traves de la gui de kodi](https://kodi.wiki/view/Add-on_manager#How_to_install_from_a_ZIP_file)

Una vez hecho esto ya podrias instalar los addons a traves de la gui de kodi

## Listado de addons:
 * [repository.homodaba](src/repository.homodaba), es el addon de repositorio de kodi para los addons de homodaba
 * [plugin.homodaba.movies](src/plugin.homodaba.movies), es una prueba para ver como funcionaba el tema de addons en kodi (spoiler: es muy doloroso ^_^), basicamente te saca una navegacion por tags y posteriormente las pelis.

## Como probar los addons:
La forma mas facil que he visto es basicamente (asumimos que lo vas a probar en un kodi en local):
1. Instalar el addon:
    1. Esto puedes hacerlo copiando el addon a pelo (la forma mas rapida y sencilla)
        ```bash
        rsync -va plugin.homodaba.movies/ ~/.kodi/addons/plugin.homodaba.movies/
        ```
    1. Creando un zip con el addon, aunque esto requiere mas pasos puede ser util en algunas situaciones (probando en un kodi que no tengas acceso o para instalar dependencias, ya que copiando los sources del addon, **kodi NO TE VA A INSTALAR SUS DEPENDENCIAS**)
        1. Creas el zip del addon:
            ```bash
            zip -r plugin.homodaba.movies.zip plugin.homodaba.movies/
            ```
        1. Lo copias al kodi donde lo vas a instalar
        1. Instalas utilizando la ui de kodi (la primera vez, te va a pedir que autorices la instalacion de addons de terceros)

1. Seguir el log:
    ```bash
    tail -f ~/.kodi/temp/kodi.log
    ```
1. Activar el addon a traves de la interfaz de kodi

1. Probar (Si encuentras algun problema, tratar de solucionarlo y volver a instalar el addon)

## Problemas conocidos

1. Es posible que te de error en la instalacion al extraer el zip o comprobar los metadatos del addon (si lo haces a traves de zip, copiando a pelo los fuentes a mi al menos no me ha pasado). Despues de volverme loco cambiando cosas y probando varios zip (ya que todo parecia que estaba correcto), la solucion fue reiniciar kodi... "[Have You Tried Turning It Off And On Again?](https://youtu.be/nn2FB1P_Mn8)". Si despues de reiniciar te sigue dando error es posible que se trate de un error de verdad

1. Que te funcione en un kodi y en otro no. Revisa los logs y ten en cuenta:
    - La version de los dos kodi.
    - Reiniciar los dos kodi y volver a probar en los dos (No vaya a ser que el error aparedca en el que parecia que funcionaba ^_^)
    - Si se trata de un error en un import, revisar que tenga la dependencia definida. 

        **OJO: para que te instale dependencias tienes que instalar desde repositorio o con zip. Alternativamente puedes buscar un plugin que tenga la misma dependencia e instalarlo antes... pero esto puede ser un poco locura**

## Compatibilidad entre leia y matrix:

* Por defecto el addon plugin.homodaba.movies, esta hecho para kodi matrix (python3), aunque en nuestros caso, resulto bastante trivial hacerlo funcionar en leia (python2):

    1. Tuvimos que hacer los import compatibles:

        ```python
        # Python3:
        try:
            from urllib.parse import urlencode, parse_qsl
        # Python2:
        except ImportError:
            from urllib import urlencode
            from urlparse import parse_qsl
        ```

    1. Actualmente solo cambiando esta linea de addon.xml, lo haremos compatible:

        **Matrix**
        ```xml
        <import addon="xbmc.python" version="3.0.0" />
        ```
        **Leia**
        ```xml
        <import addon="xbmc.python" version="2.25.0" />
        ```

* Para poder importar archivos desde addon.py, tendremos que poner __init__.py en cada carpera hasta donde se encuentre el archivo a importar. Por ejemplo, si queremos tener una carpeta libs, dentro de resources, tendremos que crear:
    ```
    resources/__init__.py
    resources/lib/__init__.py
    ```

    Presumiblemente esto debe ocurrir en python2, aunque no he mirado el motivo.
