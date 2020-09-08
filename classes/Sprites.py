#  Author: Gordei Ussatsov
#  Date: 08 September 2020
#  Version: 4.0
#  Game classes with sprites

import pygame as pg
from math import cos, sin, radians
from random import randrange, choice, uniform
from .Classes import *
from .config import *


class Ship(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self._Game = game
        self.image = self._Game.ship_img[0]
        self.rect = self.image.get_rect()
        self.radius = 25
        self._Player = Player(self, self._Game)
        self._Engine = Engine(self)
        self._RightAileron = RightAileron(self)
        self._LeftAileron = LeftAileron(self)
        # self._Failures = Failures(self)        
        self.pos = pg.math.Vector2(randrange(0, WIDTH), 0)
        self.vel = pg.math.Vector2(uniform(0, .625), uniform(-.625, .625))
        self.acc = pg.math.Vector2(0, 0)
        self.fuel = FUEL_AMOUNT
        self.rot = 0
        self.dmg_sustain = 0
        self.height = self.rect.bottom
        self.if_crashed = False
        self.if_fast = False
        self.if_too_canted = False
        # For random failures
        self.last_update = pg.time.get_ticks()
        self.now = pg.time.get_ticks()
        self.failed_module = None
    
    def death(self):
        """
        [summary]
            Method that simulates ship crash. Explosion animation and sound are played
            Then run method that respowns ship at the top 
        """
        if  self._Game.if_death_screen:
            self._Game.show_death_screen()
        elif not  self._Game.if_death_screen:
            self.death_animation = Explosion(self._Game, self.rect.center, "ship")
            self._Game.all_sprites.add(self.death_animation)
            self._Game.start_ticks = pg.time.get_ticks()
        self.respwan()
   
    def check_failure(self):
        """
        [summary]
            Method that checks if something is broken in the ship
        Returns:
            [Bool]: [if there are any failures returns true else false]
        """
        if not self._Engine._if_functional or\
           not self._RightAileron._if_functional or\
           not self._LeftAileron._if_functional:
           return True
        return False
    
    def check_fuel(self):
        """
        [summary]
            Method that checks if there is enough fuel left in the tank
            if not it runs Engine.fail() method
        """
        if self.fuel <= 0:
            self._Engine.fail()
    
    def check_dmg(self):
        """
        [summary]
            Method that if ship is completely damaged all systems
            will fail: Run .fail() of all componets
        """
        if self.dmg_sustain >= 100:
            self._Engine.fail()
            self._RightAileron.fail()
            self._LeftAileron.fail()
    
    def check_speed(self):
        """
        [summary]
            Method that checks if ship is falling too fast and can crash
            during the landing
        """
        if self.vel.x * HEIGTADJUSTMENT >= 5 or\
            self.vel.y * HEIGTADJUSTMENT >= 5:
            self.if_fast = True
        else:
            self.if_fast = False
    
    def check_rot(self):
        """
        [summary]
            Method that Checks if the ship is too canted.
            If ship lands like that it will crash
        """
        if self.rot > 10 and self.rot < 350:
            self.if_too_canted = True
        else:
            self.if_too_canted = False

    def colide_with_meteor(self, hits, dmg, spawn):
        """
        [summary]
            Method which adds dmg to ship, runs meteorite explosion
            animation and plays explosion sound
        Args:
            hits ([list]): [list of collisions]
            dmg (int): [what is the damage that has to be added to ship's sustained damage]
            spawn (function): [respawns the meteor that was hit by the ship]
        """
        for hit in hits:    
            choice(self._Game.explosion_sounds).play()
            self.expl = Explosion(self._Game, hit.rect.center, "meteor")
            self._Game.all_sprites.add(self.expl)
            self.dmg_sustain += dmg
            spawn()
    
    def colide_with_obstacle(self, hits, dmg):
        """
        [summary]
            Method which adds dmg to ship, runs obstacle explosion
            animation and plays explosion sound
        Args:
            hits ([list]): [list of collisions]
            dmg (int): [what is the damage that has to be added to ship's sustained damage]
        """
        for hit in hits:    
            choice(self._Game.explosion_sounds).play()
            self.expl = Explosion(self._Game, hit.rect.center, "obstacle")
            self._Game.all_sprites.add(self.expl)
            self.dmg_sustain += dmg   

    def random_failure(self):
        """
        [summary]
            Method that makes random failure appear
        """
        failure = randrange(0,3)
        if failure == 0:
            self._Engine.fail()
            self.failed_module = 0
        elif failure == 1:
            self.failed_module = 1
            self._RightAileron.fail()
        else:
            self._LeftAileron.fail()
            self.failed_module = 2

    def failure_appear(self):
        """
        [summary]
            Method that makes a failure appear
        """
        if_failure = randrange(0, 100)
        if if_failure == 1:    
            self.now = pg.time.get_ticks()
            if not self.check_failure():
                self.random_failure()

    def update_failure(self):
        self.failure_appear()
        self.now = pg.time.get_ticks()
        if self.now - self.last_update > 1000:
            self.last_update = self.now  
            if self.failed_module == 0:
                self._Engine.fix()
            elif self.failed_module == 1:
                self._RightAileron.fix()
            elif self.failed_module == 2:
                self._LeftAileron.fix()

    def respwan(self):
        """
        [summary]
            Method that resets ship if it crashed. It also decrements
            Player lives
        """
        self.rot = 0
        self.vel = pg.math.Vector2(uniform(0, .625), uniform(-.625, .625))
        self.pos = pg.math.Vector2(randrange(0, WIDTH), 0)
        if self.if_crashed == True:
            self._Game.seconds = 0
            self.fuel = FUEL_AMOUNT
            self.dmg_sustain = 0
            self._Player.lives -= 1
            self.if_crashed = False
        # Fix all the failures
        self._Engine.fix()
        self._LeftAileron.fix()
        self._RightAileron.fix()
        self._Game.running = True
            
    def equation_of_motion(self):
        """
        [summary]
            Method that moves ship sprite across the screen
        """
        self.vel.y += self.acc.y
        self.rect.center = self.pos
    
    def rotate_self(self):
        """
        [summary]
            Method that rotates ship image
        """
        self.rot = (self.rot + self.rot_speed) % 360
        self.image = pg.transform.rotate(self.image, self.rot)
        self.rect = self.image.get_rect()
        self.rect.center = self.pos

    def colide_with_window(self):
        """
        [summary]
            Method that checks if the ship colades with the frame of the screen
            and does according transforamtions or doesn't allow ship to go up
        """
        if self.rect.bottom > HEIGHT:
            self.if_crashed = True
            self.death()
            self.vel = pg.math.Vector2(0, 0)
            self.acc = pg.math.Vector2(0, 0)
            self.rot = 0
        if self.rect.centerx > WIDTH:
            self.pos.x = 0
        if self.rect.centerx < 0:
            self.pos.x = WIDTH
        if self.rect.centery < 0:
            self.pos.y = 0
            self.vel.y = 0
    
    def update(self):
        """
        [summary]
            Method that runs an update for ship
        """
        # Checks if there is failure and if that the case plays failure sound
        if self.check_failure():
            self._Game.allert_sound.play()
        # Update Player
        self._Player.update()
        self.check_fuel()
        self.check_dmg()
        self.check_rot()
        self.check_speed()
        self.image = self._Game.ship_img[0]
        self._Player.get_keys()
        self.equation_of_motion()
        self.rotate_self()
        self.colide_with_window()
        # Update position
        self.pos += self.vel + self.acc
        # Update position of a ship
        self.height = self.rect.bottom
        self.rect.center = self.pos
        # Make random failures appear
        self.update_failure()


class LandingPad(pg.sprite.Sprite):
    def __init__(self, game):
        super().__init__()
        self._Game = game
        self.image = choice(self._Game.landing_pads)
        self.rect = self.image.get_rect()
    
    def set_position(self):
        """
        [summary]
            Method that sets position of the landing pads
        """
        self.rect.bottom = HEIGHT
        self.rect.x = randrange(160, WIDTH - 160)
        if pg.sprite.spritecollide(self, self._Game.landing_zones, True):
            self.set_position()
    
    def overlap(self, ship):
        """
        [summary]
            Method that checks if the ship colades with the landing pad
        Args:
            ship (Ship Type): check if this ship collides with the landing pad

        Returns:
            [Bool]: [If given ship colides with the pad return true else false]
        """
        if HEIGHT - self.rect.height + 10 > ship.rect.bottom > HEIGHT - self.rect.height and\
           ship.rect.bottomleft >= self.rect.topleft and\
           ship.rect.bottomright <= self.rect.topright:
            return True
        return False


class _Mob(pg.sprite.Sprite):
    def __init__(self, _Game):
        super().__init__()
        self._Game = _Game
    
    def update(self):
        pass


class Obstacle(_Mob):
    def __init__(self, _Game):
        super().__init__(_Game)
        self.image = choice(_Game.obstacle_imgs)
        self.rect = self.image.get_rect()
    
    def set_position(self):
        """
        [summary]
            Method that sets the position of that obstacle
        """
        self.pos = pg.math.Vector2(randrange((self.rect.width), WIDTH - (self.rect.width)),\
            randrange(200, HEIGHT - (self.rect.height)))
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        if pg.sprite.spritecollide(self, self._Game.obstacles, True):
            self.set_position()


class Meteor(_Mob):
    def __init__(self, _Game):
        super().__init__(_Game)
        self.image_orig = choice(self._Game.meteor_imgs)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .9 / 2)
        self.rect.x = randrange(WIDTH-self.rect.width)
        self.rect.y = randrange(-100, -40)
        self.speedy = randrange(1, 3)
        self.speedx = randrange(-4, 4)
        self.rot = 0
        self.rot_speed = randrange(-8, 8)
        self.last_update = pg.time.get_ticks()        
    
    def rotate(self):
        """
        [summary]
            Method that makes meteors rotate while the travel accross the screen
        """
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
    def __init__(self, _Game, center, nature):
        super().__init__()
        self.nature = nature
        self._Game = _Game
        self.image = self._Game.explosion_animation[nature][0]
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
            if self.frame == len(self._Game.explosion_animation[self.nature]):
                self.kill()
            else:
                center = self.rect.center
                self.image = self._Game.explosion_animation[self.nature][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center
