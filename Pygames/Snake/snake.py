import pygame
import random
import time
from pygame import mixer

pygame.init() #Inicializa métodos y funciones del módulo pygame
mixer.init()

#VENTANA DE JUEGO
screen = pygame.display.set_mode((600,500))
manzana = pygame.image.load('manzana.png')
manzana = pygame.transform.smoothscale(manzana,(10,10))
mixer.music.load('game_music.mp3')
mixer.music.play(-1)
pygame.display.set_caption('snake game') 


#VARIABLES DE LA SERPIENTE
snake_pos = [80,30] #Posicion inicial 
snake_speed = 10 #Velocidad inicial 
snake_body = [[80,30],[70,30]] #Cuerpo

dir = 'RIGHT' #Dirección inicial en el que se mueve la serpiente
next_dir = dir #Dirección que proporcionamos con las teclas

#Este objeto determina el framerate
clock = pygame.time.Clock() 

#VARIABLES DE LA COMIDA
food = True #Este booleano determinará cuando cambiar la comida de posición.
food_pos = [random.randrange(1, (600//10)) *10 ,random.randrange(1, (500//10)) *10] #Esto determina la posicion de la primera comida

score = 0 #Estado inicial de la puntuación

#Función que muestra la puntuación en pantalla
def show_score(): 
    font = pygame.font.SysFont('Georgia',30)
    Font = font.render('Score: ' + str(score),True,'red')
    rect = Font.get_rect()
    screen.blit(Font,rect)

#Función que determina el game over
def game_over(): #Funcion que determina el final del juego
    font = pygame.font.SysFont('Georgia',50)
    Font = font.render('GAME OVER Score: ' + str(score),True,'purple')
    rect = Font.get_rect()
    rect.midtop = (600/2,500/4)
    screen.blit(Font,rect)
    pygame.display.flip()
    game_over_sound = mixer.Sound('game_over.mp3')
    mixer.Sound.play(game_over_sound,0,0,1)
    time.sleep(2)
    pygame.quit()
    quit()

#GAME LOOP
while True:
    
    #DETECCIÓN DE TECLAS
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN: 
            if event.key == pygame.K_UP:
                next_dir = 'UP'
            if event.key == pygame.K_DOWN:
                next_dir = 'DOWN'
            if event.key == pygame.K_LEFT:
                next_dir = 'LEFT'
            if event.key == pygame.K_RIGHT:
                next_dir = 'RIGHT'
    
    #CONTROLAMOS EL CAMBIO DE POSICION DE LA SERPIENTE
    if dir == 'UP': 
        snake_pos[1] -= 10
    if dir == 'DOWN':
        snake_pos[1] += 10
    if dir == 'RIGHT':
        snake_pos[0] += 10
    if dir == 'LEFT':
        snake_pos[0] -= 10
    
    #CONTROLAMOS QUE NO SE SOLAPE LA SERPIENTE CON MOVIMIENTOS OPUESTOS
    if next_dir == 'UP' and dir !='DOWN': 
        dir = 'UP'
    if next_dir == 'DOWN' and dir !='UP':
        dir = 'DOWN'
    if next_dir == 'RIGHT' and dir !='LEFT':
        dir = 'RIGHT'
    if next_dir == 'LEFT' and dir !='RIGHT':
        dir = 'LEFT'
    
   
    #CONTROL SOBRE EL CRECIMIENTO DE LA SERPIENTE Y CAMBIO DE POSICION DE FRUTA
    snake_body.insert(0,list(snake_pos)) #Inserta en el cuerpo cada coordenada que atraviesa
    if snake_pos[0] == food_pos[0] and snake_pos[1] == food_pos[1]:
        score +=10
        food = False
        pickup_sound = mixer.Sound('pickup_object.mp3')
        mixer.Sound.play(pickup_sound,0,0,1)
        
        
        

    else:  #Si no se encuentra una fruta, el cuerpo insertado se elimina,manteniendo el tamaño de la serpiente
        snake_body.pop()
    
    if not food: #Si food toma el valor falso, es decir, la serpiente la toma, cambia su posicion
        food_pos = [random.randrange(1, (600//10)) *10, random.randrange(1, (500//10)) *10]
    
    food = True
    screen.fill('green')

    for pos in snake_body: #DIBUJAR LA SERPIENTE Y LAS FRUTAS
        pygame.draw.rect(screen,'darkblue',(pos[0],pos[1],10,10))
    #pygame.draw.circle(screen,'dark red',(food_pos[0],food_pos[1]),5)
    screen.blit(manzana,(food_pos[0],food_pos[1]))

    #CONDICIONES DE GAME OVER
    if snake_pos[0] < 0 or snake_pos[0] == 600: 
        game_over()
    if snake_pos[1] < 0 or snake_pos[1] == 500:
        game_over()
    for block in snake_body[1:]:
        if snake_pos[0] == block[0] and snake_pos[1] == block[1]:#La serpiente se muerde a si misma
            game_over()
    
    show_score()
    pygame.display.update() #Actualiza el juego mientras haya datos disponibles
    clock.tick(snake_speed)