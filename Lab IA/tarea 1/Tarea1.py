import pandas as pd
import numpy as np
from pgmpy.estimators import GES, HillClimbSearch, BayesianEstimator
from pgmpy.models import DiscreteBayesianNetwork
from sklearn.model_selection import train_test_split
from pgmpy.inference import VariableElimination

#Cargar datos
datos = pd.read_csv('Vehicles.csv', nrows=10000)

# Ajustar datos para red bayesiana
if 'cylinders' in datos.columns:
    datos['cylinders'] = datos['cylinders'].str.extract(r"(\d+)",expand=False).astype(float).astype('Int64').astype('category')
    
if 'year' in datos.columns:
    datos['year'] = pd.to_numeric(datos['year'], errors='coerce')
    datos['year'] = pd.qcut(datos['year'], q=3, labels=['viejo','medio','nuevo'], duplicates='drop')

if 'price' in datos.columns:
    datos['price'] = pd.to_numeric(datos['price'], errors='coerce')
    datos['price'] = pd.qcut(datos['price'], q=3, labels=['barato','medio','caro'], duplicates='drop')
    
for c in datos.columns:
    if datos[c].dtype == 'object':
        datos[c] = datos[c].astype('category')
        
datos = datos.dropna().copy()
for c in datos.select_dtypes(include='category').columns:
    datos[c] = datos[c].cat.remove_unused_categories()

# <----- Parte 1 ----->
#Dividir datos en entrenamiento y prueba
train_data, test_data = train_test_split(datos, test_size=0.3, random_state=42)

#Aprendizaje de estructuras 
print("Aprendizaje de estructura con GES...")
ges = GES(train_data)
ges_model = ges.estimate(scoring_method="k2")
print("Termino de estimacion estructura con GES")
print("GES edges:", list(ges_model.edges()))
print("GES nodes:", list(ges_model.nodes()))

print("Aprendizaje de estructura con HC...")
hillclimbsearch = HillClimbSearch(train_data)
model_hc = hillclimbsearch.estimate(scoring_method='k2')
print("Termino de estimacion estructura con HC")
print("HC edges:", list(model_hc.edges()))
print("HC nodes:", list(model_hc.nodes()))

#Creacion de modelos bayesianos discretos
ges_bn = DiscreteBayesianNetwork(ges_model.edges())
hc_bn = DiscreteBayesianNetwork(model_hc.edges())

#Estimacion de parametros
print("Estimacion de parametros con GES:")
ges_bn.fit(train_data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)

print("Estimacion de parametros con HC:")
hc_bn.fit(train_data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)
        
#Inferencias GES
inference_ges = VariableElimination(ges_bn)
query1 = inference_ges.query(variables=['price'], evidence={'year': 'nuevo', 'cylinders': 4})
print("Inferencia GES - P(price | year=nuevo, cylinders=4):")
print(query1)

query2 = inference_ges.query(variables=['type'], evidence={'price': 'medio', 'manufacturer': 'ford'})
print("Inferencia GES - P(type | price=medio, manufacturer=ford):")
print(query2)

query3 = inference_ges.query(variables=['condition'], evidence={'year': 'medio', 'cylinders': 6})
print("Inferencia GES - P(condition | year=medio, cylinders=6):")
print(query3)

query4 = inference_ges.query(variables=['manufacturer'], evidence={'price': 'caro', 'type': 'sedan'})
print("Inferencia GES - P(manufacturer | price=caro, type=sedan):")
print(query4)

# Comparación de resultados GES
query1_filas = test_data[(test_data['year']=='medio') & (test_data['cylinders'] == 4)].shape[0]
query1_correctos = test_data[(test_data['year']=='medio') & (test_data['cylinders'] == 4) & (test_data['price'] == 'caro')].shape[0]
print(query1_filas,query1_correctos)
print(f"Porcentaje de aciertos para query1: {query1_correctos/query1_filas}")
print("Probabilidad inferida para query1:", query1.values[query1.state_names['price'].index('caro')])

query2_filas = test_data[(test_data['price'] == 'medio') & (test_data['manufacturer'] == 'ford')].shape[0]
query2_correctos = test_data[(test_data['price'] == 'medio') & (test_data['manufacturer'] == 'ford') & (test_data['type'] == 'sedan')].shape[0]
print(query2_filas, query2_correctos)
print(f"Porcentaje de aciertos para query2: {query2_correctos/query2_filas:.4f}")
print("Probabilidad inferida para query2:", query2.values[query2.state_names['type'].index('sedan')])

