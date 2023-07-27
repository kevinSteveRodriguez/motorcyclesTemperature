import network
import time
from machine import Pin, ADC, I2C
from utime import sleep, sleep_ms, ticks_ms
from ssd1306 import SSD1306_I2C
from max6675 import MAX6675
import ufirebase as firebase

ancho = 128
alto = 64
alert_message = "ALERTA"
danger_message = "PELIGRO"
normal_message = "ESTABLE"
value_temp_alert = 50.1
value_temp_danger = 100.1

i2c = I2C(0, scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(ancho, alto, i2c)
print(i2c.scan(), "Conectada")


so = Pin(5, Pin.IN)  # Data de entrada
sck = Pin(18, Pin.OUT)
cs = Pin(19, Pin.OUT)  # Selector de canal

max = MAX6675(sck, cs, so)


def conectaWifi(red, password):
    global miRed
    miRed = network.WLAN(network.STA_IF)
    if not miRed.isconnected():  # Si no está conectado…
        miRed.active(True)  # activa la interface
        miRed.connect(red, password)  # Intenta conectar con la red
        print('Conectando a la red', red + "…")
        timeout = time.time()
        while not miRed.isconnected():  # Mientras no se conecte..
            if (time.ticks_diff(time.time(), timeout) > 10):
                return False
    return True


if conectaWifi("EndpointEthernetR5G", "PASS543212"):

    print("Conexión exitosa!")
    print('Datos de la red (IP/netmask/gw/DNS):', miRed.ifconfig())
    print("Conectado!")

    firebase.setURL(
        "https://motorcyclestemperature-default-rtdb.firebaseio.com/")

    try:
        while True:
            tem = max.read()
            print("Tem:{}°c".format(tem))
            sleep_ms(50)
            temperature = {"Level": tem}
            firebase.put("motorcycle/temp/{}".format(ticks_ms()),
                         temperature, bg=0)
            print("Dato enviado")

            # firebase.get("motorcycle/temp/", "dataObtained",bg=0)
            # print("Dato obtenido: " + str(firebase.dataObtained))

            oled.fill(0)
            oled.vline(0, 0, 20, 1)
            oled.vline(125, 0, 20, 1)
            oled.hline(0, 0, 125, 1)
            oled.hline(0, 20, 125, 1)
            oled.text("TEMPERATURA", 20, 10, 1)
            oled.text("Tem:", 0, 30, 1)
            oled.text(str(tem), 60, 30, 1)
            oled.text("c", 110, 30, 1)
            oled.text("Estado:", 0, 45, 1)

            if tem > value_temp_alert:
                oled.text(str(alert_message), 60, 45, 1)
                print("La temperatura de tu moto esta en estado: " + alert_message)
            elif tem > value_temp_danger:
                oled.text(str(danger_message), 60, 45, 1)
                print("La temperatura de tu moto esta en estado: " + danger_message)
            else:
                oled.text(str(normal_message), 60, 45, 1)
                print("La temperatura de tu moto esta en estado: " + normal_message)
            oled.show()
            sleep_ms(50)

    except KeyboardInterrupt:
        print("Proceso Abortado")

else:
    print("Imposible conectar")
    miRed.active(False)
