# File created by: Chris Cozort

# The sprites module contains all the sprites
# Sprites include: player, mob - moving object


import pygame as pg
from pygame.sprite import Sprite
from settings import *
from utils import Cooldown
from utils import Spritesheet
from random import randint
from random import choice
from os import path
vec = pg.math.Vector2

class Player(Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.spritesheet = Spritesheet(path.join(self.game.img_folder, "spritesheet.png"))
        self.load_images()
        self.image = pg.Surface((32, 32))
        
        # self.image.fill(GREEN)
        self.image = game.player_img
        self.image.set_colorkey(BLACK)
        self.image_inv = game.player_img_inv
        self.rect = self.image.get_rect()
        # self.rect.x = x * TILESIZE[0]
        # self.rect.y = y * TILESIZE[1]
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.speed = 250
        self.health = 100
        self.coins = 0
        self.cd = Cooldown(1000)
        self.weapon_cd = Cooldown(400)
        self.effect_cd = Cooldown(200)
        self.dir = vec(0,0)
        self.walking = False
        self.jumping = False
        self.current_frame = 0
        self.last_update = 0
        self.jump_power = 100
        self.attacking = False
        self.facing = ""
    
    def rotate(self):
        pass
    def jump(self):
        # print('trying to jump')
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
        self.rect.y += -1
        if hits:
            # print('collided with floor')
            self.vel.y = -self.jump_power
    def load_images(self):
        self.standing_frames = [self.spritesheet.get_image(0, 0, 32, 32),
                                self.spritesheet.get_image(0, 32, 32, 32)]
        for frame in self.standing_frames:
            frame.set_colorkey(BLACK)
        # self.walk_frames_r
        # self.walk_frames_l
        # pg.transform.flip

    def animate(self):
        now = pg.time.get_ticks()
        if not self.jumping and not self.walking:
            if now - self.last_update > 350:
                # print(now)
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.standing_frames)
                bottom = self.rect.bottom
                self.image = self.standing_frames[self.current_frame]
                self.rect = self.image.get_rect()
                self.rect.bottom = bottom
    



    
    def get_keys(self):
        ######################## mr cozort made a mistake :( #############
        self.vel = vec(0,GRAVITY)
        keys = pg.key.get_pressed()
        
        if keys[pg.K_SPACE]:
            self.jump()
        if keys[pg.K_e]:
            print(self.rect.x)
            p = Projectile(self.game, self.rect.x, self.rect.y, self.dir)
        if keys[pg.K_w]:
            self.vel.y = -self.speed*self.game.dt
            self.dir = vec(0,-1)
        if keys[pg.K_a]:
            self.vel.x = -self.speed*self.game.dt
            self.dir = vec(-1,0)
            if self.facing != "right":
                self.facing = "right"
                self.flipped_img = pg.transform.flip(self.image, True, False)
            self.image = self.flipped_img
        if keys[pg.K_s]:
            self.vel.y = self.speed*self.game.dt
            self.dir = vec(0,1)
        if keys[pg.K_d]:
            self.vel.x = self.speed*self.game.dt
            self.dir = vec(1,0)
            if self.facing != "left":
                self.facing = "left"
                self.flipped_img = pg.transform.flip(self.image, True, False)
            self.image = self.flipped_img
        # if keys[pg.K_k]:
        #     self.attack()

        # accounting for diagonal
        if self.vel[0] != 0 and self.vel[1] != 0:
            self.vel *= 0.7071
    
    # def attack(self):
    #     if self.weapon_cd.ready() and not self.attacking:
    #         self.weapon_cd.start()
    #         self.attacking = True
    def effects_trail(self):
        if self.effect_cd.ready():
            EffectTrail(self.game, self.rect.x,self.rect.y)

    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # print(self.pos)
                if self.vel.x > 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].vel.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.x = hits[1].rect.left - self.rect.width
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                        
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].vel.x += self.vel.x
                    else:
                        self.pos.x = hits[0].rect.right
                self.vel.x = 0
                # hits[0].vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # print(self.pos)
                if self.vel.y > 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].vel.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.y = hits[1].rect.top - self.rect.height
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height
                        
                if self.vel.y < 0:
                    if hits[0].state == "moveable":
                        print("i hit a moveable block...")
                        hits[0].vel.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmovable":
                                self.pos.y = hits[1].rect.bottom
                    else:
                        self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                # hits[0].vel.x = 0
                self.rect.y = self.pos.y
    
    def collide_with_stuff(self, group, kill):
        hits = pg.sprite.spritecollide(self, group, kill)
        if hits: 
            if str(hits[0].__class__.__name__) == "Mob":
                if self.cd.ready():
                    self.health -= 10
                    self.cd.start()
                # print("Ouch!")
            if str(hits[0].__class__.__name__) == "Coin":
                self.coins += 1
                print(self.coins)

    def update(self):
        # self.effects_trail()
        self.get_keys()
        # self.animate()
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        self.collide_with_stuff(self.game.all_mobs, False)
        self.collide_with_stuff(self.game.all_coins, True)
        # print(self.weapon_cd.ready())
        print(self.attacking)

        # # print(self.cd.ready())
        # if not self.cd.ready():
        #     self.image = self.game.player_img_inv
        #     # self.rect = self.image_inv.get_rect()
        #     print("not ready")
        # else:
        #     # self.image.fill(GREEN)
        #     self.image = self.game.player_img
        #     # self.rect = self.image.get_rect()
        #     print("ready")