query3_filas = test_data[(test_data['year'] == 'medio') & (test_data['cylinders'] == 6)].shape[0]
query3_correctos = test_data[(test_data['year'] == 'medio') & (test_data['cylinders'] == 6) & (test_data['condition'] == 'excellent')].shape[0]
print(query3_filas, query3_correctos)
print(f"Porcentaje de aciertos para query3: {query3_correctos/query3_filas:.4f}")
print("Probabilidad inferida para query3:", query3.values[query3.state_names['condition'].index('excellent')])

query4_filas = test_data[(test_data['price'] == 'caro') & (test_data['type'] == 'sedan')].shape[0]
query4_correctos = test_data[(test_data['price'] == 'caro') & (test_data['type'] == 'sedan') & (test_data['manufacturer'] == 'ford')].shape[0]
print(query4_filas, query4_correctos)
print(f"Porcentaje de aciertos para query4: {query4_correctos/query4_filas:.4f}")
print("Probabilidad inferida para query4:", query4.values[query4.state_names['manufacturer'].index('ford')])

# Inferencias de resultados HC
inference_hc = VariableElimination(hc_bn)
query5 = inference_hc.query(variables=['price'], evidence={'manufacturer': 'ford', 'condition': 'excellent'})
print("Inferencia HC - P(price | manufacturer=ford, condition=excellent):")
print(query5)

query6 = inference_hc.query(variables=['type'], evidence={'paint_color': 'white', 'cylinders': 6})
print("Inferencia HC - P(type | paint_color=white, cylinders=6):")
print(query6)

query7 = inference_hc.query(variables=['manufacturer'], evidence={'condition': 'fair', 'cylinders': 8})
print("Inferencia HC - P(manufacturer | condition=fair, cylinders=8):")
print(query7)

query8 = inference_hc.query(variables=['condition'], evidence={'year': 'medio', 'price': 'caro'})
print("Inferencia HC - P(condition | year=medio, price=caro):")
print(query8)

# Comparación de resultados HC
query5_filas = test_data[(test_data['manufacturer'] == 'ford') & (test_data['condition'] == 'excellent')].shape[0]
query5_correctos = test_data[(test_data['manufacturer'] == 'ford') & (test_data['condition'] == 'excellent') & (test_data['price'] == 'caro')].shape[0]
print(query5_filas, query5_correctos)
print(f"Porcentaje de aciertos para query5: {query5_correctos/query5_filas:.4f}")
print("Probabilidad inferida para query5:", query5.values[query5.state_names['price'].index('caro')])

query6_filas = test_data[(test_data['paint_color'] == 'white') & (test_data['cylinders'] == 6)].shape[0]
query6_correctos = test_data[(test_data['paint_color'] == 'white') & (test_data['cylinders'] == 6) & (test_data['type'] == 'truck')].shape[0]
print(query6_filas, query6_correctos)
print(f"Porcentaje de aciertos para query6: {query6_correctos/query6_filas:.4f}")
print("Probabilidad inferida para query6:", query6.values[query6.state_names['type'].index('truck')])

query7_filas = test_data[(test_data['condition'] == 'fair') & (test_data['cylinders'] == 8)].shape[0]
query7_correctos = test_data[(test_data['condition'] == 'fair') & (test_data['cylinders'] == 8) & (test_data['manufacturer'] == 'ford')].shape[0]
print(query7_filas, query7_correctos)
print(f"Porcentaje de aciertos para query7: {query7_correctos/query7_filas:.4f}")
print("Probabilidad inferida para query7:", query7.values[query7.state_names['manufacturer'].index('ford')])

query8_filas = test_data[(test_data['year'] == 'medio') & (test_data['price'] == 'caro')].shape[0]
query8_correctos = test_data[(test_data['year'] == 'medio') & (test_data['price'] == 'caro') & (test_data['condition'] == 'excellent')].shape[0]
print(query8_filas, query8_correctos)
print(f"Porcentaje de aciertos para query8: {query8_correctos/query8_filas:.4f}")
print("Probabilidad inferida para query8:", query8.values[query8.state_names['condition'].index('excellent')])


# <----- Parte 2 ----->

