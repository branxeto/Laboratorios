#Utilizando el mismo conjunto de datos previamente seleccionado,
#diseñe e implemente una técnica que permita entrenar en paralelo múltiples
#instancias (al menos tres por técnica) de Regresión Logística y SVM, variando sus
#hiperparámetros (por ejemplo: batch size, tasa de aprendizaje, etc, según sea el
#caso). Los parámetros de cada configuración deberán definirse en un archivo de
#configuración externo, y el entrenamiento deberá realizarse utilizando el 80% de los
#datos. Cada modelo se evaluará periódicamente (solo con datos de entrenamiento),
#y por cada cinco épocas deberá descartarse la configuración con peor desempeño
#entre todas las configuraciones restantes. Para las dos mejores configuraciones,
#presente métricas de evaluación utilizando el conjunto de testing, es decir, el 20%
#de los datos. Analice los resultados obtenidos en función de los hiperparámetros
#seleccionados.

