import pygame
from pygame.locals import *
from pygame import mixer
from Fighter import Fighter

pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
mixer.init()

#Ventana
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH,SCREEN_HEIGHT))
pygame.display.set_caption('Brawler')

#Carga de imágenes
bg_image = pygame.image.load('assets/images/background/background.jpg').convert_alpha()
victory_img = pygame.image.load('assets/images/icons/victory.png').convert_alpha()

#Carga de spritesheets
warrior_sheet = pygame.image.load('assets/images/warrior/Sprites/warrior.png')
wizard_sheet = pygame.image.load('assets/images/wizard/Sprites/wizard.png')

#Definir número de sprites de cada animacion
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

#Fuentes
font_count = pygame.font.Font('assets/fonts/turok.ttf', 80)
font_score = pygame.font.Font('assets/fonts/turok.ttf', 30)

#Colores
WHITE =(255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)

#Carga de sonidos
pygame.mixer.music.load('assets/audio/music.mp3')
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1, 0.0, 5000)

sword_fx = pygame.mixer.Sound('assets/audio/sword.wav')
sword_fx.set_volume(0.5)
magic_fx = pygame.mixer.Sound('assets/audio/magic.wav')
magic_fx.set_volume(0.5)

#Variables de juego
clock = pygame.time.Clock()  #Objeto para marcar el framerate
FPS = 60
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]
round_over = False
ROUND_OVER_COOLDOWN = 2000

#Variables de luchador
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE ,WIZARD_SCALE, WIZARD_OFFSET]



#------------------FUNCIONES---------------------------------------------------------------
def draw_gb():
    scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    SCREEN.blit(scaled_bg, (0, 0))

def draw_health_bar(health, x, y):
    ratio = health / 100
    pygame.draw.rect(SCREEN, WHITE, (x - 2, y - 2, 404, 34))
    pygame.draw.rect(SCREEN, RED, (x, y, 400, 30))
    pygame.draw.rect(SCREEN, YELLOW, (x, y, 400 * ratio, 30))

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    SCREEN.blit(img, (x, y))
  
#-----------------INSTANCIAS--------------------------------------------------------
# Crear 2 instancias de la clase Fighter
fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
fighter_2 = Fighter(2, 700, 310, True,  WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)


#------------------GAME LOOP--------------------------------------------------------
run = True
while run:

    #Reloj que marca los FPS
    fps_clock = clock.tick(FPS)

    #Dibujo de fondo
    draw_gb()

    #Dibujo de barras de salud y marcadores
    draw_health_bar(fighter_1.health, 20, 20)
    draw_health_bar(fighter_2.health, 580, 20)
    draw_text('P1: ' + str(score[0]), font_score, RED, 20, 60)
    draw_text('P2: ' + str(score[1]), font_score, RED, 580, 60)

    #Actualizar cuenta atras
    if intro_count <= 0:
        #Movimiento de luchadores
        fighter_1.move(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN, fighter_2, round_over)
        fighter_2.move(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN, fighter_1, round_over)
    else:
        #Mostrar cuenta atras
        draw_text(str(intro_count), font_count, RED, SCREEN_WIDTH / 2 - 10, SCREEN_HEIGHT / 8)
        #Actualizar cuenta atras
        if (pygame.time.get_ticks() - last_count_update) >= 1000:
            intro_count -= 1
            last_count_update = pygame.time.get_ticks()

    #Dibujo de luchadores
    fighter_1.draw(SCREEN)
    fighter_2.draw(SCREEN)

    #Comprobar derrota de un jugador
    if round_over == False:
        if fighter_1.alive == False:
            score[1] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
        elif fighter_2.alive == False:
            score[0] += 1
            round_over = True
            round_over_time = pygame.time.get_ticks()
    else:
        SCREEN.blit(victory_img, (360, 150))
        if pygame.time.get_ticks() - round_over_time > ROUND_OVER_COOLDOWN:
            round_over = False
            intro_count = 3
            fighter_1 = Fighter(1, 200, 310, False, WARRIOR_DATA, warrior_sheet, WARRIOR_ANIMATION_STEPS, sword_fx)
            fighter_2 = Fighter(2, 700, 310, True,  WIZARD_DATA, wizard_sheet, WIZARD_ANIMATION_STEPS, magic_fx)

    #Actualizacion de animaciones
    fighter_1.update()
    fighter_2.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    
    pygame.display.update()

pygame.quit()