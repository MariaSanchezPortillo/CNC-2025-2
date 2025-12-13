from machine import Pin, PWM
import time
#Configuracion de Leds
led1 = Pin(15, Pin.OUT)
led2 = Pin(2, Pin.OUT)
led3 = Pin(4, Pin.OUT)

led1.value(1)

# Configuración de los servos
servo_x = PWM(Pin(14), freq=50)  # Servo X en el pin 13
servo_y = PWM(Pin(13), freq=50)  # Servo Y en el pin 14
servo_z = PWM(Pin(27), freq=50)  # Servo Z en el pin 27

# Configuración de los rangos
MIN_DUTY = 40
MAX_DUTY_XY = 135
MAX_DUTY_Z = 120

# Función para convertir grados a duty cycle para el servo X e Y
def grados_a_duty_xy(grados):
    if grados < 10:
        grados = 10
    elif grados > 170:
        grados = 170
    return MIN_DUTY + (MAX_DUTY_XY - MIN_DUTY) * (grados - 0) / 180

# Función para convertir grados a duty cycle para el servo Z
def grados_a_duty_z(grados):
    if grados < 5:
        grados = 5
    elif grados > 25:
        grados = 25
    return MIN_DUTY + (MAX_DUTY_Z - MIN_DUTY) * (grados - 0) / 180

# Función para mover el servo X
def mover_servo_x(grados):
    duty = int(grados_a_duty_xy(grados))
    servo_x.duty(duty)
    print(f"Servo X movido a {grados} grados (duty: {duty})")

# Función para mover el servo Y
def mover_servo_y(grados):
    duty = int(grados_a_duty_xy(grados))
    servo_y.duty(duty)
    print(f"Servo Y movido a {grados} grados (duty: {duty})")

# Función para mover el servo Z
def mover_servo_z(grados):
    duty = int(grados_a_duty_z(grados))
    servo_z.duty(duty)
    print(f"Servo Z movido a {grados} grados (duty: {duty})")

# Función para mover los servos a las posiciones iniciales
def posicion_inicial():
    mover_servo_z(10)  # Levantar lápiz (Z en 10 grados)
    time.sleep(0.5)
    mover_servo_x(90)# Servo X en el centro (90 grados)
    time.sleep(0.5)
    mover_servo_y(150)  # Servo Y en 170 grados
    print("Posición inicial alcanzada")
    time.sleep(1)
    
#Solicitud de posiciones
#posicion x
def solicitar_posicion_x():
    while True:
        try:
            posicion_x = int(input("Ingrese la posición X de un rango de -80  a  80: "))

            if (-80) <= posicion_x <= 80:
                print(f"Posiciones válidas: X={posicion_x}")
                return posicion_x
            else:
                print("Error: Las posiciones deben estar entre -80 y 80. Intente nuevamente.")
        except ValueError:
            print("Error: Ingrese un número válido.")
#posicion y
def solicitar_posicion_y():
    while True:
        try:
            posicion_y = int(input("Ingrese la posición Y de un rango de -80  a  80: "))

            if (-80) <= posicion_y <= 80:
                print(f"Posiciones válidas: Y={posicion_y}")
                posicion_y= -(posicion_y)
                return posicion_y
            else:
                print("Error: Las posiciones deben estar entre -80 y 80. Intente nuevamente.")
        except ValueError:
            print("Error: Ingrese un número válido.")
            
def longitud_cuadrados():
    while True:
        try:
            numero = int(input("Ingrese un número mayor que 0 y menor o igual a 80 "))
            
            # Verificamos que el número sea mayor a 0, par, y que sumado a 90 no supere 170
            if numero > 0 and numero % 2 == 0 and (numero + 90) <= 170:
                print(f"Número válido: {numero}")
                return numero
            else:
                print("Error: El número debe ser mayor a 0 y menor o igual a 80")
        except ValueError:
            print("Error: Ingrese un número válido.")

#FIGURAS
#lINEAS
def dibujar_linea():
    led2.value(1)
    print('Determine el primer punto: ')
    p_x1 = solicitar_posicion_x()
    p_y1 = solicitar_posicion_y()
    print('Determine el segundo Punto: ')
    p_x2 = solicitar_posicion_x()
    p_y2 = solicitar_posicion_y()
    time.sleep(1)
    
    led2.value(0)
    led3.value(1)
    
    mover_servo_x(90 + p_x1)
    mover_servo_y(90 + p_y1)
    time.sleep(1)
    mover_servo_z(26)
    time.sleep(1)
    mover_servo_x(90 + p_x2)
    mover_servo_y(90 + p_y2)
    time.sleep(1)
    led2.value(1)
    led3.value(0)
    posicion_inicial()
    

 
    
#Cuadrado
def cuadrado():
    mover_servo_x(90)
    time.sleep(1)
    mover_servo_y(90)
    time.sleep(1)
    longitud = longitud_cuadrados()
    mover_servo_y(90-(longitud/2))
    time.sleep(1)
    mover_servo_z(26)
    time.sleep(1)
    mover_servo_x(90+(longitud/2))
    time.sleep(1)
    mover_servo_y(90-(longitud/2)+longitud)
    time.sleep(1)
    mover_servo_x(90+(longitud/2)-longitud)
    time.sleep(1)
    mover_servo_y(90+(longitud/2)-longitud)
    time.sleep(1)
    mover_servo_x(90)
    time.sleep(1)
    posicion_inicial()
    time.sleep(1)
    
while True:
    print("¿Qué deseas hacer?")
    print("1. Dibujar una línea")
    print("2. Dibujar un cuadrado")
    eleccion = input("Elige una opción (1 o 2): ")
    
    if eleccion == "1":
        dibujar_linea()
    elif eleccion == "2":
        cuadrado()
    else:
        print("Opción no válida, intenta de nuevo.")
