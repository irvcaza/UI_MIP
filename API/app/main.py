from typing import Optional, List
from fastapi import FastAPI, Query
import app.simulador_MIP as simulador_MIP
import numpy as np
import networkx as nx

app = FastAPI(
    title="Simulador MIP",
    description="Esta API realiza simulaciones numéricas y de redes de la matriz insumo-producto",
    version="0.1",
)


simulador = simulador_MIP.Simulador_MIP("/app/mip_d_pb_pxp__4_22_42_202_133.xlsx","/app/mip_t_pb_pxp__4_22_45_202_133.xlsx")


def deserializa_lista(lista_cambios):
    lista = [[int(x) for x in cambio.split(",")] for cambio in lista_cambios]
    return lista

@app.get("/simula/tablas")
async def simula_tablas(
        cambio:List[str] = Query(...,
            title="Cambio a la MIP",
            description="Vector de 3 valores separados por comas que indican id sector inicial, final y porcentaje de participación",
        ),
        limite:int = Query(0,
            title="Limite de resultados",
            description="límite de resultados ordenados por variación, seleccionar 0 u omitir valor para obtener todos (sin orden)"
        )
    ):
    lista = deserializa_lista(cambio)
    A, B, C, D, E = simulador.simular_tablas(lista)
    orient = "records"
    if limite:
        v_mdp = "Variación (millones de pesos)"
        v_p = "Variación (Puestos)"

        resultado = {
            "macro":A.to_dict(orient),
            "PIB":B.nlargest(limite,v_mdp).sort_values(v_mdp,0,False).to_dict(orient),
            "remuneraciones":C.nlargest(limite,v_mdp).sort_values(v_mdp,0,False).to_dict(orient),
            "puestos_rem":D.nlargest(limite,v_p).sort_values(v_p,0,False).to_dict(orient),
            "puestos_tot":E.nlargest(limite,v_p).sort_values(v_p,0,False).to_dict(orient)
        }
    else:
        resultado = {
            "macro":A.to_dict(orient),
            "PIB":B.to_dict(orient),
            "remuneraciones":C.to_dict(orient),
            "puestos_rem":D.to_dict(orient),
            "puestos_tot":E.to_dict(orient)
        }
    return resultado

@app.get("/simula/red/{inicial}")
def simula_red(inicial:int,
        filtro:int = Query(4,
            description= "Filtro para omitir valores (relativos) que sean menores a este filtro",
            title = "Filtro en porcentaje"
        ),
        cambio:List[str] = Query([],
            title="Cambio a la MIP",
            description="Vector de 3 valores separados por comas que indican id sector inicial, final y porcentaje de participación, omitir para obtener la red original",
        )):
    filtro = filtro/100
    lista = deserializa_lista(cambio)
    red = simulador.simula_red(inicial,filtro,lista)
    return nx.node_link_data(red)


@app.get("/datos/etiquetas")
def etiquetas():
    resultado = {i:x for i,x in enumerate(list(simulador.etiSCIAN))}
    return resultado


