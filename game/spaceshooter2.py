#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: tasdik
# @Contributers : Branden (Github: @bardlean86)
# @Date:   2016-01-17
# @Email:  prodicus@outlook.com  Github: @tasdikrahman
# @Last Modified by:   tasdik
# @Last Modified by:   Branden
# @Last Modified time: 2016-01-26
# MIT License. You can find a copy of the License @ http://prodicus.mit-license.org

## Game music Attribution
##Frozen Jam by tgfcoder <https://twitter.com/tgfcoder> licensed under CC-BY-3 <http://creativecommons.org/licenses/by/3.0/>

## Additional assets by: Branden M. Ardelean (Github: @bardlean86)

from __future__ import division
import pygame
import random
from os import path
import select
import os

## assets folder
img_dir = path.join(path.dirname(__file__), 'assets')
sound_folder = path.join(path.dirname(__file__), 'sounds')

###############################
## to be placed in "constant.py" later
WIDTH = 800
HEIGHT = 600
FPS = 60
POWERUP_TIME = 5000
BAR_LENGTH = 100
BAR_HEIGHT = 10
BUFFER_LEN = 30
# Define Colors 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
###############################

###############################
## to placed in "__init__.py" later
## initialize pygame and create window
pygame.init()
pygame.mixer.init()  ## For sound
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")
clock = pygame.time.Clock()     ## For syncing the FPS
###############################

font_name = pygame.font.match_font('arial')
pipe_dir = '/home/odroid/test/testfifo'

def main_menu():
    global screen

    menu_song = pygame.mixer.music.load(path.join(sound_folder, "menu.ogg"))
    pygame.mixer.music.play(-1)

    title = pygame.image.load(path.join(img_dir, "main.png")).convert()
    title = pygame.transform.scale(title, (WIDTH, HEIGHT), screen)

    screen.blit(title, (0,0))
    pygame.display.update()

    while True:
        ev = pygame.event.poll()
        if ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN:
                break
            elif ev.key == pygame.K_q:
                pygame.quit()
                quit()
        else:
            draw_text(screen, "Press [ENTER] To Begin", 30, WIDTH/2, HEIGHT/2)
            draw_text(screen, "or [Q] To Quit", 30, WIDTH/2, (HEIGHT/2)+40)
            pygame.display.update()

    #pygame.mixer.music.stop()
    ready = pygame.mixer.Sound(path.join(sound_folder,'getready.ogg'))
    ready.play()
    screen.fill(BLACK)
    draw_text(screen, "GET READY!", 40, WIDTH/2, HEIGHT/2)
    pygame.display.update()
    

def draw_text(surf, text, size, x, y):
    ## selecting a cross platform font to display the score
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)       ## True denotes the font to be anti-aliased 
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)


def draw_shield_bar(surf, x, y, pct):
    # if pct < 0:
    #     pct = 0
    pct = max(pct, 0) 
    ## moving them to top
    # BAR_LENGTH = 100
    # BAR_HEIGHT = 10
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, GREEN, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)


def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect= img.get_rect()
        img_rect.x = x + 30 * i
        img_rect.y = y
        surf.blit(img, img_rect)


def newObstacle(x, y,width,height):
    obstacle_element = Obstacle(x,y,width,height)
    #all_sprites.add(obstacle_element)
    obstacles.append([obstacle_element, BUFFER_LEN])

def newmob():
    mob_element = Mob()
    all_sprites.add(mob_element)
    mobs.add(mob_element)

class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0 
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 75

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


class Player(pygame.sprite.Sprite):
    def __init__(self, pnum):
        pygame.sprite.Sprite.__init__(self)
        ## scale the player img down
        self.image = pygame.transform.scale(player_img, (50, 38))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT - 10
        self.speedx = 0 
        #adding movement in y direction
        self.speedy = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_timer = pygame.time.get_ticks()
        self.player_num = pnum


    def update(self):
        ## time out for powerups
        if self.power >=2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()

        ## unhide 
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 1000:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 30
        #self stabilizing mechanism
        '''if self.speedx>0:
            self.speedx += -.1
        else:
            self.speedx += .1
        if self.speedy>0:
            self.speedy += -.1
        else:
            self.speedy += .1
        '''   
        # then we have to check whether there is an event hanlding being done for the arrow keys being 
        ## pressed 
        #TODO: acceleration
        ## will give back a list of the keys which happen to be pressed down at that moment
        
        keystate = pygame.key.get_pressed()     
        
        if self.player_num == 1:
            if keystate[pygame.K_LEFT]:
                self.speedx = -7
            elif keystate[pygame.K_RIGHT]:
                self.speedx = 7
            else:
                self.speedx = 0
            if keystate[pygame.K_UP]:
                self.speedy = -7
            elif keystate[pygame.K_DOWN]:
                self.speedy = 7
            else:
                self.speedy = 0
            #Fire weapons by holding spacebar
