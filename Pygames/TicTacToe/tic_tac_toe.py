import pygame
from pygame import mixer
from pygame.locals import *

pygame.init() 

#DESPLIEGUE DE VENTANA
screen_width = 600
screen_height = 600
screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('TicTacToe')

#VARIABLES 
line_width = 6 #Grosor de linea
markers = [] #Lista de marcadores que dibuja las casillas
clicked = False #Instancia de click de ratón
mouse_pos = [] #Instancia de posición de ratón
player = 1 #Jugador inicializado como player 1
Winner = 0
game_over = False

green_color = (0,255,0)
red_color = (255,0,0)

font = pygame.font.SysFont('Georgia' , 40)

Yes_rect = Rect(screen_width // 2 -100 , screen_height // 2 + 150,70,50)
No_rect = Rect(screen_width // 2 +40 , screen_height // 2 + 150,50,50)
    
#Método para dibujar la cuadrícula
def draw_grid():
    bg_color = (255,255,200)
    grid = (50,50,50)
    screen.fill(bg_color)
    for x in range(1,3):
        pygame.draw.line(screen,grid,(0,200*x),(screen_width,200*x),line_width)
        pygame.draw.line(screen,grid,(200*x,0),(200*x,screen_height),line_width)

#Método para dibujar las "X" y las "O" al clickar con el ratón
def draw_markers():
    x_pos = 0 #Coordenada X dentro de la celda
    for x in markers: #bucle que recorre las celdas
        y_pos = 0 #Coordenada Y dentro de la celda
        for y in x:
            if y == 1:
                pygame.draw.line(screen,green_color,(x_pos*200 + 30,y_pos*200 + 30),(x_pos*200 + 170,y_pos*200 + 170),line_width)
                pygame.draw.line(screen,green_color,(x_pos*200 + 30,y_pos*200 + 170),(x_pos*200 + 170,y_pos*200 + 30),line_width)
            if y == -1:
                pygame.draw.circle(screen,red_color,(x_pos*200 +100,y_pos*200+100),76,line_width)
            y_pos +=1
        x_pos +=1

#Función que detecta el ganador
def check_winner():

    global winner
    global game_over
    y_pos = 0

    for x in markers:
        #Revisa columnas
        if sum(x) == 3:
            winner = 1
            game_over = True
        if sum(x) == -3:
            winner = 2
            game_over = True

        #Revisa filas
        if markers[0][y_pos] + markers[1][y_pos] + markers[2][y_pos] == 3:
            winner = 1
            game_over = True
        if markers[0][y_pos] + markers[1][y_pos] + markers[2][y_pos] == -3:
            winner = 2
            game_over = True
        y_pos+=1
    
    #Revisa diagonales
    if markers[0][0] + markers[1][1] + markers[2][2] == 3 or markers[2][0] + markers[1][1] + markers[0][2] == 3:
        winner = 1
        game_over = True
    if markers[0][0] + markers[1][1] + markers[2][2] == -3 or markers[2][0] + markers[1][1] + markers[0][2] == -3:
        winner = 2
        game_over = True

#Funcion que indica ganador
def draw_winner(winner):

    winner_text = 'Player ' + str(winner) + 'wins!'
    winner_img = font.render(winner_text,True,'purple','white')
    screen.blit(winner_img,(screen_width//2 - 100, screen_height//2 - 50))
    winner_sound = mixer.Sound('ganador.mp3')
    mixer.Sound.play(winner_sound,0,0,1)

    play_again_text = 'Play again?'
    play_again_img = font.render(play_again_text,True,'Black','White')
    screen.blit(play_again_img,(screen_width//2 - 100,screen_height//2 + 100))

    Yes_text = 'Yes'
    Yes_img = font.render(Yes_text,True,'Black')
    pygame.draw.rect(screen,'white',Yes_rect)
    screen.blit(Yes_img,(screen_width//2 - 100,screen_height//2 + 150))

    No_text = 'No'
    No_img = font.render(No_text,True,'Black')
    pygame.draw.rect(screen,'white',No_rect)
    screen.blit(No_img,(screen_width//2 + 40,screen_height//2 + 150))



#Bucle que divide la gradilla en una matriz de 3x3
for x in range(3):
    row = [0] * 3
    markers.append(row)


while True:

    draw_grid()
    draw_markers()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if game_over == 0:

         if event.type ==pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
         if event.type == pygame.MOUSEBUTTONUP and clicked ==True:
            clicked = False
            mouse_pos = pygame.mouse.get_pos()
            cell_x = mouse_pos[0]
            cell_y = mouse_pos[1]
            if markers [cell_x//200][cell_y//200] == 0:
               markers [cell_x//200][cell_y//200] = player
               player *= -1
               check_winner()
    if game_over == True:
        draw_winner(winner)
        if event.type ==pygame.MOUSEBUTTONDOWN and clicked == False:
            clicked = True
        if event.type == pygame.MOUSEBUTTONUP and clicked ==True:
            clicked = False
            pos = pygame.mouse.get_pos()
            if Yes_rect.collidepoint(pos):
                markers = [] 
                mouse_pos = [] 
                player = 1 
                Winner = 0
                game_over = False
                for x in range(3):
                 row = [0] * 3
                 markers.append(row)
            if No_rect.collidepoint(pos):
                pygame.quit()

    pygame.display.update()