import pygame
import math


# ... (Pygame initialization and loading original_image) ...

class ArcRotatingSprite(pygame.sprite.Sprite):
    def __init__(self, game, pivot_offset, arc_center, arc_radius):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.sword_img
        self.original_image = self.image.convert_alpha()
        self.image = self.original_image
        self.pivot_offset = pivot_offset  # (x_offset, y_offset) from topleft of image
        self.arc_center = arc_center
        self.arc_radius = arc_radius
        self.current_angle = 0  # For sprite rotation
        self.current_arc_angle = 0 # For arc movement
        self.rect = self.image.get_rect()
        self.spin_speed = 250

    def update(self):
        # Update sprite rotation
        self.current_angle = (self.current_angle + 5 * self.game.dt) % 360  # Example rotation speed
        # self.current_angle = 90
        self.image = pygame.transform.rotate(self.original_image, self.current_angle)
        
        # Calculate new rect based on rotation and pivot
        old_center = self.rect.center
        self.rect = self.image.get_rect(center=old_center)
        
        # Adjust for pivot offset
        # This part requires more precise calculation based on your pivot_offset
        # For a bottom-center pivot:
        pivot_on_rotated_image = (self.image.get_width() / 2, self.image.get_height())
        offset_x = self.pivot_offset[0] - pivot_on_rotated_image[0]
        offset_y = self.pivot_offset[1] - pivot_on_rotated_image[1]
        
        # Update arc movement
        self.current_arc_angle = (self.current_arc_angle + 0.05 * self.game.dt) % (2 * math.pi) # Example arc speed
        arc_pivot_x = self.arc_center[0] + self.arc_radius * 2 * math.cos(self.current_arc_angle)
        arc_pivot_y = self.arc_center[1] + self.arc_radius * 2 *  math.sin(self.current_arc_angle)

        self.rect.centerx = arc_pivot_x - offset_x
        self.rect.centery = arc_pivot_y - offset_y





