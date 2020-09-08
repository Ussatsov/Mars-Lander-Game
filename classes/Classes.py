#  Author: Gordei Ussatsov
#  Date: 08 September 2020
#  Version: 4.0
#  Game classes

import pygame as pg
from math import cos, sin, radians
from random import randrange
from .config import *

class PartBase():
    # by default part is functional
    def __init__(self, ship):
        # every part has the var of a Ship() class
        self._Ship = ship
        self._if_functional = 1

    def action(self):
        """
        [summary]
        Method that makes the part work
        """
        print('Yet to be emplimented')

    def fail(self):
        """
        [summary]
            Method that brakes the part
        """
        self._if_functional = 0

    def fix(self):
        """
        [summary]
            Method that fixes part
        """
        self._if_functional = 1
    
class Engine(PartBase):
    """
    [summary]
    Class that simulates engine of the ship    
    """
    def __init__(self, ship):
        super().__init__(ship)
        self.acc = ENGINE_ACC
    
    def action(self):
        """
        [summary]
        Method that changes ship image from no thrust to ship with a 
        When called. It also subtracts fuel from the tank and 
        calculates x and y speed
        """
        self._Ship.image = self._Ship._Game.ship_img[1]
        self._Ship.fuel -= 5
        self._Ship.vel.x += self.acc*sin(radians(-self._Ship.rot))
        self._Ship.vel.y -= self.acc*cos(radians(-self._Ship.rot))
    

class AleronBase(PartBase):
    """
    [summary]
        Base aleron class inherited from the PartBase classes
        This is a meta class and have no use in the program
    """
    def __init__(self, ship):
        super().__init__(ship)
        self.rot_speed = SHIP_ROT_SPEED


class LeftAileron(AleronBase):
    """
    [summary]
        Left aleron class can rotate ship to the left side
    """
    def __init__(self,ship):
        super().__init__(ship)
            
    def action(self):
        self._Ship.rot = (self._Ship.rot + self.rot_speed) % 360


class RightAileron(AleronBase): 
    """
    [summary]
        Right aleron class can rotate ship to the right side
    """
    def __init__(self,ship):
        super().__init__(ship)
            
    def action(self):
        self._Ship.rot = (self._Ship.rot - self.rot_speed) % 360
    

class Player:
    """
    [summary]
        Player class represents player who has lives and score. Each player
        is assigned to it's ship
    """
    def __init__(self, ship, game):
        self.game = game
        self._Ship = ship
        self.score = 0
        self.lives = 3
    
    def get_keys(self):
        """
        [summary]
            Function that gets an input from player
        """
        self._Ship.rot_speed = 0
        self._Ship.acc.y = GRAVITY        
        key_state = pg.key.get_pressed()
        # if space call thrust
        if key_state[pg.K_SPACE]:
            if self._Ship._Engine._if_functional:
                self._Ship._Engine.action()
        # if left arrow key call turn left from LeftAleron class
        if key_state[pg.K_LEFT]:
            if self._Ship._LeftAileron._if_functional:
                self._Ship._LeftAileron.action()
        # if right arrow key call turn right from RightAleron class
        if key_state[pg.K_RIGHT]:
            if self._Ship._RightAileron._if_functional:
                self._Ship._RightAileron.action()
    
    def if_scored(self):
        """
        [summary]
            Function which checks validity of landing i.e. if it moves too
            fast or to canted. If landing is successful. Game screen will
            get cleared and all the obsticles as well as landing pad
            will get created
        """
        landing = pg.sprite.spritecollide(self._Ship,\
            self.game.landing_zones, False)
        for i in landing:
            if self._Ship.if_too_canted == False and\
                self._Ship.if_fast == False:
                    for i in self.game.landing_zones:
                        if i.overlap(self._Ship) == True:                         
                            self._Ship.respwan()
                            self._Ship._Player.add_score()
                            for obj in self.game.obstacles:
                                obj.kill()
                            self.game.spawn_obstacles()                            
            else:
                self._Ship.if_crashed = True
                self._Ship.death()   
    
    def add_score(self):
        """
        [summary]
            Method that increments player score by some value
        """
        self.score += LANDING_POINTS
    
    def draw_lives(self, surf, x, y):
        """
        [summary]
            Method that draws player life on the screen 
        Args:
            surf (game screen): [main game screen]
            x (int): [x coordinate]
            y (int): [y coordinate]
        """
        for i in range(self.lives):
            # get the mini image of the ship and then draw the left lives
            img_rect = self._Ship._Game.mini_img.get_rect()
            img_rect.x = x + 60 * i
            img_rect.y = y
            surf.blit(self._Ship._Game.mini_img, img_rect)
    
    def update(self):
        """
        [summary]
            Checks if player has zero lives left and kills ship
            if that is the case
        """
        self.if_scored()
        if self.lives == 0:
            self._Ship.kill()        