<<<<<<< HEAD
            if keystate[pygame.K_RETURN]:
                self.shoot()
=======
            if keystate[pygame.K_SPACE]:
                self.shoot()

>>>>>>> 96e83db52d24f83caae2ab96cd16a7992f66b8a7
        else:
            if keystate[pygame.K_a]:
                self.speedx = -7
            elif keystate[pygame.K_d]:
                self.speedx = 7
            else:
                self.speedx = 0
            if keystate[pygame.K_w]:
                self.speedy = -7
            elif keystate[pygame.K_s]:
                self.speedy = 7
            else:
                self.speedy = 0
<<<<<<< HEAD
            #Fire weapons by holding spacebar
            if keystate[pygame.K_SPACE]:
                self.shoot()
=======
            #Fire weapons by pressing 
            if keystate[pygame.K_TAB]:
                self.shoot()

>>>>>>> 96e83db52d24f83caae2ab96cd16a7992f66b8a7

        self.rect.x += self.speedx
        self.rect.y += self.speedy

        ## check for the borders at the left and right, up down
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH-1
        if self.rect.left < 0:
            self.rect.left = 1
        if self.rect.top < 0:
            self.rect.top = 1
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT-1
        

    def shoot(self):
        ## to tell the bullet where to spawn
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top, self.player_num)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shooting_sound.play()
            if self.power == 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery, self.player_num)
                bullet2 = Bullet(self.rect.right, self.rect.centery, self.player_num)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shooting_sound.play()

            """ MOAR POWAH """
            if self.power >= 3:
                bullet1 = Bullet(self.rect.left, self.rect.centery, self.player_num)
                bullet2 = Bullet(self.rect.right, self.rect.centery, self.player_num)
                missile1 = Missile(self.rect.centerx, self.rect.top, self.player_num) # Missile shoots from center of ship
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                all_sprites.add(missile1)
                bullets.add(bullet1)
                bullets.add(bullet2)
                bullets.add(missile1)
                shooting_sound.play()
                missile_sound.play()

    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()

    def hide(self):
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)


# defines the enemies
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width *.90 / 2)
        self.rect.x = random.randrange(0, WIDTH - self.rect.width)
        self.rect.y = random.randrange(0, HEIGHT-30)
        self.speedy = 0#random.randrange(5, 20)        ## for randomizing the speed of the Mob

        ## randomize the movements a little more 
        self.speedx = 0#random.randrange(-3, 3)

        ## adding rotation to the mob element
        self.rotation = 0
        self.rotation_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()  ## time when the rotation has to happen
        
    def rotate(self):
        time_now = pygame.time.get_ticks()
        if time_now - self.last_update > 50: # in milliseconds
            self.last_update = time_now
            self.rotation = (self.rotation + self.rotation_speed) % 360 
            new_image = pygame.transform.rotate(self.image_orig, self.rotation)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        ## now what if the mob element goes out of the screen

        if (self.rect.top > HEIGHT + 10) or (self.rect.left < -25) or (self.rect.right > WIDTH + 20):
            self.rect.x = random.randrange(0, WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = 0#random.randrange(1, 8)        ## for randomizing the speed of the Mob

# defines the enemies
class Obstacle():
    def __init__(self, x, y, width, height):
        #pygame.sprite.Sprite.__init__(self)
        #self.image_orig = random.choice(meteor_images)
        #self.image_orig.set_colorkey(BLACK)
        #self.image = self.image_orig.copy()
        self.rect = pygame.Rect(x,y,width,height)
        self.rect.x = x
        self.rect.y = y
        self.last_update = pygame.time.get_ticks()  ## time when the rotation has to happen

    def update(self):
        pass

## defines the sprite for Powerups
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.center = center
        self.speedy = 2

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.top > HEIGHT:
            self.kill()

            

## defines the sprite for bullets
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, player_num):
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        ## place the bullet according to the current position of the player
        self.rect.bottom = y 
        self.rect.centerx = x
        self.speedy = -20
	self.player_num = player_num

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        ## kill the sprite after it moves over the top border
        if self.rect.bottom < 0:
            self.kill()

        ## now we need a way to shoot
        ## lets bind it to "spacebar".
        ## adding an event for it in Game loop