class RotatingSprite(Sprite):
    def __init__(self, game,pivot_pos, radius, angle_offset=0, rotate_with_orbit=False):
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.game = game
        
        self.image = game.sword_img
        self.original_image = self.image.convert_alpha()
        self.image = self.original_image
        

        self.pivot = pygame.Vector2(pivot_pos)   # rotation center
        self.radius = radius                     # distance from pivot
        self.angle = angle_offset                # start angle in radians
        self.rotate_with_orbit = rotate_with_orbit

        # image info
        self.image_w = self.original_image.get_width()
        self.image_h = self.original_image.get_height()

        # bottom-center of the sprite (its rotation anchor)
        self.local_pivot = pygame.Vector2(self.image_w // 2, self.image_h)

        self.rect = self.image.get_rect()
        self.speed = 1

    def update(self):
        """Rotate around the pivot. Speed is radians per frame."""
        self.angle += self.speed

        # Orbit position
        pos_x = self.game.player.pos.x + 16 + math.cos(self.angle) * self.radius
        pos_y = self.game.player.pos.y + 16 + math.sin(self.angle) * self.radius
        # pos_x = self.pivot.x + math.cos(self.angle) * self.radius
        # pos_y = self.pivot.y + math.sin(self.angle) * self.radius

        # Rotate the sprite's image if desired
        if self.rotate_with_orbit:
            rot_deg = -math.degrees(self.angle)  # negative to rotate correctly
            self.image = pygame.transform.rotate(self.original_image, rot_deg)
        else:
            self.image = self.original_image

        # Update rect
        self.rect = self.image.get_rect(center=(pos_x, pos_y))


class Mob(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_mobs
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((32, 32), pg.SRCALPHA)
        self.fade = 255
        self.image.fill((255,0,0,50))
        self.rect = self.image.get_rect()
        self.vel = vec(choice([-1,1]),choice([-1,1]))
        self.pos = vec(x,y)*TILESIZE[0]
        # self.rect.x = x * TILESIZE[0]
        # self.rect.y = y * TILESIZE[1]
        self.health = 100
        self.speed = 5
        print(self.pos)
        self.cd = Cooldown(1000)
    
    def collide_with_stuff(self, group, kill):
        hits = pg.sprite.spritecollide(self, group, kill)
        if hits: 
            if str(hits[0].__class__.__name__) == "Sword":
                if self.cd.ready():
                    self.health -= 50
                    self.cd.start()
                    print("enemy health is", str(self.health))
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # print(self.pos)
                if self.vel.x > 0:
                    self.pos.x = hits[0].rect.left - self.rect.width
                if self.vel.x < 0:
                    self.pos.x = hits[0].rect.right
                self.rect.x = self.pos.x
                self.vel.x *= choice([-1,1])
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                if self.vel.y > 0:
                    self.pos.y = hits[0].rect.top - self.rect.height
                if self.vel.y < 0:
                    self.pos.y = hits[0].rect.bottom
                self.rect.y = self.pos.y
                self.vel.y *= choice([-1,1])
    def update(self):
        if self.health <= 0:
            self.kill()
        # mob behavior
        # if self.game.player.pos.x > self.pos.x:
        #     self.vel.x = 1
        # else:
        #     self.vel.x = -1
        #     # print("I don't need to chase the player x")
        # if self.game.player.pos.y > self.pos.y:
        #     self.vel.y = 1
        # else:
        #     self.vel.y = -1
            # print("I don't need to chase the player x")
        self.pos += self.vel * self.speed
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')
        self.collide_with_stuff(self.game.all_weapons, False)
         # print(self.cd.ready())
        if not self.cd.ready():
            self.image.fill((255,0,0,150))
            print("not ready")
        else:
            self.image.fill((0,255,0,255))
            # self.rect = self.image.get_rect()
            print("ready")

class Coin(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_coins
        Sprite.__init__(self, self.groups)
        self.image = pg.Surface(TILESIZE)
        self.image.fill(YELLOW)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y *TILESIZE[1]
        # coin behavior
        pass

class EffectTrail(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites
        Sprite.__init__(self, self.groups)
        self.image = pg.Surface(TILESIZE, pg.SRCALPHA)
        self.alpha = 255
        self.image.fill((255,255,255,255))
        self.rect = self.image.get_rect()
        self.cd = Cooldown(10)
        self.rect.x = x
        self.rect.y = y
        # coin behavior
        self.scale_x = 32
        self.scale_y = 32
    def update(self):
        if self.alpha <= 10:
            self.kill()
        self.image.fill((255,255,255,self.alpha))
        
        if self.cd.ready():
            self.scale_x -=1
            self.scale_y -=1
            print("I'm ready")
            self.alpha -= 50
            new_image = pg.transform.scale(self.image, (self.scale_x, self.scale_y))
            self.image = new_image



class Sword(Sprite):
    def __init__(self, game, x, y):
        self.game = game
        self.groups = game.all_sprites, game.all_weapons
        Sprite.__init__(self, self.groups)
        self.image = pg.Surface((TILESIZE[0]*2,TILESIZE[1]//2))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = x * TILESIZE[0]
        self.rect.y = y *TILESIZE[1]
    def update(self):
        self.rect.x = self.game.player.rect.x + self.game.player.dir.x * 32
        if self.game.player.dir.x < 0:
            self.rect.x = self.game.player.rect.x + self.game.player.dir.x * 64
            # pg.transform.flip(self.image, True, False)
        self.rect.y = self.game.player.rect.y



class Wall(Sprite):
    def __init__(self, game, x, y, state):
        self.groups = game.all_sprites, game.all_walls
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface(TILESIZE)
        self.image.fill(GREY)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x,y) * TILESIZE[0]
        self.state = state
        # print("wall created at", str(self.rect.x), str(self.rect.y))
    
    def collide_with_walls(self, dir):
        if dir == 'x':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                
                # print(self.pos)
                if self.vel.x > 0:
                    # print("a wall collided with a wall")
                    if hits[0].state == "moveable":
                        # print("i hit a moveable block...")
                        hits[0].pos.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.x = hits[1].rect.left - self.rect.width
                    else:
                        self.pos.x = hits[0].rect.left - self.rect.width
                        
                if self.vel.x < 0:
                    if hits[0].state == "moveable":
                        # print("i hit a moveable block...")
                        hits[0].pos.x += self.vel.x
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.x = hits[1].rect.right
                    else:
                        self.pos.x = hits[0].rect.right
                self.vel.x = 0
                self.rect.x = self.pos.x
        if dir == 'y':
            hits = pg.sprite.spritecollide(self, self.game.all_walls, False)
            if hits:
                # print(self.pos)
                
                if self.vel.y > 0:
                    # print('wall y collide down')
                    if hits[0].state == "moveable":
                        # print("i hit a moveable block...")
                        hits[0].pos.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmoveable":
                                self.pos.y = hits[1].rect.top - self.rect.height
                    else:
                        self.pos.y = hits[0].rect.top - self.rect.height
                        
                if self.vel.y < 0:
                    if hits[0].state == "moveable":
                        # print("i hit a moveable block...")
                        hits[0].pos.y += self.vel.y
                        if len(hits) > 1:
                            if hits[1].state == "unmovable":
                                self.pos.y = hits[1].rect.bottom
                    else:
                        self.pos.y = hits[0].rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
    def update(self):
        # wall
        self.pos += self.vel
        self.rect.x = self.pos.x
        self.collide_with_walls('x')
        self.rect.y = self.pos.y
        self.collide_with_walls('y')


class Projectile(Sprite):
    def __init__(self, game, x, y, dir):
        self.game = game
        self.groups = game.all_sprites, game.all_projectiles
        Sprite.__init__(self, self.groups)
        self.game = game
        self.image = pg.Surface((16, 16))
        self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.vel = dir
        self.pos = vec(x,y)
        self.rect.x = x
        self.rect.y = y
        self.speed = 10
        print
    def update(self):
        self.pos += self.vel * self.speed
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        hits = pg.sprite.spritecollide(self, self.game.all_walls, True)
        if hits:
            self.kill()
        
