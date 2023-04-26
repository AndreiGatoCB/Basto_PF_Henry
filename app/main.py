from support_api import filter_area_perimetro, data_devices, select_data_by_date,setle_clean,df_gps,select_data_by_dates, agregar_ith
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse
from ml_suport import predict_model
from aguadas import agua_click,result_select,agua_clicks
import pandas as pd
import json
from transform_data import add_dormida_column,separador_por_dia, dataframe_interview_vaca,data_interview,diagnostico_devices
#Creo una instancia de FastAPI
app = FastAPI()

#---- redireccion al docs de fastapi--------

@app.get('/')
async def root():
    return RedirectResponse(url='/docs/')



#---------- Queries-----
# Primer consulta: Informacion propia de una finca.
@app.get("/informacion_por_finca/{nombre}")
async def informacion_por_finca(nombre: str):
    merge_data = data_interview(nombre)
    merge_data.point_ini= merge_data.point_ini.astype(str)
    merge_data.point_next= merge_data.point_next.astype(str)
    #return JSONResponse(content= json.dumps(merge_data.to_dict('records')))
    return JSONResponse(content= json.loads(merge_data.to_json()))


# Segunda consulta: Informacion propia de una finca en un periodo de tienpo.
@app.get("/informacion_por_un_periodo_por_finca/{nombre}/{fecha_init}/{fecha_fin}")
async def informacion_por_un_periodo_por_finca(nombre : str, fecha_init: str, fecha_fin : str):
    data_finca = setle_clean(nombre)
    df_gp = filter_area_perimetro(df_gps,data_finca['latitud_c'],data_finca['longitud_c'],data_finca['hectares'])
    df_gp = select_data_by_dates(df_gp,fecha_init,fecha_fin)
    df_gp = data_interview(nombre,df_gp)
    df_gp.point_ini= df_gp.point_ini.astype(str)
    df_gp.point_next= df_gp.point_next.astype(str)
    #return JSONResponse(content= json.dumps(df_gp.to_dict('records')))
    return JSONResponse(content= json.loads(df_gp.to_json()))



# Tercera consulta: Toda la informacion de una vaca de un establecimiento
@app.get("/filtro_por_una_vaca_establecimiento/{nombre}/{id}")
async def filtro_por_una_vaca_establecimiento(nombre : str, id : str):
    data_finca = data_interview(nombre)
    df_gps = data_finca[data_finca.UUID==id]
    df_gps.point_ini= df_gps.point_ini.astype(str)
    df_gps.point_next= df_gps.point_next.astype(str)
    #return JSONResponse(content= json.dumps( df_gps.to_dict('records')))
    return JSONResponse(content= json.loads(df_gps.to_json()))



# Cuarta consulta: Toda la informacion de una vaca, en un establecimiento en una fecha
@app.get("/informacion_por_un_dia_una_vaca_por_finca/{nombre}/{id}/{fecha}")
async def informacion_por_un_dia_una_vaca_por_finca(nombre : str, id : str, fecha: str):
    data_finca = setle_clean(nombre)
    df_gp = filter_area_perimetro(df_gps,data_finca['latitud_c'],data_finca['longitud_c'],data_finca['hectares'])
    df_gp = select_data_by_date(df_gp,fecha)
    df_gp = data_devices(df_gp,id)
    df_gp = dataframe_interview_vaca(df_gp)
    df_gp.point_ini= df_gp.point_ini.astype(str)
    df_gp.point_next= df_gp.point_next.astype(str)
    #return JSONResponse(content=  json.dumps(df_gp.to_dict('records')))
    return JSONResponse(content= json.loads(df_gp.to_json()))


