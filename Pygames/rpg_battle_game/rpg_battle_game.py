import pygame
from pygame.locals import *
from pygame import mixer
import random
import button


pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
mixer.init()

#-----------------VENTANA---------------------------------------
bottom_panel = 150
screen_width = 800
screen_height = 400 + bottom_panel


screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('RPG Battle')

#------------------CARGA DE IMÁGENES----------------------------
#Imagen de fondo
bg_img = pygame.image.load('img/Background/background.png').convert_alpha()

#Imagen del panel
panel_img = pygame.image.load('img/Icons/panel.png').convert_alpha()

#Imagen de espada
sword_img = pygame.image.load('img/Icons/sword.png').convert_alpha()

#Imagen de pocion
potion_img = pygame.image.load('img/Icons/potion.png').convert_alpha()

#Imagen para reiniciar
restart_img = pygame.image.load('img/Icons/restart.png').convert_alpha()

#Imagenes de victoria y derrota
victory_img = pygame.image.load('img/Icons/victory.png').convert_alpha()
defeat_img = pygame.image.load('img/Icons/defeat.png').convert_alpha()


#------------------FUENTES----------------------------
font = pygame.font.SysFont('Times New Roman' , 26)

#------------------COLORES----------------------------
red =(255, 0, 0)
green = (0, 255, 0)

#------------------SONIDOS----------------------------


#------------------VARIABLES DE JUEGO----------------------------
clock = pygame.time.Clock()
fps = 60
current_fighter = 1
total_fighters = 3
action_cooldown = 0
action_wait_time = 90
attack = False
potion = False
potion_effect = 15
clicked = False
game_over = 0


#------------------FUNCIONES---------------------------------------------------------------
#Dibujar mapa
def draw_bg():
    screen.blit(bg_img, (0, 0))

#Dibujar panel
def draw_panel():
    screen.blit(panel_img, (0, screen_height - bottom_panel))
    #Mostrar stats de caballero
    draw_text(f'{knight.name} HP: {knight.hp}', font, red, 100, screen_height - bottom_panel + 10)
    for count, i in enumerate(bandit_list):
        #Mostrar nombre y salud
         draw_text(f'{i.name} ' +  f'{count + 1} HP: {i.hp}', font, red, 550, (screen_height - bottom_panel + 10) + count * 60)

#Dibujar textos
def draw_text(Text, font, text_col, x, y):
    img = font.render(Text, True, text_col)
    screen.blit(img, (x, y))




#------------------CLASES-----------------------------------------------------------
#clase luchador
class Fighter():
    def __init__(self, x, y, name, max_hp, strength, potions):
        self.name = name
        self.hp = max_hp
        self.max_hp = max_hp
        self.strength = strength
        self.start_potions = potions
        self.potions = potions
        self.alive = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0: Idle, 1:Ataque, 2:herido, 3:Muerto
        self.update_time = pygame.time.get_ticks()
        #Carga de imagenes Idle
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Idle/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        #Carga de imagenes para el ataque
        temp_list = []
        for i in range(8):
            img = pygame.image.load(f'img/{self.name}/Attack/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        #Carga de imagenes para el daño
        temp_list = []
        for i in range(3):
            img = pygame.image.load(f'img/{self.name}/Hurt/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)
        self.animation_list.append(temp_list)

        #Carga de imagenes para la muerte
        temp_list = []
        for i in range(10):
            img = pygame.image.load(f'img/{self.name}/Death/{i}.png')
            img = pygame.transform.scale(img, (img.get_width() * 3, img.get_height() * 3))
            temp_list.append(img)

        self.animation_list.append(temp_list)
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self):
        animation_cooldown = 100

        #Gestion de animaciones
        self.image = self.animation_list[self.action][self.frame_index]

        #Comprobar el tiempo que pasa desde la ultima actualizacion de frames
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index +=1
        # Al acabar la animacion, reiniciarla
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.idle()

    def idle(self):
        #Animacion idle
        self.action = 0
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def attack(self, target):
        #Hacer daño
        self.action = 1
        rand = random.randint(-5, 5)
        damage = self.strength + rand
        target.hp -= damage
        target.hurt()

        #Comprobar si el objetivo esta muerto
        if target.hp < 1:
            target.hp = 0
            target.alive = False
            target.death()
        damage_text = DamageText(target.rect.centerx, target.rect.y, str(damage), red)
        damage_text_group.add(damage_text)

        #Animacion de ataque
        self.action = 1
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def hurt(self):
        #Animacion para el daño
        self.action = 2
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def death(self):
        #Animacion para la muerte
        self.action = 3
        self.frame_index = 0
        self.update_time = pygame.time.get_ticks()

    def reset(self):
        self.alive = True
        self.potions = self.start_potions
        self.hp = self.max_hp
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()

    def draw(self):
        screen.blit(self.image, self.rect)
     
#Clase barra de salud
class HealthBar():
    def __init__(self, x, y, hp, max_hp):
        self.x = x
        self.y = y
        self.hp = hp
        self.max_hp = max_hp

    def draw(self, hp):
        #Comprobar el ratio de salud y actualizar en base a el
        self.hp = hp
        ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, red, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, green, (self.x, self.y, 150 * ratio, 20))
                         