#Generar datos sintéticos
num_sinteticos = datos.shape[0]/2
def generate_synthetic_data(num_filas):
    sinteticos = pd.DataFrame({
        'region': np.random.choice(datos['region'].unique(), num_filas),
        'price': np.random.choice(['barato', 'medio', 'caro'], num_filas),  # Precios aleatorios entre 1000 y 50000
        'year': np.random.choice(['viejo', 'medio', 'nuevo'], num_filas),  # Años entre 2000 y 2023
        'manufacturer': np.random.choice(datos['manufacturer'].unique(), num_filas),  # Marcas aleatorias
        'condition': np.random.choice(['excellent', 'good', 'fair', 'like new'], num_filas),
        'cylinders': np.random.choice([4, 6, 8, 10, 12], num_filas),  # Números de cilindros comunes
        'type': np.random.choice(['truck', 'SUV', 'sedan', 'van', 'pickup', 'wagon', 'mini-van', 'offroad'], num_filas),
        'paint_color': np.random.choice(['black', 'white', 'silver', 'blue', 'red', 'green', 'yellow'], num_filas)
    })
    return sinteticos
datos_sinteticos = generate_synthetic_data(int(num_sinteticos))
datos_finales = pd.concat([datos, datos_sinteticos], ignore_index=True)
print("Datos originales:", datos.shape[0], type(datos))
print("Datos sintéticos:", datos_sinteticos.shape[0], type(datos_sinteticos))
print("Datos finales:", datos_finales.shape[0], type(datos_finales))


#Dividir datos en entrenamiento y prueba
train_data, test_data = train_test_split(datos_finales, test_size=0.3, random_state=42)

#Aprendizaje de estructuras 
print("Aprendizaje de estructura con GES...")
ges = GES(train_data)
ges_model = ges.estimate(scoring_method="k2")
print("Termino de estimacion estructura con GES")
print("GES edges:", list(ges_model.edges()))
print("GES nodes:", list(ges_model.nodes()))

print("Aprendizaje de estructura con HC...")
hillclimbsearch = HillClimbSearch(train_data)
model_hc = hillclimbsearch.estimate(scoring_method='k2')
print("Termino de estimacion estructura con HC")
print("HC edges:", list(model_hc.edges()))
print("HC nodes:", list(model_hc.nodes()))

#Creacion de modelos bayesianos discretos
ges_bn = DiscreteBayesianNetwork(ges_model.edges())
hc_bn = DiscreteBayesianNetwork(model_hc.edges())

#Estimacion de parametros
print("Estimacion de parametros con GES:")
ges_bn.fit(train_data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)

print("Estimacion de parametros con HC:")
hc_bn.fit(train_data, estimator=BayesianEstimator, prior_type='BDeu', equivalent_sample_size=10)
        
#Inferencias GES
inference_ges = VariableElimination(ges_bn)
query1 = inference_ges.query(variables=['price'], evidence={'year': 'nuevo', 'cylinders': 4})
print("Inferencia GES - P(price | year=nuevo, cylinders=4):")
print(query1)

query2 = inference_ges.query(variables=['type'], evidence={'price': 'medio', 'manufacturer': 'ford'})
print("Inferencia GES - P(type | price=medio, manufacturer=ford):")
print(query2)

query3 = inference_ges.query(variables=['condition'], evidence={'year': 'medio', 'cylinders': 6})
print("Inferencia GES - P(condition | year=medio, cylinders=6):")
print(query3)

query4 = inference_ges.query(variables=['manufacturer'], evidence={'price': 'caro', 'type': 'sedan'})
print("Inferencia GES - P(manufacturer | price=caro, type=sedan):")
print(query4)

# Comparación de resultados GES
query1_filas = test_data[(test_data['year']=='medio') & (test_data['cylinders'] == 4)].shape[0]
query1_correctos = test_data[(test_data['year']=='medio') & (test_data['cylinders'] == 4) & (test_data['price'] == 'caro')].shape[0]
print(query1_filas,query1_correctos)
print(f"Porcentaje de aciertos para query1: {query1_correctos/query1_filas}")
print("Probabilidad inferida para query1:", query1.values[query1.state_names['price'].index('caro')])

query2_filas = test_data[(test_data['price'] == 'medio') & (test_data['manufacturer'] == 'ford')].shape[0]
query2_correctos = test_data[(test_data['price'] == 'medio') & (test_data['manufacturer'] == 'ford') & (test_data['type'] == 'sedan')].shape[0]
print(query2_filas, query2_correctos)
print(f"Porcentaje de aciertos para query2: {query2_correctos/query2_filas:.4f}")
print("Probabilidad inferida para query2:", query2.values[query2.state_names['type'].index('sedan')])

