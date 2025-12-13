from machine import Pin, PWM, Timer
from math import pi, cos, sin, radians
import time

# ---------------------------------------------------------
# FUNCIÓN PARA ÁNGULO
# ---------------------------------------------------------
def angle_to_duty(angle):
    return int((angle / 180) * 102 + 26)

def set_servo_angle(servo, angle):
    angle = max(0, min(180, angle))
    servo.duty(angle_to_duty(angle))

# ---------------------------------------------------------
# PARÁMETROS DE COORDENADAS Y ÁNGULOS
# ---------------------------------------------------------
X_ANGULO_INICIAL = 180
X_ANGULO_FINAL = 120
X_COORD_MAX = 65

Y_ANGULO_MIN = 5
Y_ANGULO_MAX = 180
Y_COORD_MIN = -40
Y_COORD_MAX = 40

def coord_x_a_angulo(x):
    ang = X_ANGULO_INICIAL - (x / X_COORD_MAX) * (X_ANGULO_INICIAL - X_ANGULO_FINAL)
    return min(max(ang, X_ANGULO_FINAL), X_ANGULO_INICIAL)

def coord_y_a_angulo(y):
    ang = Y_ANGULO_MIN + ((y - Y_COORD_MIN) / (Y_COORD_MAX - Y_COORD_MIN)) * (Y_ANGULO_MAX - Y_ANGULO_MIN)
    return min(max(ang, Y_ANGULO_MIN), Y_ANGULO_MAX)

# ---------------------------------------------------------
# CONFIGURACIÓN DE SERVOS
# ---------------------------------------------------------
servo_x = PWM(Pin(27), freq=50)
servo_y = PWM(Pin(12), freq=50)
servo_z = PWM(Pin(14), freq=50)

z_angle = 20
set_servo_angle(servo_z, z_angle)

# ---------------------------------------------------------
# LEDS
# ---------------------------------------------------------
LED_rojo = Pin(15, Pin.OUT)
LED_amarillo = Pin(2, Pin.OUT)
LED_azul = Pin(4, Pin.OUT)

# ---------------------------------------------------------
# FUNCIONES SERVO Z
# ---------------------------------------------------------
def pluma_arriba():
    global z_angle
    while z_angle > 20:
        z_angle -= 1
        set_servo_angle(servo_z, z_angle)
        time.sleep(0.07)

def pluma_abajo():
    global z_angle
    while z_angle < 50:
        z_angle += 1
        set_servo_angle(servo_z, z_angle)
        time.sleep(0.07)

# ---------------------------------------------------------
# MOVIMIENTO EN LÍNEA
# ---------------------------------------------------------
def mover_linea(x1, y1, x2, y2, pasos=150):
    dx = (x2 - x1) / pasos
    dy = (y2 - y1) / pasos
    for i in range(pasos + 1):
        xt = x1 + dx * i
        yt = y1 + dy * i
        set_servo_angle(servo_x, coord_x_a_angulo(xt))
        set_servo_angle(servo_y, coord_y_a_angulo(yt))
        time.sleep(0.01)

# ---------------------------------------------------------
# FIGURA DE LISSAJOUS
# ---------------------------------------------------------
A = 50
B = 50
phase = pi / 2
t = 0.0
dt = 0.01
running_lissajous = False
contador_pasos = 0
total_pasos = 0
X_MIN = 0
X_MAX = 180
Y_MIN = 0
Y_MAX = 180

timer_lissajous = Timer(0)

def update_lissajous(timer):
    LED_rojo.value(0)
    LED_amarillo.value(1)
    global t, contador_pasos, running_lissajous, pos_x, pos_y, fx, fy

    if not running_lissajous or contador_pasos >= total_pasos:
        running_lissajous = False
        timer.deinit()
        pluma_arriba()
        LED_amarillo.value(0)
        LED_azul.value(1)
        mover_linea(pos_x, pos_y, 0, 0)
        pos_x, pos_y = 0, 0
        LED_azul.value(0)
        LED_rojo.value(1)
        return

    x = 120 + A * cos(2 * pi * fx * t)
    y = 90 + B * sin(2 * pi * fy * t)

    set_servo_angle(servo_x, max(X_MIN, min(X_MAX, x)))
    set_servo_angle(servo_y, max(Y_MIN, min(Y_MAX, y)))

    t += dt
    contador_pasos += 1

# ---------------------------------------------------------
# CÁLCULO DE TIEMPO PARA COMPLETAR FIGURA
# ---------------------------------------------------------
def tiempo_figura(fx, fy):
    T_x = 1 / fx
    T_y = 1 / fy
    return max(T_x + 3, T_y + 3)

