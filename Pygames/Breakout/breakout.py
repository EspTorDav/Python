import pygame
from pygame.locals import *

pygame.init()

#VARIABLES DE VENTANA

screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width,screen_height))
pygame.display.set_caption('Breakout')

#FUENTES

#Fuente de texto
font = pygame.font.SysFont('Constantia',30)


#COLORES

#Color de fondo
bg = (234,218,184) 

#Colores de bloques
red_block = (242,85,96)
green_block = (86,174,87)
blue_block = (69,177,233)

#Colores de barra de jugador
paddle_color = (142,135,123)
paddle_outline_color = (100,100,100)

#Colores de texto
text_color = (78,81,139)

#VARIABLES DE JUEGO
columns = 6
rows = 6
fps = 60
fpsClock = pygame.time.Clock()
live_ball = False
game_over = 0


#Funcion para mostrar texto
def draw_text(text,font,text_color,x,y):
    img = font.render(text,True,text_color)
    screen.blit(img,(x,y))



#CLASE MURO DE BLOQUES
class wall():

    #Instancias
    def __init__(self):
        self.width = screen_width // columns
        self.height = 50
    
    #Crear bloques
    def create_wall(self):

        #Crea una lista vacia de pared de bloques
        self.blocks = []
        
        #Crea una lista vacía de propiedades de cada bloque
        block_individual = []
        for row in range(rows):
            #Crea una lista vacía de filas de bloques
            block_row = []
            #Iterar sobre cada columna
            for column in range(columns):
                #Generar para cada bloque la posición x e y
                block_x = column *self.width
                block_y = row * self.height
                rect = pygame.Rect(block_x,block_y,self.width,self.height)
                #Asignar dureza del bloque en función de la fila
                if row < 2:
                    strenght = 3
                elif row < 4:
                    strenght = 2
                elif row < 6:
                    strenght = 1
                #Aquí se crea la lista donde se guardan los datos de color y forma de cada bloque
                block_individual = [rect, strenght,]
                #Añadir cada bloque a la lista de fila de bloques
                block_row.append(block_individual)
            #Aqui se añade la lista de filas de bloques a la lista de la pared de bloques
            self.blocks.append(block_row)
    
    #Dibujar bloques
    def draw_wall(self):
        for row in self.blocks:
            for block in row:
                #Asignar un color basado en fuerza de bloques
                if block[1] == 3:
                    block_color = blue_block
                elif block[1] == 2:
                    block_color = green_block
                elif block[1] == 1:
                    block_color = red_block
                pygame.draw.rect(screen,block_color,block[0])
                pygame.draw.rect(screen,bg,block[0],2)

