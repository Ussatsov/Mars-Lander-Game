#!/usr/bin/env python3

#  Author: Gordei Ussatsov
#  Date: 15 April 2019
#  Version: 3.0
#  Game classes with sprites

import pygame as pg
from settings import *
from math import cos, sin, radians
from random import randrange, choice, uniform
from classes import *
vec = pg.math.Vector2


class Ship(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = game.ship_img[0]
        self.rect = self.image.get_rect()
        self.radius = 25
        self._Player = Player(self, self.game)
        self._Engine = Engine(self)
        self._Failures = Failures(self)        
        self.pos = vec(randrange(0, WIDTH), 0)
        self.vel = vec(uniform(0, .625), uniform(-.625, .625))
        self.acc = vec(0, 0)
        self.fuel = 10000
        self.rot = 0
        self.dmg_sustain = 0
        self.height = self.rect.bottom
        self.if_crashed = False
        self.failure_engine = False
        self.failure_rot_left = False
        self.failure_rot_right = False
        self.if_fast = False
        self.if_too_canted = False
    
    # If ship crashes runs ship explosion animation, plays explosion sound and respawns ship
    def death(self):
        if self.game.if_death_screen == False:
            self.death_animation = Explosion(self.game, self.rect.center, "ship")
            self.game.all_sprites.add(self.death_animation)
            self.game.start_ticks = pg.time.get_ticks()
        elif self.game.if_death_screen == True:
            self.game.show_death_screen()
        self.respwan()
   
    def check_failure(self):
        """Function that checks if there is any failures"""
        if self.failure_engine == True or\
           self.failure_rot_left == True or\
           self.failure_rot_right == True:
            return True
        return False
    
    def check_fuel(self):
        """Function that checks if there is zero fuel left"""
        if self.fuel <= 0:
            self.failure_engine = True
    
    def check_dmg(self):
        """Function that checks if ship's damage is less than 100"""
        if self.dmg_sustain >= 100:
            self._Failures.fatal_error()
    
    def check_speed(self):
        """Function that checks x's and y's velosity"""
        if self.vel.x * HEIGTADJUSTMENT >= 5 or self.vel.y * HEIGTADJUSTMENT >= 5:
            self.if_fast = True
        else:
            self.if_fast = False
    
    def check_rot(self):
        """Function that checks if ship is to cnated"""
        if self.rot > 10:
            if self.rot < 350:
                self.if_too_canted = True
        else:
            self.if_too_canted = False

    def colide_with_meteor(self, hits, dmg, spawn):
        """Function which adds dmg to ship, runs meteorit explosion animation and plys explosion sound"""
        for hit in hits:    
            choice(self.game.expl_sounds).play()
            self.expl = Explosion(self.game, hit.rect.center, "meteor")
            self.game.all_sprites.add(self.expl)
            self.dmg_sustain += dmg
            spawn()
    
    def colide_with_obsticle(self, hits, dmg):
        """Function which adds dmg to ship, runs obsticle explosion animation and plys explosion sound"""
        for hit in hits:    
            choice(self.game.expl_sounds).play()
            self.expl = Explosion(self.game, hit.rect.center, "obsticle")
            self.game.all_sprites.add(self.expl)
            self.dmg_sustain += dmg   

    def respwan(self):
        """Function that respawns the ship at the top of the screen"""
        self.rot = 0
        self.vel = vec(uniform(0, .625), uniform(-.625, .625))
        self.pos = vec(randrange(0, WIDTH), 0)
        if self.if_crashed == True:
            self.game.seconds = 0
            self.fuel = 1000
            self.dmg_sustain = 0
            self._Player.lives -= 1
            self.if_crashed = False
        self._Failures.fix()
        self.game.running = True
            
    def equation_of_motion(self):
        """Function that noves ship accros the screen"""
        self.vel.y += self.acc.y
        self.rect.center = self.pos
    
    def colide_with_window(self):
        """Function that checks if ship toched the window"""
        if self.rect.bottom > HEIGHT:
            self.if_crashed = True
            self.death()
            self.vel = vec(0, 0)
            self.acc = vec(0, 0)
            self.rot = 0
        if self.rect.centerx > WIDTH:
            self.pos.x = 0
        if self.rect.centerx < 0:
            self.pos.x = WIDTH
        if self.rect.centery < 0:
            self.pos.y = 0
            self.vel.y = 0
    
    def rotate_self(self):
        self.rot = (self.rot + self.rot_speed) % 360
        self.image = pg.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos 
    
    def update(self):
        # Checks if there is failure and if that the case plays failure sound
        if self.check_failure() == True:
            self.game.allert_sound.play()
        # Update Player
        self._Player.update()
        self.check_fuel()
        self.check_dmg()
        self.check_failure()
        self.check_rot()
        self.check_speed()
        self._Failures.upadate()        
        self.image = self.game.ship_img[0]
        self._Player.get_keys()
        self.equation_of_motion()
        self.rotate_self()
        self.colide_with_window()
        # Update position
        self.pos += self.vel + self.acc
        # Update position of a ship
        self.height = self.rect.bottom
        self.rect.center = self.pos            


class LandingPad(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.image = choice(game.landing_pads)
        self.rect = self.image.get_rect()
    
    def set_position(self):
        """Sets landing pad's position"""
        self.rect.bottom = HEIGHT
        self.rect.x = randrange(160, WIDTH - 160)
        if pg.sprite.spritecollide(self, self.game.landing_zones, True) == True:
            self.set_position()
    
    def overlap(self, ship):
        """Checks if ship has overlaped landing pad"""
        if HEIGHT - self.rect.height + 10 > ship.rect.bottom > HEIGHT - self.rect.height and\
           ship.rect.bottomleft >= self.rect.topleft and\
           ship.rect.bottomright <= self.rect.topright:
            return True
        return False


class _Mob(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
    
    def update(self):
        pass


class Obstacle(_Mob):
    def __init__(self, game):
        super().__init__(game)
        self.image = choice(game.obstacle_imgs)
        self.rect = self.image.get_rect()
    
    def set_position(self):
        """Function that sets obstacle's position on the screen"""
        self.pos = vec(randrange((self.rect.width), WIDTH - (self.rect.width)),\
                       randrange(200, HEIGHT - (self.rect.height)))
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        if pg.sprite.spritecollide(self, self.game.obstacles, True) == True:
            self.set_position()


class Meteor(_Mob):
    def __init__(self, game):
        super().__init__(game)
        self.image_orig = choice(self.game.meteor_imgs)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .9 / 2)
        # line below shows the collison of meteors
        #pg.draw.circle(self.image, GREEN, self.rect.center, self.radius)        
        self.rect.x = randrange(WIDTH-self.rect.width)
        self.rect.y = randrange(-100, -40)
        self.speedy = randrange(1, 3)
        self.speedx = randrange(-4, 4)
        self.rot = 0
        self.rot_speed = randrange(-8, 8)
        self.last_update = pg.time.get_ticks()        
    
    def rotate(self):
        """Function that rotates meteors while they travel accros the screen"""
        now = pg.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pg.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
    
    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # Make gravity influence meteors as well
        self.rect.y += self.speedy + GRAVITY/4
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or\
           self.rect.right > WIDTH + 25:
            self.rect.x = randrange(WIDTH-self.rect.width)
            self.rect.y = randrange(-100, -40)
            self.speedy = randrange(3, 6)    


class Explosion(pg.sprite.Sprite):
    def __init__(self, game, center, nature):
        super().__init__()
        self.nature = nature
        self.game = game
        self.image = self.game.explosion_animation[nature][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pg.time.get_ticks()
        self.frame_rate = 30
    
    def update(self):
        now = pg.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(self.game.explosion_animation[self.nature]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self.game.explosion_animation[self.nature][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center

if __name__ == "__main__":
    print("test")
    input()
