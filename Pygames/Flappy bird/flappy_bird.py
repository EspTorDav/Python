import pygame
from pygame.locals import *
import random


pygame.init()

#Ventana
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Flappy bird')

#Fuentes
font = pygame.font.SysFont('Bauhaus 93', 60)

#Colores
white = (255, 255, 255)

#Variables de juego
screen_scroll = 0
scroll_speed = 4
clock = pygame.time.Clock()
fps = 60
flying = False
game_over = False
pipe_gap = 150
pipe_freq = 1500#milisegundos
last_pipe = pygame.time.get_ticks() - pipe_freq
score = 0
pass_pipe = False

#Carga de imagenes
bg = pygame.image.load('img/bg.png')
ground_img = pygame.image.load('img/ground.png')
button_img = pygame.image.load('img/restart.png')

#Mostrar textos
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#Funcion reset
def reset_game():
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    return score 


#CLASES

#Clase del pajaro
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'img/bird{num}.png')
            self.images.append(img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):

        if flying == True:
        #Gravedad
            self.vel += 0.5
            if self.vel > 8:
               self.vel = 8
            if self.rect.bottom < 768:
               self.rect.y += int(self.vel)
 
        if game_over == False:

            #Salto
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            #Gestion de animacion del pájaro
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            #Rotacion del pájaro
            self.image = pygame.transform.rotate(self.images[self.index], - 2 *self.vel)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], - 90)


class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position) :
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('img/pipe.png')
        self.rect = self.image.get_rect()
        self.rect.topleft = [x,y]
        #position 1 es desde arriba, position -1 es desde abajo
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap /2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]
    
    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image) :
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):

        action = False

        pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True


        screen.blit(self.image, (self.rect.x, self.rect.y))

        return action

        
#GRUPOS DE SPRITES
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

#INSTANCIAS
flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)
button = Button(screen_width //2 - 50, screen_height // 2 - 100, button_img)



#GAME LOOP
run = True
while run:

    screen.blit(bg, (0,0))
    fps_clock = clock.tick(fps)

    #Dibujo de grupos de sprites
    bird_group.draw(screen)
    pipe_group.draw(screen)
    bird_group.update()
    

    #Dibujar y hacer scroll con el suelo
    screen.blit(ground_img, (screen_scroll, 768 )) 

    #Comprobar marcador
    if len(pipe_group) > 0:
        if bird_group.sprites()[0]. rect.left > pipe_group.sprites()[0].rect.left\
           and bird_group.sprites()[0]. rect.right < pipe_group.sprites()[0].rect.right\
           and pass_pipe == False:
           pass_pipe = True
        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
               score += 1
               pass_pipe = False


    draw_text(str(score), font, white, int(screen_width / 2), 40)          

            
        


    #Colisiones pajaro-tubo
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False) or flappy.rect.top < 0:
        game_over = True

    #Comprobar si el pájaro está en el suelo
    if flappy.rect.bottom > 768:
        game_over = True
        flying = False

    if game_over == False and flying == True:
        #Generacion de tubos
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_freq:
            pipe_height = random.randint(-100,100) 
            btm_pipe = Pipe(screen_width,int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width,int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now
            
        #Scroll de la pantalla
        screen_scroll -= scroll_speed
        if abs(screen_scroll) > 35:
           screen_scroll = 0
        
        pipe_group.update()
    
    #Comprobar game over y reiniciar
    if game_over == True:
        draw_text('PULSA PARA COMENZAR', font, white, screen_width / 7, screen_height / 2 - 200)
        if button.draw() == True:
            game_over = False
            score = reset_game()


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and flying == False and game_over == False:
            flying = True
    
    pygame.display.update()

pygame.quit()