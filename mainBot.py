import pickle  # guardar modelos
import random  # escoger respeustas aleatorias
import json
import tensorflow
import tflearn
import numpy
import nltk
import discord
from nltk.stem.lancaster import LancasterStemmer  # Mas entendible
from tensorflow.python.compiler.tensorrt import trt_convert as trt
stemmer = LancasterStemmer()

# MONGO

from clasification import Clasification


# nltk.download('punkt')

key = ''

with open("contenido.json", encoding='utf-8') as archivo:
    datos = json.load(archivo)
# datos = Clasification.find()

try:
    with open("variables.pickle", "rb") as archivoPickle:
        palabras, tags, entrenamiento, salida = pickle.load(archivoPickle)
except:
    palabras = []
    tags = []
    auxX = []
    auxY = []

    for contenido in datos["contenido"]:
        for patrones in contenido["patrones"]:
            '''Diferencia entre tokenize y split
            tokenize va a reconocer los puntos especiales automaticamente.
            En split se lo tienes que pasar
            '''
            auxPalabra = nltk.word_tokenize(
                patrones)  # Una frase, la separa en palabras.
            palabras.extend(auxPalabra)
            auxX.append(auxPalabra)
            auxY.append(contenido["tag"])

            if contenido["tag"] not in tags:
                tags.append(contenido["tag"])

    palabras = [stemmer.stem(w.lower()) for w in palabras if w != "?"]
    palabras = sorted(list(set(palabras)))
    tags = sorted(tags)
    entrenamiento = []
    salida = []

    salidaVacia = [0 for _ in range(len(tags))]

    for x, documento in enumerate(auxX):
        cubeta = []
        auxPalabra = [stemmer.stem(w.lower()) for w in documento]
        for w in palabras:
            if w in auxPalabra:
                cubeta.append(1)
            else:
                cubeta.append(0)
        filaSalida = salidaVacia[:]
        # El la lista de los indices del tag
        # El contendio de Y en cada uno de los indices

        filaSalida[tags.index(auxY[x])] = 1
        entrenamiento.append(cubeta)
        salida.append(filaSalida)

    entrenamiento = numpy.array(entrenamiento)
    salida = numpy.array(salida)
    with open("variables.pickle", "wb") as archivoPickle:
        pickle.dump((palabras, tags, entrenamiento, salida), archivoPickle)


tensorflow.compat.v1.reset_default_graph()

red = tflearn.input_data(shape=[None, len(entrenamiento[0])])
red = tflearn.fully_connected(red, 100)
red = tflearn.fully_connected(red, 100)
red = tflearn.fully_connected(red, len(salida[0]), activation="softmax")
red = tflearn.regression(red)


modelo = tflearn.DNN(red)
# modelo.load("modelo.tflearn")
modelo.fit(entrenamiento, salida, n_epoch=1000, batch_size=10, show_metric=True)
modelo.save("modelo.tflearn")


def mainBot():
    global key
    client = discord.Client()
    while True:
        @client.event
        async def on_message(message):
            if message.author == client.user:
                return
            cubeta = [0 for _ in range(len(palabras))]
            entradaProcesada = nltk.word_tokenize(message.content)
            entradaProcesada = [stemmer.stem(
                palabra.lower()) for palabra in entradaProcesada]
            for palabraIndividual in entradaProcesada:
                for i, palabra in enumerate(palabras):
                    if palabra == palabraIndividual:
                        cubeta[i] = 1

            resultados = modelo.predict([numpy.array(cubeta)])
            resultadosIndices = numpy.argmax(resultados)
            tag = tags[resultadosIndices]

            for tagAux in datos["contenido"]:
                if tagAux["tag"] == tag:
                    respuesta = tagAux["respuestas"]
            await message.channel.send(random.choice(respuesta))
        client.run(key)


mainBot()
