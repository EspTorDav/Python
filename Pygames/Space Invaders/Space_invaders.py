import pygame
import random
from pygame.locals import *
from pygame import mixer

pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()


#Variables de ventana
screen_width = 600
screen_height = 800

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Space Invaders')

#Carga de sonidos
explosion_fx = pygame.mixer.Sound('img/explosion.wav')
explosion_fx.set_volume(0.25)

explosion2_fx = pygame.mixer.Sound('img/explosion2.wav')
explosion2_fx.set_volume(0.25)

laser_fx = pygame.mixer.Sound('img/laser.wav')
laser_fx.set_volume(0.25)


#Definir variables de juego
fps = 60
clock = pygame.time.Clock()
rows = 5
cols = 5
alien_cooldown = 500 #milisegundos
last_alien_shot = pygame.time.get_ticks()
countdown = 3
last_count = pygame.time.get_ticks()
game_over = 0 # 0 es continua el juego, 1 es victoria, -1 es derrota

#Definir colores
red = (255,0,0)
green = (0,255,0)
white = ( 255, 255, 255)

#Definir fuentes
font30 = pygame.font.SysFont('Constantia', 30) 
font40 = pygame.font.SysFont('Constantia', 40)

#Cargar imagenes 
bg = pygame.image.load("img/bg.png")

#Función para dibujar el background
def draw_bg():
    screen.blit(bg,(0,0))

#Funcion para crear textos
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

#CLASES DEL JUEGO

#Clase de la nave jugador, hereda de la clase sprite
class spaceship(pygame.sprite.Sprite):
    def __init__(self, x, y,health):
        #Inicializa la clase
        pygame.sprite.Sprite.__init__(self)
        #Carga la imagen de la nave
        self.image = pygame.image.load('img/spaceship.png')
        #Genera un rect a partir de la imagen
        self.rect = self.image.get_rect()
        #Coloca el centro en las coordenadas
        self.rect.center = [x, y]
        #Declara la barra de salud inicial y restante
        self.health_start = health
        self.health_remaining = health
        self.last_shot = pygame.time.get_ticks()


    def update(self):
        #Establecer una velocidad de movimiento
        speed = 8
        #Establecer un cooldown entre disparos
        cooldown = 500 #ms
        game_over = 0

        #Gestor de eventos de teclas
        key = pygame.key.get_pressed()
        if key[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= speed
        if key[pygame.K_RIGHT] and self.rect.right < screen_width:
            self.rect.x += speed

        #Tiempo actual
        time_now = pygame.time.get_ticks()

        #Actualizar mask (Dibujo de cada pixel NO transparente)
        self.mask = pygame.mask.from_surface(self.image)

        #Balas
        if key[pygame.K_SPACE] and time_now - self.last_shot > cooldown:
            laser_fx.play()
            bullets = bullet(self.rect.centerx,self.rect.top)
            bullet_group.add(bullets)
            self.last_shot = time_now

        #Dibujar la barra de salud
        pygame.draw.rect(screen,red, (self.rect.x, (self.rect.bottom + 10), self.rect.width, 15))
        if self.health_remaining > 0:
            pygame.draw.rect(screen,green, (self.rect.x, (self.rect.bottom + 10), int(self.rect.width * (self.health_remaining / self.health_start)), 15))
        elif self.health_remaining <=0:
            explosions = explosion(self.rect.centerx, self.rect.centery, 3)
            explosion_group.add(explosions)
            self.kill()
            game_over = -1
        return game_over



#Clase de las balas, hereda de la clase sprite
class bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        #Inicializa la clase
        pygame.sprite.Sprite.__init__(self)
        #Carga la imagen de la spaceship
        self.image = pygame.image.load('img/bullet.png')
        #Genera un rect a partir de la imagen
        self.rect = self.image.get_rect()
        #Coloca el centro en las coordenadas
        self.rect.center = [x, y]
    

    #Funcion que actualiza las balas
    def update(self):
        self.rect.y -= 5
        if self.rect.bottom < 0:
            self.kill()
        if pygame.sprite.spritecollide(self,aliens_group,True, pygame.sprite.collide_mask):
            self.kill()
            explosion_fx.play()
            explosions = explosion(self.rect.centerx, self.rect.centery, 2)
            explosion_group.add(explosions)



#Clase de los alients, hereda de la clase sprite
class aliens(pygame.sprite.Sprite):
    def __init__(self, x, y):
        #Inicializa la clase
        pygame.sprite.Sprite.__init__(self)
        #Carga la imagen de la spaceship
        self.image = pygame.image.load('img/alien' + str(random.randint(1,5)) + '.png')
        #Genera un rect a partir de la imagen
        self.rect = self.image.get_rect()
        #Coloca el centro en las coordenadas
        self.rect.center = [x, y]
        self.direction = 1
        self.move_counter = 0
    
    def update(self):
        self.rect.x += self.direction
        self.move_counter += 1
        if abs(self.move_counter) > 75:
            self.direction *= -1
            self.move_counter *= self.direction

    #Actualizar mask (Dibujo de cada pixel NO transparente)
        self.mask = pygame.mask.from_surface(self.image)
        

#Clase de las balas de aliens, hereda de la clase sprite
class aliens_bullets(pygame.sprite.Sprite):
    def __init__(self, x, y):
        #Inicializa la clase
        pygame.sprite.Sprite.__init__(self)
        #Carga la imagen de la spaceship
        self.image = pygame.image.load('img/alien_bullet.png')
        #Genera un rect a partir de la imagen
        self.rect = self.image.get_rect()
        #Coloca el centro en las coordenadas
        self.rect.center = [x, y]
    

    #Funcion que actualiza las balas
    def update(self):
        self.rect.y += 2
        if self.rect.top > screen_height:
            self.kill()
        if pygame.sprite.spritecollide(self,spaceship_group,False,pygame.sprite.collide_mask):
            self.kill()
            explosion2_fx.play()
            spaceship_player.health_remaining -= 1
            explosions = explosion(self.rect.centerx, self.rect.centery, 1)
            explosion_group.add(explosions)
        

        
#Clase para explosiones
class explosion(pygame.sprite.Sprite):
    def __init__(self, x, y,size):
        #Inicializa la clase
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f'img/exp{num}.png')
            if size ==1:
                img = pygame.transform.scale(img,(20, 20))
            if size ==2:
                img = pygame.transform.scale(img,(40, 40))
            if size ==3:
                img = pygame.transform.scale(img,(160, 160))
            self.images.append(img)
        self.index = 0      
        #Carga la imagen de la explosion
        self.image = self.images[self.index]
        #Genera un rect a partir de la imagen
        self.rect = self.image.get_rect()
        #Coloca el centro en las coordenadas
        self.rect.center = [x, y]
        self.counter = 0
    
    def update(self):
        explosion_speed = 3
        self.counter += 1
        
        if self.counter >= explosion_speed and self.index < len(self.images) - 1:
            self.counter = 0
            self.index += 1
            self.image = self.images[self.index]

        #Cuando acaba la animación, se borra la explosion
        if self.index >= len(self.images) - 1 and self.counter >= explosion_speed:
            self.kill()
    


