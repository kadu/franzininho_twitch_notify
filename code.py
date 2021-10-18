import ssl
import socketpool
import wifi
import board
import neopixel_write
import digitalio
import time
import neopixel
import adafruit_minimqtt.adafruit_minimqtt as MQTT
import ipaddress
from secrets import secrets

##voltar a escrever nos leds (barra de led) as corres e basear essas cores no mqtt ja implentado

try:
    from secrets import secrets
except ImportError:
    print("WiFi secrets are kept in secrets.py, please add them there!")
    raise


pixels = neopixel.NeoPixel(board.IO1, 10)
pixels.fill((255,0,0))
time.sleep(2)
pixels.fill((0,0,0))

print("ESP32-S2 WebClient Test")
print("My MAC addr:", [hex(i) for i in wifi.radio.mac_address])
print("Connecting to %s"%secrets["ssid"])
wifi.radio.connect(secrets["ssid"], secrets["password"])
print("Connected to %s!"%secrets["ssid"])
print("My IP address is", wifi.radio.ipv4_address)

### Topic Setup ###
# MQTT Topic
# Use this topic if you'd like to connect to a standard MQTT broker
mqtt_topic = "test/franzininho"

def connect(mqtt_client, userdata, flags, rc):
    # This function will be called when the mqtt_client is connected
    # successfully to the broker.
    print("Connected to MQTT Broker!")
    print("Flags: {0}\n RC: {1}".format(flags, rc))


def disconnect(mqtt_client, userdata, rc):
    # This method is called when the mqtt_client disconnects
    # from the broker.
    print("Disconnected from MQTT Broker!")


def subscribe(mqtt_client, userdata, topic, granted_qos):
    # This method is called when the mqtt_client subscribes to a new feed.
    print("Subscribed to {0} with QOS level {1}".format(topic, granted_qos))


def unsubscribe(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client unsubscribes from a feed.
    print("Unsubscribed from {0} with PID {1}".format(topic, pid))


def publish(mqtt_client, userdata, topic, pid):
    # This method is called when the mqtt_client publishes data to a feed.
    print("Published to {0} with PID {1}".format(topic, pid))

def message(client, topic, message):
    # Method callled when a client's subscribed feed has a new value.
    print("New message on topic {0}: {1}".format(topic, message))
    if(topic == "test/franzininho"):
        try:
            colors = message.split(',')
            pixel_color = bytearray([int(colors[0]),int(colors[1]),int(colors[2])])
            neopixel_write.neopixel_write(pin, pixel_color)
        except:
            print("Pessoas do Mal! é só o que eu digo!");

    if(topic == "franzininho/guerra"):
        try:
            leds = message.split(',')
            contador = 0;
            for cor in leds:
                if(cor == "2"):
                    print(contador, " AZUL")
                    pixels[contador] = (0,0,255)
                if(cor == "1"):
                    print(contador, " VERMELHO")
                    pixels[contador] = (255,0,0)
                if(cor == "0"):
                    print(contador, " APAGADO")
                    pixels[contador] = (0,0,0)
                contador = contador +1

            print(leds)
        except:
            print("Deu Ruim no cabo de guerra")


# Create a socket pool
pool = socketpool.SocketPool(wifi.radio)

# Set up a MiniMQTT Client
mqtt_client = MQTT.MQTT(
    broker=secrets["broker"],
    port=1883,
    username=secrets["user"],
    password=secrets["pass"],
    socket_pool=pool,
    ssl_context=ssl.create_default_context(),
)

# Connect callback handlers to mqtt_client
mqtt_client.on_connect = connect
mqtt_client.on_disconnect = disconnect
mqtt_client.on_subscribe = subscribe
mqtt_client.on_unsubscribe = unsubscribe
mqtt_client.on_publish = publish
mqtt_client.on_message = message

print("Attempting to connect to %s" % mqtt_client.broker)
mqtt_client.connect()

print("Subscribing to %s" % mqtt_topic)
mqtt_client.subscribe(mqtt_topic)
mqtt_client.subscribe("franzininho/guerra")


print("Publishing to %s" % mqtt_topic)
mqtt_client.publish(mqtt_topic, "Hello Broker!")

print("Publishing to LEDMATRIX")
mqtt_client.publish("homie/ledmatrix/message/message/set", "Oi, eu sou o Franzininho WIFI com Cobrinha PYTHONESCA")


#print("Unsubscribing from %s" % mqtt_topic)
#mqtt_client.unsubscribe(mqtt_topic)

#print("Disconnecting from %s" % mqtt_client.broker)
#mqtt_client.disconnect()




print("Entering in the matrix!")
while True:
    mqtt_client.loop()
