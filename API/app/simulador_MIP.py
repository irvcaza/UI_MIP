import numpy as np
import pandas as pd
import networkx as nx

class Simulador_MIP():
    def __init__(self, archivo_domestico, archivo_total):
        self.carga_datos(archivo_domestico, archivo_total)
        self.define_varibles_calculadas()
        self.vectores_coeficientes()
        self.matrices_coeficientes_tecnicos()
        self.variables_macroeconomicas()
        self.crea_red()
        
    def carga_datos(self,archivo_domestico, archivo_total):
        # ToDo: Hacer cambios para hacer la improtacion mas rapida 
        datosD = pd.read_excel(archivo_domestico,skiprows=5,index_col=0)
        datosT = pd.read_excel(archivo_total,skiprows=5,index_col=0)
        
        flujos_intermedios = ["111110 - Cultivo de soya","931810 - Actividades de seguridad nacional"]
        self.Zd = self.obtenerSubmatriz(flujos_intermedios,flujos_intermedios,datosD)
        self.Zt = self.obtenerSubmatriz(flujos_intermedios,flujos_intermedios,datosT)
        
        demanda_final = ["CP - Consumo Privado","YA0 - Discrepancia estadística"]
        self.Fd = self.obtenerSubmatriz(flujos_intermedios,demanda_final,datosD)
        Ft = self.obtenerSubmatriz(flujos_intermedios,demanda_final,datosT)
        self.Ft = np.delete(Ft,-2,1)
        
        self.etiSCIAN = datosD.loc[flujos_intermedios[0]:flujos_intermedios[1]].index
        eti = self.etiSCIAN.str.slice(9)
        reemp_dic = {
           "Fabricación de" : "Fab.",
           "Cultivo de" : "C.",
           "Explotación de" : "Exp.",
           "Producción" : "Prod.",
           "producción" : "prod.",
           "Minería de" : "Min.",
           "Elaboración de" : "Elab.",
           "Transporte de" : "Trans.",
           "Transporte" : "Trans.",
           "Alquiler" : "Alq.",
           "Servicios de" : "S.",
           "Servicios" : "S."
           }
        eti2 = list(self.etiSCIAN)
        for key,val in reemp_dic.items():
            eti2 = list(map(lambda s: s.replace(key, val), eti2))
        self.eti2 = eti2
        
        self.REM = self.obtenerSubmatriz(["D.1 - Remuneración de los asalariados"]*2,flujos_intermedios,datosD)
        self.PT = self.obtenerSubmatriz(["PT - Puestos de trabajo"]*2,flujos_intermedios,datosD)
        self.PTR = self.obtenerSubmatriz(["PTR - Puestos de trabajo remunerados"]*2,flujos_intermedios,datosD)
        self.PIB = self.obtenerSubmatriz(["B.1bP - Producto interno bruto"]*2,flujos_intermedios,datosD)
        
        
    def obtenerSubmatriz(self,renglones,columnas,datos):
        datos2 = datos.fillna(0)
        datos_interes = datos2.loc[renglones[0]:renglones[1],columnas[0]:columnas[1]]
        matriz = np.array(datos_interes) 
        return matriz
    
    
    def invD(self, vector):
        if vector.ndim > 1 : 
            vector = vector.flatten()
        invertida = np.where(vector==0,0,1/vector)
        diagonal = np.diag(invertida)
        return diagonal
    
    
    def define_varibles_calculadas(self):
        self.n = len(self.Zd)
        self.fd = np.sum(self.Fd,1)
        ft = np.sum(self.Ft,1)
        self.x = np.sum(self.Zd,1) + self.fd
        self.M = self.Zt - self.Zd
        Fm = self.Ft - self.Fd
        Iota = np.ones([1,self.n])
    
    
    def vectores_coeficientes(self):
        invD_x = self.invD(self.x)
        self.rem = np.matmul(self.REM,invD_x)
        self.pt = np.matmul(self.PT,invD_x)
        self.ptr = np.matmul(self.PTR,invD_x)
        self.pib = np.matmul(self.PIB,invD_x)
        imp = np.matmul(np.sum(self.M,0),invD_x)
    
    def matrices_coeficientes_tecnicos(self):
        #A = Zd . invD[x];(*Matriz de coeficientes técnicos domésticos*)
        self.A = np.matmul(self.Zd,self.invD(self.x))
        #Am = M . invD[x];(*Matriz de coeficientes técnicos de importaciones*)
        self.Am = np.matmul(self.M,self.invD(self.x))
        #At = A + Am;(*Matriz de coeficientes técnicos totales*)
        self.At = self.A + self.Am
        #L = Inverse[IdentityMatrix[n] - A];(*Matriz inversa de Leontief*)
        L = np.linalg.inv( np.identity(self.n) - self.A)
        
    def variables_macroeconomicas(self):
        #xtot = Total[x];(*Valor Bruto de la Producción total*)
        self.xtot = np.sum(self.x)
        #PIBtot = Total[PIB];(*PIB total*)
        self.PIBtot = np.sum(self.PIB)
        #REMtot = Total[REM];(*Remuneraciones totales*)
        self.REMtot = np.sum(self.REM)
        #PTtot = Total[PT];(*Puestos de trabajo totales*)
        self.PTtot = np.sum(self.PT)
        #PTRtot = Total[PTR];(*Puestos de trabajo remunerados totales*)
        self.PTRtot = np.sum(self.PTR)
        #IMPtot = Total[Total[M]];(*Importaciones totales*)
        self.IMPtot = np.sum(self.M)
        #macro0 = {xtot, PIBtot, REMtot, PTtot, PTRtot, IMPtot};(*Lista de variables macro originales*)
        self.macro0 = np.array([self.xtot, self.PIBtot, self.REMtot, self.PTtot, self.PTRtot, self.IMPtot])
    
    
    def simular_tablas(self,lista):
        etiMacro = ["Producción (millones de pesos)",    "PIB (millones de pesos)", "Remuneraciones (millones de pesos)",    "Puestos de Trabajo", "Puestos de Trabajo Remunerados",    "Importaciones (millones de pesos)"]
        
        #numSust = Length[lista];(*Número de insumos a integrar*)
        numSust = len(lista)
        
        Amod,AMmod = self.simula_adyacencia(lista)
        
        #Lmod = Inverse[ IdentityMatrix[n] -  Amod];(*Inversa de Leontief doméstica modificada*)
        Lmod = np.linalg.inv( np.identity(self.n) - Amod)
        #xmod = Lmod . fd;(*Vector de VBP modificado*)
        xmod = np.matmul(Lmod , self.fd)
        #PIBmod = pib . xmod;(*Total del PIB modificado*)
        PIBmod = np.matmul(self.pib,  xmod)[0]
        #PIBmodVec = pib*xmod;(*Vector del PIB por actividad modificado*)
        PIBmodVec = self.pib*xmod
        #REMmod = rem . xmod;(*Total de Remuneraciones modificadas*)
        REMmod = np.matmul(self.rem, xmod)[0]
        #REMmodVec = rem*xmod;(*Vector de Remuneraciones por actividad modificadas*)
        REMmodVec = self.rem*xmod
        #PTmod = pt . xmod;(*Total del PT modificados*)
        PTmod = np.matmul(self.pt , xmod)[0]
        #PTmodVec = pt*xmod;(*Vector de PT por actividad modificados*)
        PTmodVec = self.pt*xmod
        #PTRmod = ptr . xmod;(*Total del PTR modificados*)
        PTRmod = np.matmul(self.ptr , xmod)[0]
        #PTRmodVec = ptr*xmod;(*Vector del PTR por actividad modificados*)
        PTRmodVec = self.ptr*xmod
        #IMPmod = Total[AMmod] . xmod;(*Total del importaciones modificadas*)
        IMPmod = np.matmul( np.sum(AMmod,0), xmod)
        #(*-- Generación de tablas con resultados*)
        #(*Tabla de resultados macro*)
        resMacro = [np.sum(xmod) , PIBmod , REMmod , PTmod , PTRmod , IMPmod ] - self.macro0
        tablaMacro = pd.DataFrame({"Variable":etiMacro,
                                   "Niveles originales (millones de pesos)":self.macro0,
                                   "Variación (millones de pesos)":resMacro.flatten(),
                                   "Variación porcentual (%)":(resMacro/self.macro0*100).flatten()})
        #(*Tabla de principales sectores afectados vía PIB*)
        tablaPIB = pd.DataFrame({"Variable":self.etiSCIAN, 
                                 "Niveles originales (millones de pesos)":self.PIB.flatten(), 
                                 "Variación (millones de pesos)":(PIBmodVec - self.PIB).flatten(),
                                 "Variación porcentual (%)":((np.matmul(PIBmodVec , self.invD(self.PIB)) - 1)*100).flatten()})

        #(*Tabla de principales sectores afectados vía Remuneraciones*)
        tablaREM = pd.DataFrame({"Variable":self.etiSCIAN, 
                                 "Niveles originales (millones de pesos)":self.REM.flatten(), 
                                 "Variación (millones de pesos)":(REMmodVec - self.REM).flatten(), 
                                 "Variación porcentual (%)":((np.matmul(REMmodVec , self.invD(self.REM)) - 1)*100).flatten()})
        
        #(*Tabla de principales sectores afectados vía Puestos de Trabajo Remunerados*)
        tablaPTR = pd.DataFrame({"Variable":self.etiSCIAN, 
                                 "Niveles originales (Puestos)":self.PTR.flatten(), 
                                 "Variación (Puestos)":(PTRmodVec - self.PTR).flatten(), 
                                 "Variación porcentual (%)":((np.matmul(PTRmodVec , self.invD(self.PTR)) - 1)*100).flatten()})
        
        #(*Tabla de principales sectores afectados vía Puestos de Trabajo*)
        tablaPT = pd.DataFrame({"Variable":self.etiSCIAN, 
                                "Niveles originales (Puestos)":self.PT.flatten(), 
                                "Variación (Puestos)":(PTmodVec - self.PT).flatten(),  
                                "Variación porcentual (%)":((np.matmul(PTmodVec , self.invD(self.PT)) - 1)*100).flatten()})
        
        return [tablaMacro, tablaPIB, tablaREM, tablaPTR, tablaPT]
    
    def simula_adyacencia(self,lista):
        #Amod = ReplacePart[A, listaSustA];(*Matriz de coeficientes técnicos modificada*)
        #AMmod = ReplacePart[Am, listaSustAm];(*Matriz de coeficientes importados modificada*)
        Amod = self.A.copy()
        AMmod = self.Am.copy()
        for elem in lista:
            Amod[elem[0],elem[1]] += (elem[2]/100)*self.Am[elem[0],elem[1]]
            AMmod[elem[0],elem[1]] = (1 - elem[2]/100)* self.Am[elem[0],elem[1]]
            
        return [Amod,AMmod]
    
    def crea_red(self):
        DG = nx.DiGraph()
        DG.add_edges_from([(i,j,{"domestico":self.A[i,j],"total":destino,"importaciones":self.Am[i,j]}) 
                            for i, origen in enumerate(self.At) 
                            for j, destino in enumerate(origen) 
                            if destino > 0 and i != j and not i in [446, 447]])
        for n in DG.nodes:
            DG.nodes[n]["etiqueta"] = self.etiSCIAN[n]

        self.red = DG
        
    def cerradura(self, elementos,funcion_pseudoclausura, red, **arg):
        sub_red = nx.DiGraph()
        nodos_elementos = [(x,red.nodes[x]) for x in elementos]
        sub_red.add_nodes_from(nodos_elementos)
        clausura = funcion_pseudoclausura(sub_red,red,**arg)
        while sub_red.nodes != clausura.nodes and sub_red.edges != clausura.edges:
            sub_red = clausura
            clausura = funcion_pseudoclausura(sub_red,red,**arg)
        return sub_red


    def presouclausura_atras(self,elementos,red,nivel,filtro):
        presouclausura = elementos.copy()
        for x in elementos.nodes:
            for y in red.nodes :
                if red.has_edge(y,x) and red.edges[y,x][nivel]>filtro:
                    if not presouclausura.has_node(y):
                        presouclausura.add_node(y,**red.nodes[y])
                    if not presouclausura.has_edge(y,x):
                        presouclausura.add_edge(y,x,**red.edges[y,x])
        return presouclausura

    def modifica_red(self,lista):
        redMod = self.red.copy()
        for elem in lista:
            #Amod[elem[0],elem[1]] += (elem[2]/100)*self.Am[elem[0],elem[1]]
            redMod.edges[elem[0],elem[1]]["domestico"] += (elem[2]/100)*redMod.edges[elem[0],elem[1]]["importaciones"]
            redMod.edges[elem[0],elem[1]]["importaciones"] = redMod.edges[elem[0],elem[1]]["total"] - redMod.edges[elem[0],elem[1]]["domestico"]
            
        return redMod
    
    def simula_red(self, sector_inicial, filtro=0.04, lista=[[]]):
        red_domestica = self.cerradura([sector_inicial],self.presouclausura_atras,self.red,nivel="domestico",filtro=filtro)
        red_total = self.cerradura([sector_inicial],self.presouclausura_atras,self.red,nivel="total",filtro=filtro)
        inicios = [x[0] for x in lista]
        red_simulada = self.cerradura(inicios,self.presouclausura_atras,self.modifica_red(lista),nivel="domestico",filtro=filtro)
        
        for e in red_total.edges:
            if red_domestica.has_edge(*e):
                tipo = "domestico"
            elif any([l[0] == e[0] and l[1] == e[1] for l in lista]):
                tipo = "simulado_directo"
            elif red_simulada.has_edge(*e):
                tipo = "simulado_indirecto"
            else:
                tipo = "total"
            red_total.edges[e]["tipo"] = tipo
            
        for n in red_total.nodes:
            if n == sector_inicial:
                tipo = "inicial"
            elif red_domestica.has_node(n):
                tipo = "domestico"
            else:
                tipo = "total"
            red_total.nodes[n]["tipo"] = tipo
                
            
        return red_total