## Usar pip install en una imagen de docker
# https://jupyter-docker-stacks.readthedocs.io/en/latest/using/recipes.html#using-pip-install-or-conda-install-in-a-child-docker-image

# Para elegir la imagen correcta consultar https://jupyter-docker-stacks.readthedocs.io/en/latest/using/selecting.html
#  Utilizar solo imagen base con texlive, git y vi
#FROM jupyter/minimal-notebook:5cb007f03275
# Utilizar solo imagen minimal-notebook con scipy: paquetes del ecosistema cientifico de python
FROM jupyter/scipy-notebook:703d8b2dcb88
# Utilizar solo imagen scipy-notebook mas tensorflow y keras
#FROM jupyter/tensorflow-notebook:5cb007f03275
# Utilizar imagen base con interprete de R y librerias populares: tidyverse, devtools, shiny, rmarkdown, forecast, rsqlite...
#FROM jupyter/jupyter/r-notebook:5cb007f03275 
# Utilizar todos los paquetes de scipy-notebook y r-notebook asi tambien como interprete de julia
#FROM jupyter/datascience-notebook:5cb007f03275" 
# utilizar todos los paquetes de scipy-notebook y soporte para Apache Spark
#FROM jupyter/pyspark-notebook:5cb007f03275" 

COPY --chown=${NB_UID}:${NB_GID} WolframEngine_12.2.0_LIN.sh /tmp/

USER root
RUN cd /tmp && /bin/bash WolframEngine_12.2.0_LIN.sh
USER jovyan

# Copia el archivo de requerimientos al contenedor 
COPY --chown=${NB_UID}:${NB_GID} requirements.txt /tmp/
# Instal los requerimientos en le archivo 
RUN pip install --requirement /tmp/requirements.txt && \
    fix-permissions $CONDA_DIR && \
    fix-permissions /home/$NB_USER
# elimina directorio creado que no es necesario
RUN rm -r ~/work