#Clase texto de daño
class DamageText(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, colour):
        pygame.sprite.Sprite.__init__(self)
        self.image = font.render(damage, True, colour)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.counter = 0
    
    def update(self):
        #Mover texto de daño
        self.rect.y -= 1
        #Borrar texto de daño
        self.counter += 1
        if self.counter > 60:
            self.kill()


#-----------------INSTANCIAS--------------------------------------------------------
#Grupos de Sprites
damage_text_group = pygame.sprite.Group()

#Luchadores
knight = Fighter(200, 260, 'Knight' , 30 , 10 , 3 )
bandit1 = Fighter(550, 270, 'Bandit', 20, 6, 1)
bandit2 = Fighter(700, 270, 'Bandit', 20, 6, 1)
bandit_list = []
bandit_list.append(bandit1)
bandit_list.append(bandit2)

#Barras de salud
knight_health_bar = HealthBar(100, screen_height - bottom_panel + 40, knight.hp, knight.max_hp)
bandit1_health_bar = HealthBar(550, screen_height - bottom_panel + 40, bandit1.hp, bandit1.max_hp)
bandit2_health_bar = HealthBar(550, screen_height - bottom_panel + 100, bandit2.hp, bandit2.max_hp)

#Pociones
potion_button = button.Button(screen, 100, screen_height - bottom_panel + 70, potion_img, 64, 64)

#Reinicio
restart_button = button.Button(screen, 330, 120, restart_img, 120, 30)

#------------------GAME LOOP--------------------------------------------------------
run = True
while run:

    fps_clock = clock.tick(fps)

    #Dibujar mapa
    draw_bg()

    #Dibujar panel
    draw_panel()
    knight_health_bar.draw(knight.hp)
    bandit1_health_bar.draw(bandit1.hp)
    bandit2_health_bar.draw(bandit2.hp)

    #Dibujar y animar luchadores
    #Caballero
    knight.draw()
    knight.update()

    #Bandidos
    for bandit in bandit_list:
        bandit.draw()
        bandit.update()

    #Dibujar el texto de daño
    damage_text_group.update()
    damage_text_group.draw(screen)

    #Reiniciar variables de accion
    attack = False
    potion = False
    target = None

    #Mostrar espada al pasar por enemigo
    #Obtener posicion del raton y comprobar colision
    pygame.mouse.set_visible(True)
    pos = pygame.mouse.get_pos()
    for count, bandit in enumerate(bandit_list):
        if bandit.rect.collidepoint(pos):
        #ocultar cursor y mostrar espada
            pygame.mouse.set_visible(False)
            screen.blit(sword_img, pos)
            #Comprobar si se clicka en un bandido
            if clicked == True and bandit.alive == True:
                attack = True
                target = bandit_list[count]
    if potion_button.draw():
        potion = True
    #Numero de pociones restantes
    draw_text(str(knight.potions), font, red, 150, screen_height- bottom_panel + 70)

    #Accion de jugador
    if game_over == 0:
        if knight.alive == True:
            if current_fighter == 1:
                action_cooldown += 1
                if action_cooldown >= action_wait_time:
                    if attack == True and target != None:
                        knight.attack(target)
                        current_fighter += 1
                        action_cooldown = 0
                    #Efecto de pociones
                    if potion == True:
                        if knight.potions > 0:
                            if knight.max_hp - knight.hp > potion_effect:
                                heal_amount = potion_effect
                            else: 
                                heal_amount = knight.max_hp - knight.hp
                            knight.hp += heal_amount
                            knight.potions -= 1
                            damage_text = DamageText(knight.rect.centerx, knight.rect.y, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
        else:
            game_over = -1

        #Acción enemiga
        for count, bandit in enumerate(bandit_list):
            if current_fighter == 2 + count:
                if bandit.alive == True:
                    action_cooldown +=1
                    if action_cooldown >= action_wait_time:
                        #Comprobar salud
                        if (bandit.hp / bandit.max_hp) < 0.5 and bandit.potions > 0:
                            if bandit.max_hp - bandit.hp > potion_effect:
                                heal_amount = potion_effect
                            else: 
                                heal_amount = bandit.max_hp - bandit.hp
                            bandit.hp += heal_amount
                            bandit.potions -= 1
                            damage_text = DamageText(bandit.rect.centerx, bandit.rect.y, str(heal_amount), green)
                            damage_text_group.add(damage_text)
                            current_fighter += 1
                            action_cooldown = 0
                        else:
                            #Atacar
                            bandit.attack(knight)
                            current_fighter += 1
                            action_cooldown = 0
                else:
                    current_fighter += 1
        
        #Cuando todos atacan, se reinician los turnos
        if current_fighter > total_fighters:
            current_fighter = 1

    #Comprobar que todos los bandidos están muertos
    alive_bandits = 0
    for bandit in bandit_list:
        if bandit.alive == True:
            alive_bandits += 1
    if alive_bandits == 0:
        game_over = 1

    #Comprobar que el juego se ha acabado
    if game_over != 0:
        if game_over == 1:
            screen.blit(victory_img, (250, 50))
        if game_over == -1:
            screen.blit(defeat_img, (290, 50))
        if restart_button.draw():
            knight.reset()
            for bandit in bandit_list:
                bandit.reset()
            current_fighter = 1
            action_cooldown = 0
            game_over = 0
        
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            clicked = True
        else:
            clicked = False
    
    pygame.display.update()

pygame.quit()