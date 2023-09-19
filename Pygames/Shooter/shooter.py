import pygame
import os
import random
import csv
import button
from pygame import mixer

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
mixer.init()

#Ventana
screen_width = 800
screen_height = int(screen_width * 0.8)
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Shooter')

#Variables de juego
clock = pygame.time.Clock()
scroll_thresh = 200
screen_scroll = 0
bg_scroll = 0
fps = 60
gravity = 0.75
level = 1
max_levels = 1
rows = 16
cols = 150
tile_size = screen_height // rows
tile_types = 21
start_game = False
start_intro = False


#Carga de imágenes
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha()
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha()

bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    'Health' : health_box_img,
    'Ammo'   : ammo_box_img,
    'Grenade': grenade_box_img
}

img_list = []
for x in range(tile_types):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (tile_size, tile_size))
    img_list.append(img)

#Fuentes
font = pygame.font.SysFont('Futura' , 30)

#Colores
white =(255, 255, 255)
blue = (0, 0, 255)
red = (255, 0 ,0)
green = (0 ,255, 0)
black = (0, 0, 0)
pink = (235, 65, 54)
bg_col = (144, 201, 120)

#Carga de sonidos
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1, 0.0, 5000)
jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)

#Variables de jugador
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False


#------------------FUNCIONES---------------------------------------------------------------
def draw_bg():
    screen.fill(bg_col)
    width = sky_img.get_width()
    for x  in range(5):
        screen.blit(sky_img, ((x * width) - bg_scroll * 0.5, 0))
        screen.blit(mountain_img, ((x * width) - bg_scroll * 0.6, screen_height - mountain_img.get_height() - 300))
        screen.blit(pine1_img, ((x * width) - bg_scroll * 0.7, screen_height - mountain_img.get_height() - 150))
        screen.blit(pine2_img, ((x * width) - bg_scroll * 0.8, screen_height - mountain_img.get_height()))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    decoration_group.empty()
    water_group.empty()
    item_box_group.empty()
    exit_group.empty()

    #Crear lista vacia de bloques
    data = []
    for row in range (rows):
        r = [-1] * cols
        data.append(r)
    return data

