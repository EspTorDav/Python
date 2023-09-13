#JUEGO CLÄSICO DE PINGPONG

import pygame
from pygame.locals import *
from pygame import mixer

pygame.init()
mixer.init()

#Definir variables de pantalla de juego
screen_width = 600
screen_height = 500

fpsClock = pygame.time.Clock()
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Ping Pong')

#Definir fuentes
font = pygame.font.SysFont('Constantia', 30)

#Definir variables del juego
live_ball = False
margin = 50
player_score = 0
cpu_score = 0
fps = 60
winner = 0
speed_increase = 0

#Definir colores
bg = (50,25,50)
white = (255,255,255)

#Definir sonidos
sonido_pala = mixer.Sound('sonido_pala.mp3')
victoria = mixer.Sound('victoria.mp3')
derrota = mixer.Sound('derrota.mp3')

#Método para colorear la ventana
def draw_board():
    screen.fill(bg)
    pygame.draw.line(screen,white,(0,margin),(screen_width,margin),3)

#Método para mostrar texto
def draw_text(text,font,text_col,x,y):
    img = font.render(text,True,text_col)
    screen.blit(img,(x,y))

#Clase para las barras de los jugadores
class paddle ():
    #Creador de instancias de barras
    def __init__(self,x,y):
        self.x = x
        self.y = y
        self.rect = Rect(self.x, self.y ,20 ,100)
        self.speed = 5
    
    #Funcion que determina el movimiento vertical
    def move(self):
        key = pygame.key.get_pressed()
        
        if key[pygame.K_UP] and self.rect.top > margin:
            self.rect.move_ip(0, -1*self.speed)
        if key[pygame.K_DOWN] and self.rect.bottom < screen_height:
            self.rect.move_ip(0, self.speed)
    
    #Funcion que mueve la barra de la cpu
    def ai(self):
        if self.rect.centery < game_ball.rect.top and self.rect.bottom < screen_height:
            self.rect.move_ip(0,self.speed)
        if self.rect.centery > game_ball.rect.bottom and self.rect.top > margin:
            self.rect.move_ip(0,-1*self.speed)
        



    
    #Funcion que dibuja las barras
    def draw_paddles(self):
        pygame.draw.rect(screen,white,self.rect)

class ball():
    #Creador de instancias de bola
    def __init__(self,x,y):
        self.reset(x,y)

    #Función que mueve la bola
    def move(self):

        if self.rect.top < margin:
            self.speed_y *=-1
        if self.rect.bottom > screen_height:
            self.speed_y *=-1
        if self.rect.left < 0:
            self.winner = 1   
        if self.rect.right > screen_width:
            self.winner = -1
        if self.rect.colliderect(player_paddle) or self.rect.colliderect(cpu_paddle):
            self.speed_x *=-1
            mixer.Sound.play(sonido_pala,0,0,0)
            
          

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        return self.winner
    
    
    #Funcion que dibuja la bola
    def draw_ball(self):
        pygame.draw.circle(screen,white,(self.rect.x + self.radius, self.rect.y + self.radius),self.radius)

    #Funcion que reinicia el juego, mediante el reinicio de la bola
    def reset(self,x,y):
        self.x = x
        self.y = y
        self.radius = 8
        self.rect = Rect(self.x, self.y ,self.radius*2 ,self.radius*2)
        self.speed_x = -4
        self.speed_y = 4
        self.winner = 0  # 1 indica que el jugador anota, -1 indica que la cpu anota



#Crear barras de jugadores
player_paddle = paddle(screen_width - 40, screen_height//2)
cpu_paddle = paddle(20, screen_height//2)

#Crear bola
game_ball = ball(screen_width-60,screen_height//2 + 50)



#Game loop
run = True
while run:

    fpsClock.tick(fps)

    draw_board()
    draw_text('CPU: ' + str(cpu_score),font,white,20,15)
    draw_text('P1: ' + str(player_score),font,white,screen_width - 100,15)
    draw_text('Velocidad de la bola: ' + str(abs(game_ball.speed_x)),font,white,screen_width//2 - 150,15)

    player_paddle.draw_paddles()
    cpu_paddle.draw_paddles()

    if live_ball == True:
        speed_increase += 1
        winner =  game_ball.move()
        if winner == 0:
            player_paddle.move()
            cpu_paddle.ai()
            game_ball.draw_ball()
        else:
            live_ball = False
            if winner == 1:
                player_score += 1
                mixer.Sound.play(victoria)
            elif winner == -1:
                cpu_score += 1
                mixer.Sound.play(derrota)

    if live_ball == False:
        if winner == 0:
           draw_text('Pulsa para iniciar',font,white, 190, screen_height // 2 -100)
        if winner == 1:
            draw_text('Punto para el jugador',font,white,160,screen_height // 2 -100)
            draw_text('Pulsa para iniciar',font,white,190,screen_height // 2)       
        if winner == -1:
            draw_text('Punto para la máquina',font,white,160,screen_height // 2 -100)
            draw_text('Pulsa para iniciar',font,white,190,screen_height // 2)
            
        

    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and live_ball == False:
            live_ball = True
            game_ball.reset(screen_width-60, screen_height//2 + 50)

    if speed_increase > 500:
        speed_increase = 0
        if game_ball.speed_x < 0:
          game_ball.speed_x -=1
        if game_ball.speed_x > 0:
          game_ball.speed_x +=1
        if game_ball.speed_y < 0:
          game_ball.speed_y -=1
        if game_ball.speed_y > 0:
          game_ball.speed_y +=1
    
    pygame.display.update()
        
pygame.quit()