# Quinta consulta: Toda la informacion de una vaca, en un establecimiento en un periodo de tiempo
@app.get("/informacion_por_un_periodo_una_vaca_por_finca/{nombre}/{id}/{fecha_init}/{fecha_fin}")
async def informacion_por_un_periodo_una_vaca_por_finca(nombre : str, id : str, fecha_init: str, fecha_fin : str):
    data_finca = setle_clean(nombre)
    df_gp = filter_area_perimetro(df_gps,data_finca['latitud_c'],data_finca['longitud_c'],data_finca['hectares'])
    df_gp= data_devices(df_gp,id)
    df_gp = select_data_by_dates(df_gp,fecha_init,fecha_fin)
    df_gp = dataframe_interview_vaca(df_gp)
    df_gp.point_ini= df_gp.point_ini.astype(str)
    df_gp.point_next= df_gp.point_next.astype(str)
    #return JSONResponse(content= json.dumps(df_gp.to_dict('records')))
    return JSONResponse(content= json.loads(df_gp.to_json()))

# Sexta consulta:
@app.get("/conducta_vaca/{nombre}/{id}/{fecha}")
async def conducta_vaca(nombre : str, id : str, fecha: str):
    data_finca = setle_clean(nombre)
    finca = filter_area_perimetro(df_gps,data_finca['latitud_c'],data_finca['longitud_c'],data_finca['hectares'])
    df_gp= data_devices(finca,id)
    df_gp = select_data_by_date(df_gp,fecha)
    df_gp = dataframe_interview_vaca(df_gp)
    df_gp = agregar_ith(df_gp,fecha,str(data_finca._id.values[0]))
    df_gp = predict_model(df_gp)
    d = agua_click(finca, id ,fecha ,str(data_finca._id.values[0]))
    df_gp =result_select(df_gp,d)
    df_gp = add_dormida_column(df_gp, 1, 20, 6)
    resumen=separador_por_dia(df_gp)
    resumen.index= resumen.index.astype(str)
    df_gp.point_ini= df_gp.point_ini.astype(str)
    df_gp.point_next= df_gp.point_next.astype(str)
    diagnostico = diagnostico_devices(resumen)
    df_gp=df_gp.drop(columns=['fecha'])
    datos={'datos':df_gp.to_dict('records'),'resumen_datos':resumen.to_dict('records'),'diagnostico':diagnostico.to_dict('records')}
    return JSONResponse(content= datos)
            

#Septima Consulta
@app.get("/conducta_vaca_periodo/{nombre}/{id}/{fecha_init}/{fecha_fin}")
async  def conducta_vaca_periodo(nombre : str, id : str, fecha_init: str, fecha_fin : str):
    data_finca = setle_clean(nombre)
    finca = filter_area_perimetro(df_gps,data_finca['latitud_c'],data_finca['longitud_c'],data_finca['hectares'])
    df_gp = data_devices(finca,id)
    df_gp = select_data_by_dates(df_gp,fecha_init,fecha_fin)
    df_gp = dataframe_interview_vaca(df_gp)
    df_gp = agregar_ith(df_gp,fecha_init,str(data_finca._id.values[0]),fecha_fin)
    df_gp = predict_model(df_gp)
    d = agua_clicks(finca,id,fecha_init,fecha_fin,str(data_finca._id.values[0]))
    df_gp = result_select(df_gp,d)
    df_gp = add_dormida_column(df_gp, 1, 20, 6)
    resumen = separador_por_dia(df_gp)
    resumen.index = resumen.index.astype(str)
    df_gp.point_ini= df_gp.point_ini.astype(str)
    df_gp.point_next= df_gp.point_next.astype(str)
    diagnostico = diagnostico_devices(resumen)
    df_gp = df_gp.drop(columns=['fecha'])
    datos={'datos':df_gp.to_dict('records'),'resumen_datos':resumen.to_dict('records'),'diagnostico':diagnostico.to_dict('records')}
    return JSONResponse(content= datos)

##Octava consulta
@app.get("/dias_top_registro/{nombre}/{id}")
async def obtener_lista_top4_vacas(nombre: str, id: str):
    data_finca = setle_clean(nombre)
    finca = filter_area_perimetro(df_gps,data_finca['latitud_c'],data_finca['longitud_c'],data_finca['hectares'])
    df_vaca= data_devices(finca,id)
    a = df_vaca.groupby(df_vaca['createdAt'].dt.date).count()
    orden = a['UUID'].sort_values(ascending=False).head(4)
    lista = list(orden.index)
    return lista


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app,host="localhost",port=8000)