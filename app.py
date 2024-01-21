from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import os

app = Flask(__name__, template_folder='C:/Users/manua/Documents/psi/templates/')

def clean_numeric_string(x):
    # Aquí puedes implementar la lógica para limpiar el formato numérico si es necesario
    return x

def calcular_valores(aprovisionamientos, amortizaciones, impuestos, capital_variable, produccion, excel_path):
    # Cargar datos desde el archivo Excel
    df_excel = pd.read_excel(excel_path, engine='openpyxl')

    # Calcular los valores según la fórmula
    plusvalia = produccion - (amortizaciones + aprovisionamientos) - capital_variable - impuestos
    tasa_plusvalia = plusvalia / capital_variable
    tasa_ganancia = plusvalia / (capital_variable + amortizaciones + aprovisionamientos)
    acumulacion_capital = (amortizaciones + aprovisionamientos)/ capital_variable
    ciclos = 1 + acumulacion_capital + tasa_plusvalia
    # Calcular la diferencia
    diferencia_plusvalia = plusvalia - df_excel['Pv'][0]
    diferencia_tasa_plusvalia = 100*(tasa_plusvalia - df_excel['Tp'][0])
    diferencia_tasa_ganancia = 100*(tasa_ganancia - df_excel['Tg'][0])
    diferencia_acumulacion_capital = acumulacion_capital - df_excel['Ak'][0]
    diferencia_ciclos = ciclos - df_excel['C'][0]

    # Crear una gráfica
    fig, ax = plt.subplots(figsize=(20, 6))
    valores = [diferencia_tasa_plusvalia,
               diferencia_tasa_ganancia,
               diferencia_acumulacion_capital,
               diferencia_ciclos]

    etiquetas = ['Diferencia Tasa Plusvalía',
                 'Diferencia Tasa Ganancia',
                 'Diferencia Acumulación Capital',
                 'Diferencia Ciclos']

    ax.bar(etiquetas, valores)
    plt.title('Comparación de Valores')
    plt.xlabel('Categoría')
    plt.ylabel('Valor')

    # Convertir la gráfica a formato base64 para mostrar en la web
    img = BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    grafica_base64 = base64.b64encode(img.getvalue()).decode()

    return {
        'plusvalia': plusvalia,
        'tasa_plusvalia': tasa_plusvalia,
        'tasa_ganancia': tasa_ganancia,
        'acumulacion_capital': acumulacion_capital,
        'ciclos': ciclos,
        'diferencia_plusvalia': diferencia_plusvalia,
        'diferencia_tasa_plusvalia': diferencia_tasa_plusvalia,
        'diferencia_tasa_ganancia': diferencia_tasa_ganancia,
        'diferencia_acumulacion_capital': diferencia_acumulacion_capital,
        'diferencia_ciclos': diferencia_ciclos,
        'grafica_base64': grafica_base64
    }


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        aprovisionamientos = float(request.form['aprovisionamientos'])
        amortizaciones = float(request.form['amortizaciones'])
        impuestos = float(request.form['impuestos'])
        capital_variable = float(request.form['capital_variable'])
        produccion = float(request.form['produccion'])
        excel_path = request.files['excel_file']

        # Guardar el archivo Excel temporalmente
        excel_path.save('temp_excel.xlsx')

        resultados = calcular_valores(aprovisionamientos, amortizaciones, impuestos, capital_variable, produccion, 'temp_excel.xlsx')

        return render_template('resultados.html', resultados=resultados)
    return render_template('formulario.html')

if __name__ == '__main__':
    app.run(debug=True)