#------------------CLASES-----------------------------------------------------------
#Clase soldado para los personajes
class Soldier(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.speed = speed
        self.ammo = ammo
        self.start_ammo = ammo
        self.shoot_cooldown = 0
        self.grenades = grenades
        self.health = 100
        self.max_health = self.health
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()
        self.scale = scale
        self.action = 0
        #Variables especificas de ai
        self.move_counter = 0
        self.vision = pygame.Rect(0, 0, 150, 20)
        self.idling = False
        self.idling_counter = 0

        #Carga de todas las animaciones
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation in animation_types:

            #Reinicio de lista temporal de imagenes
            temp_list = []

            #Contar número de archivos en la carpeta
            num_of_frames = len(os.listdir(f'img/{self.char_type}/{animation}'))

            for i in range(num_of_frames):
                image = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
                image = pygame.transform.scale(image, (int(image.get_width() * self.scale),int(image.get_height() * self.scale)))
                temp_list.append(image)
            self.animation_list.append(temp_list)
        
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
    
    def update(self):
        self.update_animation()
        self.check_alive()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def move(self, moving_left, moving_right):
        #Reiniciar variables de movimiento
        dx = 0
        dy = 0
        screen_scroll = 0

        #Movimiento a izda y dcha
        if moving_left:
           dx = -self.speed
           self.direction = -1
           self.flip = True
        if moving_right:
           dx = self.speed
           self.direction = 1
           self.flip = False   
        
        #Salto
        if self.jump and self.in_air == False:
            self.vel_y = -12
            self.jump = False
            self.in_air = True

        #Gravedad
        self.vel_y += gravity
        if self.vel_y > 10:
            self.vel_y
        dy += self.vel_y

        #Comprobar colision 
        for tile in world.obstacle_list:
            #Colisiones en el eje x
            if tile [1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
            #Si la ia choca contra un muro, se gira
                if self.char_type == 'enemy':
                  self.direction *= -1
                  self.move_counter = 0
            #Colisiones en el eje y
            if tile [1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                #Comprobar sobre el jugador / bajo obstaculos
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #Comprobar bajo el jugador / sobre obstaculos
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom

        #Colision con agua
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0

        #Colision con salida
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True
        
        #Comprobar si cae fuera del mapa
        if self.rect.bottom > screen_height:
            self.health = 0

        #Comprobacion de laterales de la ventana
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx > screen_width:
                dx = 0


        #Actualizar rectangulo de instancia
        self.rect.x += dx
        self.rect.y += dy 

        #Actualizar scroll basado en jugador
        if self.char_type == 'player':
            if (self.rect.right > screen_width - scroll_thresh and bg_scroll < world.level_length * tile_size)\
                 or (self.rect.left < scroll_thresh and bg_scroll > abs(dx)):
               self.rect.x -= dx 
               screen_scroll = -dx

        return screen_scroll, level_complete
    
    def shoot(self):
           if self.shoot_cooldown == 0 and self.ammo > 0:
                self.shoot_cooldown = 20
                bullet  = Bullet(self.rect.centerx + (0.75 * self.direction * self.rect.size[0]), self.rect.centery, self.direction)
                bullet_group.add(bullet)
                self.ammo -= 1 
                shot_fx.play()

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1, 200) == 1:
                self.update_action(0)
                self.idling = True
                self.idling_counter = 50
            #Comprobar si la ia está cerca del jugador
            if self.vision.colliderect(player.rect):
                #Para de correr y mira al jugador
                self.update_action(0)
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1
                    
                    #Actualizar vision ia
                    self.vision.center = (self.rect.centerx + 75 * self.direction , self.rect.centery)


                    if self.move_counter > tile_size:
                            self.direction *= -1
                            self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter <=0:
                        self.idling = False
        self.rect.x += screen_scroll

        

    def update_animation(self):
        #Actualizar animacion
        animation_cooldown = 100
        self.image = self.animation_list[self.action][self.frame_index]
        #Comprobar si pasa el suficiente tiempo desde la ultima actualizacion
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
            #Si se acaban las animaciones, reiniciar
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

    def update_action(self, new_action):
        #Comprobar si la accion nueva es distinta a la anterior
        if new_action != self.action:
            self.action = new_action
            #Actualizar configuracion de animacion
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)

#Clase barra de salud
class Healthbar(pygame.sprite.Sprite):
    def __init__(self, x, y, health, max_health):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = self.health = health
        self.max_health = max_health

    def draw(self, health):
        #Actualizar nuevo daño
        self.health = health
        
        ratio = self.health /self.max_health
        pygame.draw.rect(screen, black, (self.x - 2, self.y - 2, 154, 24))
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))

#Clase balas 
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.direction = direction

    def update(self):
        #Move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll

        #Comprobar si la bala está fuera de ventana
        if self.rect.right < 0 or self.rect.left > screen_width:
            self.kill()

        #Comprobar colision con el mundo
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()

        #Colision con personajes
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive:
               player.health -= 5
               self.kill() 
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive:
                    enemy.health -= 25
                    self.kill()

