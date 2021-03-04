from clasification import Clasification
import json


with open('../contenido.json') as f:
  data = json.load(f)
  contenido = data['contenido']

  # print(data)

  for d in contenido:
      x = {}

      x['tag'] = d['tag']
      x['patrones'] = d['patrones']
      x['respuestas'] = d['respuestas']
      print(x)
      print("&&&&&&&&&&&&6")
      result = Clasification.insert_one(x)
      print(result)

  # # print(contenido)
  # for d in contenido:
  #     # print("//////////////////////7")
  #     # a = json.loads(d)
  #     #
  #     # print(a)
  #     x = Clasification.insert_one(d)
  #     print(x)