## FIRE ZE MISSILES
class Missile(pygame.sprite.Sprite):
    def __init__(self, x, y, player_num):
        pygame.sprite.Sprite.__init__(self)
        self.image = missile_img
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
	self.player_num=player_num

    def update(self):
        """should spawn right in front of the player"""
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()


###################################################
## Load all game images

background = pygame.image.load(path.join(img_dir, 'starfield.png')).convert()
background_rect = background.get_rect()
## ^^ draw this rect first 

player_img = pygame.image.load(path.join(img_dir, 'playerShip1_orange.png')).convert()
player_mini_img = pygame.transform.scale(player_img, (25, 19))
player_mini_img.set_colorkey(BLACK)
bullet_img = pygame.image.load(path.join(img_dir, 'laserRed16.png')).convert()
missile_img = pygame.image.load(path.join(img_dir, 'missile.png')).convert_alpha()
# meteor_img = pygame.image.load(path.join(img_dir, 'meteorBrown_med1.png')).convert()
meteor_images = []
meteor_list = [
    'meteorBrown_big1.png',
    'meteorBrown_big2.png', 
    'meteorBrown_med1.png', 
    'meteorBrown_med3.png',
    'meteorBrown_small1.png',
    'meteorBrown_small2.png',
    'meteorBrown_tiny1.png'
]

for image in meteor_list:
    meteor_images.append(pygame.image.load(path.join(img_dir, image)).convert())

## meteor explosion
explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    ## resize the explosion
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)

    ## player explosion
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(img_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)