#Clase Mundo
class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
         self.level_length = len(data[0])
        #Iterar por cada valor en un archivo de datos
         for y, row in enumerate(data):
             for x, tile in enumerate(row):
                 if tile >= 0:
                     img = img_list[tile]
                     img_rect = img.get_rect()
                     img_rect.x = x * tile_size
                     img_rect.y = y * tile_size
                     tile_data = (img, img_rect)
                     if tile >= 0 and tile <= 8:
                         self.obstacle_list.append(tile_data)
                     elif tile >= 9 and tile <= 10:
                         water = Water(img, x * tile_size, y * tile_size)
                         water_group.add(water)
                     elif tile >= 11 and tile <= 14:
                         decoration = Decoration(img, x * tile_size, y * tile_size)
                         decoration_group.add(decoration)
                     elif tile == 15:
                         player = Soldier('player', x * tile_size, y * tile_size , 1.65, 5, 20 , 5)
                         health_bar = Healthbar(10, 10, player.health, player. health)
                     elif tile == 16:
                         enemy = Soldier('enemy', x * tile_size, y * tile_size , 1.65, 2, 20, 0)
                         enemy_group.add(enemy)
                     elif tile == 17:
                         item_box = ItemBox('Ammo', x * tile_size, y * tile_size)
                         item_box_group.add(item_box)
                     elif tile == 18:
                         item_box = ItemBox('Grenade', x * tile_size, y * tile_size)
                         item_box_group.add(item_box)
                     elif tile == 19:
                         item_box = ItemBox('Health', x * tile_size, y * tile_size)
                         item_box_group.add(item_box)
                     elif tile == 20:
                         exit = Exit(img, x * tile_size, y * tile_size)
                         exit_group.add(exit)
         return player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])
                         
#Clase decoracion 
class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

#Clase agua
class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

#Clase salida
class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))
    
    def update(self):
        self.rect.x += screen_scroll

#Clase objetos coleccionables 
class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + tile_size // 2, y + (tile_size - self.image.get_height()))

    def update(self):
        #Scroll 
        self.rect.x += screen_scroll
        #Comprobar si el jugador ha cogido el objeto
        if pygame.sprite.collide_rect(self,player):
            #Comprobar el tipo de objeto
            if self.item_type == 'Health':
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif self.item_type == 'Ammo':
                player.ammo += 15
            elif self.item_type == 'Grenade':
                player.grenades += 3
            self.kill()
            