#CLASE BARRA DE JUGADOR
class paddle():
     
     #Instancia
     def __init__(self):
         self.reset()
        
    #Movimiento de la barra
     def move(self):
    
       #Reinicia la dirección
       self.direction = 0
       key = pygame.key.get_pressed()
       if key[pygame.K_LEFT] and self.rect.left > 0:
           self.rect.x -= self.speed
           self.direction = -1
       if key[pygame.K_RIGHT] and self.rect.right < screen_width:
           self.rect.x += self.speed
           self.direction = 1
    
     #Dibujar barra de jugador
     def draw_paddle(self):
         pygame.draw.rect(screen,paddle_color,self.rect)
         pygame.draw.rect(screen,paddle_outline_color,self.rect,3)
     
     #Reinicio de la barra
     def reset(self):
         self.height = 20
         self.width = int(screen_width // columns)
         self.x = int((screen_width // 2 - (self.width // 2)))
         self.y = screen_height - (self.height*2)
         self.speed = 10
         self.rect = Rect(self.x,self.y,self.width,self.height)
         self.direction = 0
                
#CLASE DE LA BOLA
class game_ball():
    def __init__(self,x,y):
        self.reset(x,y)
        
    #Dibujo de la bola
    def draw_ball(self):
        pygame.draw.circle(screen,paddle_color,(self.rect.x + self.radius, self.rect.y + self.radius), self.radius)
        pygame.draw.circle(screen,paddle_outline_color,(self.rect.x + self.radius, self.rect.y + self.radius), self.radius,3)
    
    #Movimiento de bola
    def move(self):

        collision_thresh = 5

        #Movimiento inicial de bola    
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        #Colisiones con paredes
        if self.rect.left < 0 or self.rect.right > screen_width:
            self.speed_x *=-1
        if self.rect.top < 0:
            self.speed_y *=-1
        if self.rect.bottom > screen_height:
            self.game_over = -1
        
        #Colision con barra
        if self.rect.colliderect(player_paddle):
            if abs(self.rect.bottom - player_paddle.rect.top) < collision_thresh and self.speed_y > 0:
               self.speed_y *=-1
               self.speed_x += player_paddle.direction
               if self.speed_x > self.speed_max:
                   self.speed_x = self.speed_max
               elif self.speed_x < 0 and self.speed_x < -self.speed_max:
                    self.speed_x = -self.speed_max
            else:
                self.speed_x *= 1

        #Colision con bloques

        #Asumimos que el muro está destruido
        wall_destroyed = 1
        row_counter = 0
        for row in wall.blocks:
            item_counter = 0
            for item in row:
                #Comprobar colisiones con cada bloque
                if self.rect.colliderect(item[0]):
                    if abs(self.rect.bottom - item[0].top) < collision_thresh and self.speed_y > 0:
                        self.speed_y *= -1    
                    if abs(self.rect.top - item[0].bottom) < collision_thresh and self.speed_y < 0:
                        self.speed_y *= -1
                    if abs(self.rect.right - item[0].left) < collision_thresh and self.speed_x > 0:
                        self.speed_x *= -1    
                    if abs(self.rect.left - item[0].right) < collision_thresh and self.speed_x < 0:
                        self.speed_x *= -1  

                     #Reducir dureza de bloques
                    if wall.blocks[row_counter][item_counter][1] > 1:
                       wall.blocks[row_counter][item_counter][1] -= 1
                    else:
                       wall.blocks[row_counter][item_counter][0] = (0,0,0,0)

                #Comprobar si el bloque existe
                if wall.blocks[row_counter][item_counter][0] != (0,0,0,0):
                    wall_destroyed = 0
                
                item_counter += 1
            row_counter +=1
        if wall_destroyed ==1:
            self.game_over = 1

        
    
        return self.game_over
    
    #Reiniciar la posicion de la bola
    def reset(self,x,y):
        self.radius = 10
        self.x = x - self.radius
        self.y = y
        self.rect = Rect(self.x,self.y,self.radius*2,self.radius*2)
        self.speed_x = 4
        self.speed_y = -4
        self.speed_max= 5
        self.game_over = 0


#INSTANCIAS DE JUEGO
#Instancia de muro de bloques
wall = wall()
wall.create_wall()

#Instancia de barra de jugador
player_paddle = paddle()

#Instancia de bola
ball = game_ball(player_paddle.x + (player_paddle.width // 2),player_paddle.y - player_paddle.height)


#GAME LOOP

run = True
while run:

    #Coloreado de fondo
    screen.fill(bg)

    #Configuracion de fps
    fpsClock.tick(fps)
    
    #DIBUJAR PABTALLA
    #Enseñar el muro
    wall.draw_wall()
    #Dibujar la barra
    player_paddle.draw_paddle()
    #Dibujar la bola en pantalla
    ball.draw_ball()

    if live_ball:
      player_paddle.move()
      game_over = ball.move()
      if game_over != 0:
          live_ball = False
    
    #Mostrar instrucciones
    if not live_ball:
        if game_over == 0:
            draw_text('Pulsa para comenzar',font,text_color,(screen_width// 2 - 125), (screen_height // 2 + 50))
        if game_over == 1:
            draw_text('HAS GANADO',font,text_color,(screen_width// 2 - 100), (screen_height // 2 - 20))
            draw_text('Pulsa para comenzar',font,text_color,(screen_width// 2 - 125), (screen_height // 2 + 50))
        if game_over == -1:
            draw_text('FIN DE LA PARTIDA',font,text_color,(screen_width// 2 - 125), (screen_height // 2 ))
            draw_text('Pulsa para comenzar',font,text_color,(screen_width// 2 - 125), (screen_height // 2 + 50))


    #Bucle que maneja todos los eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and live_ball == False:
            live_ball = True
            ball.reset(player_paddle.x + (player_paddle.width // 2),player_paddle.y - player_paddle.height)
            player_paddle.reset()
            wall.create_wall()
    
    #Actualizador de la pantalla
    pygame.display.update()
pygame.quit()