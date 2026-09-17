#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Button
from pybricks.media.ev3dev import ImageFile
from pybricks.tools import wait, StopWatch

#Inicialização
ev3 = EV3Brick()

#Motor médio (Medium)
motor_garra = Motor(Port.A)
#Motores grandes (Large)
motor_elevacao = Motor(Port.B)
motor_rotacao = Motor(Port.D)

#Sensor de toque, detecta posição inicial da base
toque_rotacao = TouchSensor(Port.S2)

#Sensor de cor, detecta posição inicial do braço
sensor_elevacao = ColorSensor(Port.S3)

#Parâmetros
VELOCIDADE = 300
VELOCIDADE_CALIBRACAO = 200
LIMITE_TORQUE_GARRA = 50
LIMIAR_REFLEXAO_ELEVACAO = 10
ELEVACAO_MAX_CIMA = 120
ELEVACAO_MAX_BAIXO = 200
ANGULO_ABERTURA = 90
LIMITE_BUSCA_ROTACAO = 90
CALIBRACAO_TIMEOUT_MS = 5000

def fechar_garra():
    #Fecha garra até travar e zera nesse ponto
    motor_garra.run_until_stalled(-200, then=Stop.HOLD, duty_limit=LIMITE_TORQUE_GARRA)
    motor_garra.reset_angle(0)

def abrir_garra():
    #Abre garra a partir do ponto fechado
    motor_garra.run_target(VELOCIDADE, ANGULO_ABERTURA, Stop.HOLD)

def mover_elevacao(angulo):
    #Move braço para ângulo alvo
    angulo = max(-ELEVACAO_MAX_CIMA, min(angulo, ELEVACAO_MAX_BAIXO))
    motor_elevacao.run_target(VELOCIDADE, angulo, Stop.HOLD)

def parar_tudo():
    #Para todos os motores
    motor_garra.stop()
    motor_elevacao.stop()
    motor_rotacao.stop()

def calibrar():
    #Calibra rotação da base pelo sensor de toque, girando pouco pra cada lado
    motor_rotacao.reset_angle(0)
    cronometro = StopWatch()
    motor_rotacao.run(-VELOCIDADE_CALIBRACAO)
    while not toque_rotacao.pressed() and abs(motor_rotacao.angle()) < LIMITE_BUSCA_ROTACAO and cronometro.time() < CALIBRACAO_TIMEOUT_MS:
        wait(10)
    motor_rotacao.stop(Stop.BRAKE)
    if not toque_rotacao.pressed():
        motor_rotacao.run(VELOCIDADE_CALIBRACAO)
        while not toque_rotacao.pressed() and abs(motor_rotacao.angle()) < LIMITE_BUSCA_ROTACAO and cronometro.time() < CALIBRACAO_TIMEOUT_MS:
            wait(10)
        motor_rotacao.stop(Stop.BRAKE)
    if not toque_rotacao.pressed():
        motor_rotacao.run_target(VELOCIDADE_CALIBRACAO, 0, Stop.BRAKE)
    motor_rotacao.reset_angle(0)

    #Calibra elevação do braço pelo sensor de cor
    motor_elevacao.reset_angle(0)
    cronometro = StopWatch()
    motor_elevacao.run(-VELOCIDADE_CALIBRACAO)
    while sensor_elevacao.reflection() > LIMIAR_REFLEXAO_ELEVACAO and abs(motor_elevacao.angle()) < ELEVACAO_MAX_CIMA and cronometro.time() < CALIBRACAO_TIMEOUT_MS:
        wait(10)
    motor_elevacao.stop(Stop.BRAKE)
    if sensor_elevacao.reflection() > LIMIAR_REFLEXAO_ELEVACAO:
        motor_elevacao.run_target(VELOCIDADE_CALIBRACAO, 0, Stop.BRAKE)
    motor_elevacao.reset_angle(0)

#Programa principal
calibrar()

garra_fechada = False
ev3.screen.draw_circle(89, 64, 40, fill=garra_fechada)

while True:
    pressionados = ev3.buttons.pressed()

    #Sobe braço enquanto limite não é atingido
    if Button.UP in pressionados and motor_elevacao.angle() > -ELEVACAO_MAX_CIMA:
        motor_elevacao.run(-VELOCIDADE)
        ev3.screen.load_image(ImageFile.FORWARD)
    #Desce braço enquanto limite não é atingido
    elif Button.DOWN in pressionados and motor_elevacao.angle() < ELEVACAO_MAX_BAIXO:
        motor_elevacao.run(VELOCIDADE)
        ev3.screen.load_image(ImageFile.BACKWARD)
    else:
        motor_elevacao.stop(Stop.BRAKE)

    #Gira base para esquerda enquanto pressionado
    if Button.LEFT in pressionados:
        motor_rotacao.run(-VELOCIDADE)
        ev3.screen.load_image(ImageFile.LEFT)
    #Gira base para direita enquanto pressionado
    elif Button.RIGHT in pressionados:
        motor_rotacao.run(VELOCIDADE)
        ev3.screen.load_image(ImageFile.RIGHT)
    else:
        motor_rotacao.stop()

    #Alterna abrir/fechar garra
    if Button.CENTER in pressionados:
        if garra_fechada:
            abrir_garra()
            ev3.screen.clear()
            ev3.screen.draw_circle(89, 64, 40, fill=False)
        else:
            fechar_garra()
            ev3.screen.clear()
            ev3.screen.draw_circle(89, 64, 40, fill=True)
        garra_fechada = not garra_fechada
        while Button.CENTER in ev3.buttons.pressed():
            wait(10)

    wait(20)