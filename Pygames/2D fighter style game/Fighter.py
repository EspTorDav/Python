import pygame

class Fighter():
    def __init__(self, player, x ,y, flip, data, sprite_sheet, animation_steps, sound):
        self.player = player
        self.size = data[0]
        self.image_scale = data[1]
        self.rect = pygame.Rect((x , y, 80, 180))
        self.vel_y = 0
        self.running = False
        self.jump = False
        self.attacking = False
        self.attack_type = 0
        self.attack_cooldown = 0
        self.health = 100
        self.alive = True
        self.flip = flip
        self.animation_list = self.load_images (sprite_sheet, animation_steps)
        self.action = 0 #0:Idle , #1:Run, #2: Jump, #3:Attack1 #4:Attack2 #5:Hit #6:Death
        self.frame_index = 0
        self.image = self.animation_list[self.action][self.frame_index]
        self.offset = data[2]
        self.update_time = pygame.time.get_ticks()
        self.hit = False
        self.attack_sound = sound

    def load_images(self, sprite_sheet, animation_steps):
        #Extraer imagenes de los spritesheet
        animation_list = []
        for y, animation in enumerate(animation_steps):
            temp_img_list = []
            for x in range(animation):
                temp_img = sprite_sheet.subsurface(x * self.size, y* self.size, self.size, self.size)
                scaled_temp_img = pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale))
                temp_img_list.append(scaled_temp_img)
            animation_list.append(temp_img_list)
        return animation_list

    
    def move(self, screen_width , screen_height, surface, target, round_over):
        self.attack_type = 0
        SPEED = 10
        GRAVITY = 2
        dx = 0
        dy = 0
        self.running = False

        #Comprobar presión de teclado
        key = pygame.key.get_pressed()

        #Solo pueden realizar acciones si no están atacando
        if self.attacking == False and self.alive == True and round_over == False:
            #Controles player 1
            if self.player == 1:
                #Movimiento
                if key[pygame.K_a]:
                    dx -= SPEED
                    self.running = True
                if key[pygame.K_d]:
                    dx += SPEED
                    self.running = True
                #Salto
                if key[pygame.K_w] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                #Ataque
                if key[pygame.K_r] or key[pygame.K_t]:
                    self.attack(target)
                    #Determinar que ataque se ha usado
                    if key[pygame.K_r]:
                        self.attack_type = 1
                    if key[pygame.K_t]:
                        self.attack_type = 2

            #Controles player 2
            if self.player == 2:
                #Movimiento
                if key[pygame.K_j]:
                    dx -= SPEED
                    self.running = True
                if key[pygame.K_l]:
                    dx += SPEED
                    self.running = True
                #Salto
                if key[pygame.K_i] and self.jump == False:
                    self.vel_y = -30
                    self.jump = True
                #Ataque
                if key[pygame.K_u] or key[pygame.K_y]:
                    self.attack(target)
                    #Determinar que ataque se ha usado
                    if key[pygame.K_u]:
                        self.attack_type = 1
                    if key[pygame.K_y]:
                        self.attack_type = 2
            

        #Aplicar gravedad
        self.vel_y += GRAVITY
        
        dy += self.vel_y

        #COLISIONES

        #Contener la clase dentro de la ventana
        if self.rect.left + dx < 0:
            dx = 0 - self.rect.left
        if self.rect.right + dx > screen_width:
            dx = screen_width - self.rect.right
        if self.rect.bottom + dy > screen_height - 110:
            self.vel_y = 0
            self.jump = False
            dy = screen_height - 110 - self.rect.bottom

        #Comprobar que los luchadores se miran
        if target.rect.centerx > self.rect.centerx:
            self.flip = False
        else:
            self.flip = True

        #Aplicar cooldown de ataque
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        #Actualizar posicion
        self.rect.x += dx
        self.rect.y += dy


    def update(self):
        if self.health <=0:
            self.health = 0
            self.alive = False
            self.update_action(6)
        elif self.hit == True:
            self.update_action(5)
        elif self.attacking == True:
            if self.attack_type == 1:
               self.update_action(3)
            elif self.attack_type == 2:
                self.update_action(4)
        elif self.jump == True:
            self.update_action(2)
        elif self.running == True:
            self.update_action(1)
        else:
            self.update_action(0)

        animation_cooldown = 50
        #Actualizar imagen
        self.image = self.animation_list[self.action][self.frame_index]
        #Comprobar que pasa suficiente tiempo entre animaciones
        if pygame.time.get_ticks() - self.update_time > animation_cooldown:
            self.frame_index += 1
            self.update_time = pygame.time.get_ticks()
        #Comprobar que la animacion ha terminado
        if self.frame_index >= len(self.animation_list[self.action]):
            #Comprobar si el jugador está vivo
            if self.alive == False:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0
            #comprobar que un ataque se ha ejecutado
                if self.action == 3 or self.action == 4:
                    self.attacking = False
                    self.attack_cooldown = 20
                #Comprobar si se ha tomado daño
                if self.action == 5:
                    self.hit = False
                    self.attacking = False
                    self.attack_cooldown = 20


    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()


    def attack(self, target):
        if self.attack_cooldown == 0:
            self.attacking = True
            self.attack_sound.play()
            attacking_rect = pygame.Rect(self.rect.centerx - (2 * self.rect.width * self.flip), self.rect.y, 2 * self.rect.width, self.rect.height)
            if attacking_rect.colliderect(target.rect):
                target.health -= 10
                target.hit = True

    def draw(self, surface):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - (self.offset[0] * self.image_scale) , self.rect.y - (self.offset[1] * self.image_scale)))