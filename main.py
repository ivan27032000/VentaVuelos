import telebot
import time
import json
import random as rd
import geopy.distance
import math

token = "1238450301:AAH6bn7nqmDvQMlmU8--OT6FuQbX7uK5a38"

bot = telebot.TeleBot(token = token)

#TODO: cambiar ruta en google colab
resp_bot = json.load(open("resp_bot.json", "r",encoding="utf-8", errors="ignore"))
aeropuertos = json.load(open("aeropuertos.json", "r", encoding="utf-8", errors="ignore"))


#Buscar aeropuerto por codigo iata
def buscar_aeropuerto_iata(codigo_iata):
    for aeropuerto in aeropuertos:
        if aeropuerto["iata"] == codigo_iata:
            return aeropuerto
    return None


#Lista para guardar las sesiones
sesiones = []


#Clase sesion para guardar los datos del usuario
class Sesion:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.paso_actual = 1
        self.cedula = ""
        self.aeropuerto_destino = ""


#Busca la sesion por el chat_id
def buscar_sesion(chat_id):
    for sesion in sesiones:
        if sesion.chat_id == chat_id:
            return sesion
    return None


#Calcula el valro dele vuelo según la distancia
def calcular_precio(aeropuerto):
    coordinada_1 = (-2.1575, -79.883611)
    coordinada_2 = (aeropuerto["lat"], aeropuerto["lon"])

    distancia = geopy.distance.distance(coordinada_1, coordinada_2).km
    
    return distancia *0.01 * math.log(distancia)


#Mensaje de saludo que va a saludar y explcia el funcionamiento del bot
@bot.message_handler(commands = ["start", "iniciar"])
def presentarse(message):
    nombre_usuario = message.from_user.first_name + " "+ message.from_user.last_name

    bot.reply_to(message, resp_bot["saludo"] + nombre_usuario)
    bot.send_message(message.chat.id, resp_bot["ayuda"])


#Explica el funcionamiento del programa
@bot.message_handler(commands = ["ayuda"])
def ayudar(message):
    bot.reply_to(message, resp_bot["ayuda"])


#0 paso - muestra los países para viajar
@bot.message_handler(commands = ["reservar"], func = lambda msg: buscar_sesion(msg.chat.id) is None)
def mostrar_paises_destino(message):
    sesion = Sesion(message.chat.id)
    sesiones.append(sesion)
    print(sesiones)
    bot.reply_to(message, "Vuelos disponibles")

    for aeropuerto in aeropuertos:
        mensaje = "/" + aeropuerto["iata"] + " - " + aeropuerto["name"] + " (" + aeropuerto["state"] +" - "+aeropuerto["city"] + ")"
        bot.send_message(chat_id = sesion.chat_id, text = mensaje)


@bot.message_handler(commands = ["UIO", "PTY", "GPS", "BRO", "JFK", "FLL", "BOG", "AMS"], func = lambda msg: buscar_sesion(msg.chat.id) is not None and buscar_sesion(msg.chat.id).paso_actual == 1)
def mostrar_info_viaje(message):
    sesion = buscar_sesion(message.chat.id)
    sesion.paso_actual += 1
    codigo_iata = message.text[1:]
    aeropuerto = buscar_aeropuerto_iata(codigo_iata)

    precio = str("{:.2f}".format(calcular_precio(aeropuerto)))

    mensaje = resp_bot["info_vuelo"][0] + aeropuerto["name"]+" "+ resp_bot["info_vuelo"][1] + "$" + precio +"\n"+resp_bot["info_vuelo"][4] +aeropuerto["hours"] +"\n"+ resp_bot["info_vuelo"][2]+"\n"+resp_bot["info_vuelo"][3]

    bot.send_message(message.chat.id, mensaje)


@bot.message_handler(commands = ["aceptar"], func = lambda msg: buscar_sesion(msg.chat.id) != None and buscar_sesion(msg.chat.id).paso_actual == 2)
def aceptar(message):
    sesion = buscar_sesion(message.chat.id)
    sesion.paso_actual = 1
    
    bot.send_message(sesion.chat_id, resp_bot["aceptar"])
    bot.reply_to(message, resp_bot["ayuda"])

@bot.message_handler(commands = ["cancelar"] , func = lambda msg: buscar_sesion(msg.chat.id) != None)
def cancelar(message):
    sesion = buscar_sesion(message.chat.id)
    sesion.paso_actual = 1

    bot.send_message(sesion.chat_id, resp_bot["cancelar"])

    bot.reply_to(message, resp_bot["ayuda"])
    
    sesiones.remove(sesion)
    

while True:
    try:
        bot.polling()
    except Exception:
        time.sleep(15)