# ---------------------------------------------------------
# ESPIRAL FIBONACCI 
# ---------------------------------------------------------
def trazo_espiral(max_elementos=13, escala_radio=0.9, paso_angular=2):
   
    fib = [0, 1]
    while len(fib) < max_elementos:
        fib.append(fib[-1] + fib[-2])

    fib = [f for f in fib if f > 0 and f * escala_radio <= X_COORD_MAX]
    if not fib:
        fib = [1, 2, 3, 5]

    global pos_x, pos_y
    cx, cy = 50, 0	         # Centro razonable
    angle_base = 0         # Ángulo acumulado (grados)

    LED_amarillo.value(1)
    pluma_arriba()
    mover_linea(pos_x, pos_y, cx, cy)   
    pos_x, pos_y = cx, cy
    pluma_abajo()

    for r in fib:
        radio = r * escala_radio 
        for ang in range(0, 90 + 1, paso_angular):
            angle_deg = angle_base + ang
            ang_rad = radians(angle_deg)
            xt = cx + radio * cos(ang_rad)
            yt = cy + radio * sin(ang_rad)

            xt = max(0, min(X_COORD_MAX, xt))
            yt = max(Y_COORD_MIN, min(Y_COORD_MAX, yt))

            set_servo_angle(servo_x, coord_x_a_angulo(xt))
            set_servo_angle(servo_y, coord_y_a_angulo(yt))

            pos_x, pos_y = xt, yt

            time.sleep(0.015)

        angle_base += 90

    pluma_arriba()
    LED_amarillo.value(0)


# ---------------------------------------------------------
# PROGRAMA PRINCIPAL
# ---------------------------------------------------------
pos_x, pos_y = 0, 0
set_servo_angle(servo_x, coord_x_a_angulo(pos_x))
set_servo_angle(servo_y, coord_y_a_angulo(pos_y))
pluma_arriba()

try:
    while True:
        print("\n=== MENU ===")
        print("1. Trazar línea")
        print("2. Figura de Lissajous")
        print("3. Espiral Fibonacci")
        opcion = input("Seleccione opción: ")

        if opcion == "1":
            running_lissajous = False
            LED_rojo.value(1)

            print("➡ Coordenada inicial")
            while True:
                x1 = int(input(f"x1 (0 a {X_COORD_MAX}): "))
                y1 = int(input(f"y1 ({Y_COORD_MIN} a {Y_COORD_MAX}): "))
                if 0 <= x1 <= X_COORD_MAX and Y_COORD_MIN <= y1 <= Y_COORD_MAX:
                    break
                print("❌ ERROR: coordenadas inválidas")

            print("➡ Coordenada final")
            while True:
                x2 = int(input(f"x2 (0 a {X_COORD_MAX}): "))
                y2 = int(input(f"y2 ({Y_COORD_MIN} a {Y_COORD_MAX}): "))
                if 0 <= x2 <= X_COORD_MAX and Y_COORD_MIN <= y2 <= Y_COORD_MAX:
                    break
                print("❌ ERROR: coordenadas inválidas")

            LED_rojo.value(0)
            LED_amarillo.value(1)
            pluma_arriba()
            mover_linea(pos_x, pos_y, x1, y1)
            pos_x, pos_y = x1, y1
            pluma_abajo()
            mover_linea(x1, y1, x2, y2)
            pos_x, pos_y = x2, y2
            pluma_arriba()
            mover_linea(x2, y2, 0, 0)
            pos_x, pos_y = 0, 0
            LED_amarillo.value(0)
            LED_azul.value(1)
            print("✔ Trazo completado")
            time.sleep(2)
            LED_azul.value(0)
            LED_rojo.value(1)

        elif opcion == "2":
            print("Ingrese relación de frecuencias X:Y (naturales), máximo 4:4")
            while True:
                try:
                    n1, n2 = map(int, input("Relación X:Y = ").split(":"))
                    if 0 < n1 <= 4 and 0 < n2 <= 4:
                        break
                    print("❌ Valores inválidos")
                except:
                    print("❌ Formato inválido, ejemplo 1:2")

            f_base = 0.2
            fx = n1 * f_base
            fy = n2 * f_base
            tiempo_total = tiempo_figura(fx, fy)
            total_pasos = int(tiempo_total / dt)
            contador_pasos = 0
            pluma_abajo()
            t = 0.0
            running_lissajous = True
            timer_lissajous.init(freq=30, mode=Timer.PERIODIC, callback=update_lissajous)

        elif opcion == "3":
            running_lissajous = False
            LED_rojo.value(0)
            trazo_espiral()
            LED_azul.value(1)
            mover_linea(pos_x, pos_y, 0, 0)
            pos_x, pos_y = 0, 0
            LED_azul.value(0)
            LED_rojo.value(1)

        else:
            print("❌ Opción no válida")

except KeyboardInterrupt:
    pass

finally:
    try:
        timer_lissajous.deinit()
    except:
        pass
    servo_x.deinit()
    servo_y.deinit()
    servo_z.deinit()