# This file contains extra validation field to models

from rest_framework.serializers import ValidationError
from datetime import datetime
from django.http.response import HttpResponse

import pandas as pd

# Only permits level between 1 and 5
def between1_5(value):
    if (value < 1 or value > 5):
        return ValidationError(' Debe seleccionar un valor del 1 al 5 ') 
  
# Only permits years before actual year and before 
def year(value):
    if value < (datetime.now.year-70) or value >= datetime.now.year:
        return ValidationError(f' No puede ser un año superior al actual o anterior a {datetime.now.year-70}')
    
# --------- other funtions to generate a QUIZ---------
Opciones = {
    "Verdadero": "Verdadero",
    "True": "Verdadero",
    "Vertader": "Verdadero",
    "Falso": "Falso",
    "False": "Falso",
    "Fals": "Falso",
    "No lo sé": "No lo sé",
    "No ho sé": "No lo sé",
    "No en sé": "No lo sé",
    "No sé": "No lo sé",
}

# """
#     Ensures right decode to CSV if is not a UTF-8 CSV, because accents can't be resolved corrected.
#     Returns a new csv file in memory to be decoded into a new utf-8 file.
# """
# def ensureDecode(file):
#     contenido_str = file.read().decode("latin-1")
#     # To read text and not bytes in memory we need io library
#     archivo_en_memoria = io.StringIO(contenido_str)
#     return archivo_en_memoria


def normalizeFile(df):

    NEW_header = [
        "enunciado",
        "dimension",
        "area",
        "contenido",
        "dificultad",
        "solucion",
        "motivo",
        "opciones",
    ]

    # compare columns
    if len(NEW_header)!= len(df.columns):
        raise ValidationError(f'Column number incorrect. Expected {len(NEW_header)}: {', '.join(NEW_header)}')

    # Set columns header
    df.columns = NEW_header

    # set data types
    df = df.astype("string")
    # Transform to float first, ignored errors and put in NaN if fails
    df["dificultad"] = pd.to_numeric(df["dificultad"], errors="coerce")

    # NA values
    df["dificultad"] = df["dificultad"].fillna(0)

    # tranform to int
    df["dificultad"] = df["dificultad"].astype("int")

    # Delete all NaN rows
    df = df.dropna(how="all")

    # Manage NA values of all dataframe
    # fill value as back or forward value
    # bfill is back fill with the next no NaN value
    # df_bfill = df.bfill()
    df = df.ffill()

    # Advertise NaN values
    nan_positions = df.isna()
    # Obtain nan rows and columns indexes
    nan_locations = nan_positions.stack()
    nan_rows_columns = nan_locations[nan_locations].index
    for row, col in nan_rows_columns:
        raise ValidationError(f"Fila: {row}, Columna: {col} no tiene un valor")

    # Guardar orden
    df["ordenD"] = df["dimension"].str.extract(r"(\d+)\.").astype(int)

    df["dimension"] = df["dimension"].str.extract(r"([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)")
    df["ordenA"] = df["area"].str.extract(r"(?<=\d\.)(\d+)").astype(int)
    df["area"] = df["area"].str.extract(r"([a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+)")
    df["solucion"] = df["solucion"].str.capitalize().map(Opciones).astype("string")
    df["opciones"] = df["opciones"].str.split(";")

    
    # determine separator
    signos = ",;:?!.-_¨´+*^`[]¿¡'&%()$#·@!º\ª{} "
    signos_f = ",;:-_¨´+*^`[¿'&%($#·@º\ª{ "

    # # delete blanks before and after each colum
    for i in df.select_dtypes(include=["string"]).columns:
        df[i] = df[i].str.strip()
        df[i] = df[i].str.lstrip(signos + '"')
        df[i] = df[i].str.rstrip(signos_f)
        df[i] = df[i].str.capitalize()
 
    return pd.DataFrame(df)

def mapping(op):

    # Only the first option is capitalize to compare we need all of them
    if op.capitalize() in Opciones:
        op = Opciones[op.capitalize()]
        return op, Opciones[op.capitalize()]
    else:
        OptionError = Exception(f"No ha escrito bien las opciones")
        return OptionError
    
# Returns a response as a csv or excel file, if its passed a dataframe by param
def export_as_csv_or_excel(request, df, resultName):
    format = request.GET.get('format')
    if format == 'excel':
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{resultName}.xlsx"'
        df.to_excel(response, index=False, engine='openpyxl')
    else:  # CSV por defecto
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{resultName}.csv"'
        df.to_csv(response, index=False, sep=';', encoding='utf-8-sig')
    return response


'''Dataframe columns format to an ansew depends on their types'''
def format(df):
    df= df.replace({True: "Sí", False: "No"})
    for col in df.columns:    
        if df[col].dtype == 'datetime64' or df[col].dtype == 'datetime64[ns, UTC]' or df[col].dtype=='datetime64[ns]':
            df[col] = df[col].dt.strftime("%d/%m/%Y %H:%M:%S:%f") # vectorize best option
    return df