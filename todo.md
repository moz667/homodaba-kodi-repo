# Tareas pendientes

## plugin.homodaba.movies
 * [ ] Parece que para actualizar la lista de versiones de los addons hay que actualizar el addon de repo... (un poco raro esto...)
 * [X] ~~Completar datos de las pelis (ahora solo saca titulo y thumb)~~
 * [ ] Pensar que hacemos con archivos con varios audios y varios subs (molaria que por defecto cogiera el definido por config :P)
 * [ ] He intentado hacer el addon lo mas compatible posible con leia y matrix, actualmente solo tiene una linea en addon.xml que lo hace incompatible (en addon.xml): 
    - Para matrix esta puesto como...
        ```xml
        <import addon="xbmc.python" version="3.0.0" />
        ```
    - Para leia seria...
        ```xml
        <import addon="xbmc.python" version="2.25.0" />
        ```
    Estaria guay que se pudiera hacer compatible quitando la version (aunque no lo he probado y como es muy coñazo de probar lo he dejado asi)