query3_filas = test_data[(test_data['year'] == 'medio') & (test_data['cylinders'] == 6)].shape[0]
query3_correctos = test_data[(test_data['year'] == 'medio') & (test_data['cylinders'] == 6) & (test_data['condition'] == 'excellent')].shape[0]
print(query3_filas, query3_correctos)
print(f"Porcentaje de aciertos para query3: {query3_correctos/query3_filas:.4f}")
print("Probabilidad inferida para query3:", query3.values[query3.state_names['condition'].index('excellent')])

query4_filas = test_data[(test_data['price'] == 'caro') & (test_data['type'] == 'sedan')].shape[0]
query4_correctos = test_data[(test_data['price'] == 'caro') & (test_data['type'] == 'sedan') & (test_data['manufacturer'] == 'ford')].shape[0]
print(query4_filas, query4_correctos)
print(f"Porcentaje de aciertos para query4: {query4_correctos/query4_filas:.4f}")
print("Probabilidad inferida para query4:", query4.values[query4.state_names['manufacturer'].index('ford')])

# Inferencias de resultados HC
inference_hc = VariableElimination(hc_bn)
query5 = inference_hc.query(variables=['price'], evidence={'manufacturer': 'ford', 'condition': 'excellent'})
print("Inferencia HC - P(price | manufacturer=ford, condition=excellent):")
print(query5)

query6 = inference_hc.query(variables=['type'], evidence={'paint_color': 'white', 'cylinders': 6})
print("Inferencia HC - P(type | paint_color=white, cylinders=6):")
print(query6)

query7 = inference_hc.query(variables=['manufacturer'], evidence={'condition': 'fair', 'cylinders': 8})
print("Inferencia HC - P(manufacturer | condition=fair, cylinders=8):")
print(query7)

query8 = inference_hc.query(variables=['condition'], evidence={'year': 'medio', 'price': 'caro'})
print("Inferencia HC - P(condition | year=medio, price=caro):")
print(query8)

# Inferencia 5: P(price | manufacturer=ford, condition=excellent)
query5_filas = test_data[(test_data['manufacturer'] == 'ford') & (test_data['condition'] == 'excellent')].shape[0]
query5_correctos = test_data[(test_data['manufacturer'] == 'ford') & (test_data['condition'] == 'excellent') & (test_data['price'] == 'caro')].shape[0]
print(query5_filas, query5_correctos)
print(f"Porcentaje de aciertos para query5: {query5_correctos/query5_filas:.4f}")
print("Probabilidad inferida para query5:", query5.values[query5.state_names['price'].index('caro')])

# Inferencia 6: P(type | paint_color=white, cylinders=6)
query6_filas = test_data[(test_data['paint_color'] == 'white') & (test_data['cylinders'] == 6)].shape[0]
query6_correctos = test_data[(test_data['paint_color'] == 'white') & (test_data['cylinders'] == 6) & (test_data['type'] == 'truck')].shape[0]
print(query6_filas, query6_correctos)
print(f"Porcentaje de aciertos para query6: {query6_correctos/query6_filas:.4f}")
print("Probabilidad inferida para query6:", query6.values[query6.state_names['type'].index('truck')])

# Inferencia 7: P(manufacturer | condition=fair, cylinders=8)
query7_filas = test_data[(test_data['condition'] == 'fair') & (test_data['cylinders'] == 8)].shape[0]
query7_correctos = test_data[(test_data['condition'] == 'fair') & (test_data['cylinders'] == 8) & (test_data['manufacturer'] == 'ford')].shape[0]
print(query7_filas, query7_correctos)
print(f"Porcentaje de aciertos para query7: {query7_correctos/query7_filas:.4f}")
print("Probabilidad inferida para query7:", query7.values[query7.state_names['manufacturer'].index('ford')])

# Inferencia 8: P(condition | year=2015, price=caro)
query8_filas = test_data[(test_data['year'] == 'medio') & (test_data['price'] == 'caro')].shape[0]
query8_correctos = test_data[(test_data['year'] == 'medio') & (test_data['price'] == 'caro') & (test_data['condition'] == 'excellent')].shape[0]
print(query8_filas, query8_correctos)
print(f"Porcentaje de aciertos para query8: {query8_correctos/query8_filas:.4f}")
print("Probabilidad inferida para query8:", query8.values[query8.state_names['condition'].index('excellent')])