#Clase granadas
class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.vel_y = - 10
        self.speed = 7
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.direction = direction  

    def update(self):
        self.vel_y += gravity
        dx = self.direction * self.speed
        dy = self.vel_y

        #Comprobar colision con el mundo
        for tile in world.obstacle_list:
            #Comprobar colision en eje x
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.speed
            #Colisiones en el eje y
            if tile [1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.speed = 0
                #Comprobar sobre la granada / bajo obstaculos
                if self.vel_y < 0:
                    self.vel_y = 0
                    dy = tile[1].bottom - self.rect.top
                #Comprobar bajo la granada / sobre obstaculos
                elif self.vel_y >= 0:
                    self.vel_y = 0
                    dy = tile[1].top - self.rect.bottom
            
        #Actualizar posicion de granada
        self.rect.x += dx + screen_scroll
        self.rect.y += dy

        #Cuenta atrás de explosiones
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #Hacer daño con la explosion a quien este cerca
            if abs(self.rect.centerx - player.rect.centerx) < tile_size * 2 and \
               abs(self.rect.centery - player.rect.centery) < tile_size * 2:
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < tile_size * 2 and \
                abs(self.rect.centery - enemy.rect.centery) < tile_size * 2:
                    enemy.health -= 50

#Clase explosiones
class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1, 6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            img = pygame.transform.scale(img, (int(img.get_width() * scale),int( img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0

    def update(self):
        #Scroll
        self.rect.x += screen_scroll
        explosion_speed = 4
        #Actualizar animacion de explosion
        self.counter += 1

        if self.counter >= explosion_speed:
            self.counter = 0
            self.frame_index += 1
            #Borrar explosion al acabar la animacion
            if self.frame_index >= len(self.images):
                self.kill()
            else:
                self.image = self.images[self.frame_index]
     
#clase para las transiciones entre pantallas
class ScreenFade():
    def __init__(self, direction, colour, speed):
        self.direction = direction
        self.colour = colour
        self.speed = speed
        self.fade_counter = 0

    def fade(self):
        fade_complete = False
        self.fade_counter += self.speed
        if self.direction == 1:
            pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, screen_width // 2, screen_height))
            pygame.draw.rect(screen, self.colour, (screen_width // 2 + self.fade_counter, 0, screen_width, screen_height))
            pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, screen_width, screen_height // 2))
            pygame.draw.rect(screen, self.colour, (0, screen_height // 2 + self.fade_counter, screen_width, screen_height // 2))
        if self.direction == 2: #Pantalla vertical cae abajo
            pygame.draw.rect(screen,self.colour, (0, 0, screen_width, 0 + self.fade_counter))
        if self.fade_counter >= screen_width:
            fade_complete = True
        
        return fade_complete
#-----------------INSTANCIAS--------------------------------------------------------
intro_fade = ScreenFade(1, black, 4)
death_fade = ScreenFade(2, pink, 4)

#Botones
start_button = button.Button(screen_width // 2 -130, screen_height // 2 - 150, start_img, 1)
exit_button = button.Button(screen_width // 2 -110, screen_height // 2 + 50, exit_img, 1)
restart_button = button.Button(screen_width // 2 -100, screen_height // 2 - 50, restart_img, 2)

#Grupos de sprites
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

#Crear una lista vacia de bloques
world_data = []
for row in range(rows):
    r = [-1] * cols
    world_data.append(r)

#Cargar datos de nivel y crear mundo
with open(f'level{level}_data.csv' , newline ='') as csvfile:
     reader = csv.reader(csvfile, delimiter= ',')
     for x, row in enumerate(reader):
         for y, tile in enumerate(row):
             world_data[x][y] = int(tile) 

world = World()
player, health_bar = world.process_data(world_data)


#------------------GAME LOOP--------------------------------------------------------
run = True
while run:

    fps_clock = clock.tick(fps)

    if start_game == False:
        #Dibujar menu
        screen.fill(bg_col)
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False

    else:

        #Dibujar fondo
        draw_bg()

        #Dibujar nivel
        world.draw()

        health_bar.draw(player.health)

        #Mostrar municion
        draw_text(f'Ammo: ', font, white, 10, 35)
        for x in range(player.ammo):
                screen.blit(bullet_img, (90 + (x * 10), 40))
        
        draw_text(f'Grenades: ', font, white, 10, 60)
        for x in range(player.grenades):
                screen.blit(grenade_img, (135 + (x * 15), 60))

        #Mostrar granadas
        draw_text(f'Grenades: ', font, white, 10, 60)

        #Actualizar y dibujar 
        player.update()
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()

        player.draw()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #Mostrar intro
        if start_intro == True:
           if intro_fade.fade():
               start_intro = False
               intro_fade.fade_counter = 0
        

        #Mover jugador y actualizar acciones
        if player.alive:
            if shoot == True:
                player.shoot()
            elif grenade == True and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.4 * player.direction * player.rect.size[0]),\
                            player.rect.top + 10, player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                player.grenades -= 1  
            if player.in_air:
                player.update_action(2) #2
            elif moving_left or moving_right:
                player.update_action(1) #1: Correr
            else:
                player.update_action(0) #0: Idle

            screen_scroll, level_complete = player.move(moving_left,moving_right)
            bg_scroll -= screen_scroll
            #Comprobar si el nivel se ha completado
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= max_levels:
                    with open(f'level{level}_data.csv' , newline ='') as csvfile:
                        reader = csv.reader(csvfile, delimiter= ',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile) 

        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f'level{level}_data.csv' , newline ='') as csvfile:
                        reader = csv.reader(csvfile, delimiter= ',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile) 

                    world = World()
                    player, health_bar = world.process_data(world_data)

    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        #Comprobacion de teclado
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                moving_left = True
            if event.key == pygame.K_d:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_q:
                grenade = True
            if event.key == pygame.K_w and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
        
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a:
                moving_left = False
            if event.key == pygame.K_d:
                moving_right = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False
            if event.key == pygame.K_SPACE:
                shoot = False
        
    pygame.display.update()

pygame.quit()