#Crear grupos de sprites
spaceship_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
aliens_group = pygame.sprite.Group()
aliens_bullets_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()


#Crear instancia de spaceship de jugador
spaceship_player = spaceship(int(screen_width /2), screen_height - 100, 3)
spaceship_group.add(spaceship_player)

def create_aliens():
    for row in range(rows):
        for item in range(cols):
            alien = aliens(100 + item * 100, 100 + row * 70)
            aliens_group.add(alien)

create_aliens()




#GAME LOOP
run = True
while run:

    #Dibujar background
    draw_bg()

    if countdown == 0:

        #Objeto reloj fps
        fps_clock = clock.tick(fps)

        #Crear balas de alien aleatorias
        time_now = pygame.time.get_ticks()
        if time_now - last_alien_shot > alien_cooldown and len(aliens_bullets_group) < 10 and len(aliens_group) > 0:
            attacking_alien = random.choice(aliens_group.sprites())
            alien_bullet = aliens_bullets(attacking_alien.rect.centerx,attacking_alien.rect.bottom)
            aliens_bullets_group.add(alien_bullet)
            last_alien_shot = time_now

        #Comprueba si no hay mas aliens
        if len(aliens_group) == 0:
            game_over = 1

        if game_over == 0:

            #Invocar la funcion que actualiza la spaceship
            game_over = spaceship_player.update()

            #Invocar la funcion que actualiza los grupos de sprites
            bullet_group.update()
            aliens_group.update()
            aliens_bullets_group.update()
        else:
            if game_over == -1:
                draw_text('GAME OVER!', font40 , white, int(screen_width / 2 - 110), int(screen_height / 2 + 50 ))
            if game_over == 1:
                draw_text('¡ HAS GANADO!', font40 , white, int(screen_width / 2 - 110), int(screen_height / 2 + 50 ))
    
    if countdown > 0:
        draw_text('¡PREPÁRATE!', font40 , white, int(screen_width / 2 - 110), int(screen_height / 2 + 50 ))
        draw_text(str(countdown), font40 , white, int(screen_width / 2 - 10), int(screen_height / 2 + 100 ))
        count_timer = pygame.time.get_ticks()
        if count_timer - last_count > 1000:
            countdown -= 1
            last_count = count_timer
    
    #Actualiza las animaciones
    explosion_group.update()
    
    #Dibujar grupo de sprites, el método lo proporciona la clase Sprite
    spaceship_group.draw(screen)
    bullet_group.draw(screen)
    aliens_group.draw(screen)
    aliens_bullets_group.draw(screen)
    explosion_group.draw(screen)

    #Gestor de eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()
pygame.quit()