## load power ups
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(img_dir, 'shield_gold.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(img_dir, 'bolt_gold.png')).convert()


###################################################


###################################################
### Load all game sounds
shooting_sound = pygame.mixer.Sound(path.join(sound_folder, 'pew.wav'))
missile_sound = pygame.mixer.Sound(path.join(sound_folder, 'rocket.ogg'))
expl_sounds = []
for sound in ['expl3.wav', 'expl6.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(sound_folder, sound)))
## main background music
#pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
pygame.mixer.music.set_volume(0.2)      ## simmered the sound down a little

player_die_sound = pygame.mixer.Sound(path.join(sound_folder, 'rumble1.ogg'))
###################################################

## group all the sprites together for ease of update
all_sprites = pygame.sprite.Group()
player1 = Player(1)
player2 = Player(2)
players = [player1, player2]
all_sprites.add(player1)
all_sprites.add(player2)

obstacles = []

## spawn a group of mob
mobs = pygame.sprite.Group()
#for i in range(8):      ## 8 mobs
    # mob_element = Mob()
    # all_sprites.add(mob_element)
    # mobs.add(mob_element)
    #newmob()

## group for bullets
bullets = pygame.sprite.Group()
powerups = pygame.sprite.Group()

#### Score board variable
score = 0

## TODO: make the game music loop over again and again. play(loops=-1) is not working
# Error : 
# TypeError: play() takes no keyword arguments
#pygame.mixer.music.play()

#############################
## Game loop
running = True
menu_display = True
with open(pipe_dir) as fifo:
    while running:
        if menu_display:
            main_menu()
            pygame.time.wait(3000)

            #Stop menu music
            pygame.mixer.music.stop()
            #Play the gameplay music
            pygame.mixer.music.load(path.join(sound_folder, 'tgfcoder-FrozenJam-SeamlessLoop.ogg'))
            pygame.mixer.music.play(-1)     ## makes the gameplay sound in an endless loop
            
            menu_display = False
            
        #1 Process input/events
        clock.tick(FPS)     ## will make the loop run at the same speed all the time
        for event in pygame.event.get():        # gets all the events which have occured till now and keeps tab of them.
            ## listening for the the X button at the top
            if event.type == pygame.QUIT:
                running = False

            ## Press ESC to exit game
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            # ## event for shooting the bullets
            # elif event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE:
            #         player.shoot()      ## we have to define the shoot()  function
        #clear all obstacles using a buffer
        obstacles_copy = obstacles
        for o in obstacles_copy:
	    o[1]=o[1]-1
            if o[1]<=0:
                obstacles.pop(0)
            
        #now we process our pipe data
        line = fifo.read()
        line = line.split('\n')
	error = False
        try: 
            line = line[-2].strip()
        except:
            error=True
        if line and not error and line[0]: 
            #print('line stripped')
            #print(repr(line))
            coordinates = line.split(",")
            for i in range(0, len(coordinates), 4):
                tl_x = int(coordinates[i])
                tl_y = int(coordinates[i+1])
                br_x = int(coordinates[i+2])
                br_y = int(coordinates[i+3])
            	newObstacle(tl_x,tl_y,br_x-tl_x,br_y-tl_y)
            #pygame.draw.rect(screen,(255,0,0),(tl_x,tl_y,br_x-tl_x,br_y-tl_y),1)
            #pygame.display.update()
        
        #2 Update
        all_sprites.update()


        ## check if a bullet hit a mob
        ## now we have a group of bullets and a group of mob
        hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
        ## now as we delete the mob element when we hit one with a bullet, we need to respawn them again
        ## as there will be no mob_elements left out 
        for hit in hits:
            score += 50 - hit.radius         ## give different scores for hitting big and small metoers
            random.choice(expl_sounds).play()
            # m = Mob()
            # all_sprites.add(m)
            # mobs.add(m)
            expl = Explosion(hit.rect.center, 'lg')
            all_sprites.add(expl)
            if random.random() > 0.9:
                pow = Pow(hit.rect.center)
                all_sprites.add(pow)
                powerups.add(pow)
            #newmob()        ## spawn a new mob

        ## ^^ the above loop will create the amount of mob objects which were killed spawn again
        #########################
        #now check if the bullet hit the obstacle
        for bullet in bullets:
            for obstacle in obstacles:
                #check for collision
                if obstacle[0].rect.colliderect(bullet.rect):
                    #trigger explosion
                    expl = Explosion(bullet.rect.center, 'sm')
                    all_sprites.add(expl)
                    #remove bullet
                    bullet.kill()
        for player in players:
            ## check if the player collides with the obstacle
	    #hits = pygame.sprite.spritecollide(player, obstacles, False, pygame.sprite.collide_circle)        ## gives back a list, True makes the mob element disappear
            for o in obstacles:
                if o[0].rect.colliderect(player.rect):
                    player.shield -= 100
                    #don't let the player move through the box
                    player.speedx = -player.speedx
                    player.speedy = -player.speedy
                    expl = Explosion(player.rect.center, 'sm')
                    all_sprites.add(expl)
                    if player.shield <= 0: 
                        player_die_sound.play()
                        death_explosion = Explosion(player.rect.center, 'player')
                        all_sprites.add(death_explosion)
                        player.hide()
                        player.lives -= 1
                        player.shield = 100
            ## check if the player collides with the mob
            hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)        ## gives back a list, True makes the mob element disappear
            for hit in hits:
                player.shield -= 10
                #don't let the player move through the box
                player.speedx = 0
                player.speedy = 0
                expl = Explosion(hit.rect.center, 'sm')
                all_sprites.add(expl)
                if player.shield <= 0: 
                    player_die_sound.play()
                    death_explosion = Explosion(player.rect.center, 'player')
                    all_sprites.add(death_explosion)
                    player.hide()
                    player.lives -= 1
                    player.shield = 100
            #check if player got hit by another player's bullets
            #or its own I guess haha
            hits = pygame.sprite.spritecollide(player, bullets, True)
            for hit in hits:
                player.shield -= 10
                expl = Explosion(hit.rect.center, 'sm')
                all_sprites.add(expl)
                if player.shield <= 0: 
                    player_die_sound.play()
                    death_explosion = Explosion(player.rect.center, 'player')
                    all_sprites.add(death_explosion)
                    player.hide()
                    player.lives -= 1
                    player.shield = 100
            ## if the player hit a power up
            hits = pygame.sprite.spritecollide(player, powerups, True)
            for hit in hits:
                if hit.type == 'shield':
                    player.shield += random.randrange(10, 30)
                    if player.shield >= 100:
                        player.shield = 100
                if hit.type == 'gun':
                    player.powerup()
            ## keep track of whose alive
            if player.lives == 0 and not death_explosion.alive():
                players.remove(player)
        if len(players)==1:
            #game over - only one player left
            running = False
        #3 Draw/render
        screen.fill(BLACK)
        ## draw the stargaze.png image
        #screen.blit(background, background_rect)
        all_sprites.draw(screen)
        draw_text(screen, str(score), 18, WIDTH / 2, 10)     ## 10px down from the screen
        draw_shield_bar(screen, 5, 5, player1.shield)

        # Draw lives
        draw_lives(screen, WIDTH - 100, 5, player1.lives, player_mini_img)

        ## Done after drawing everything to the screen
        pygame.display.flip()       
    #end screen
    screen.fill(BLACK)
    draw_text(screen, "Winner: Player "+str(players[0].player_num), 40, WIDTH/2, HEIGHT/2)
    pygame.display.update()
    pygame.time.wait(3000)
    #back to main menu
pygame.quit()