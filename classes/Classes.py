#  Author: Gordei Ussatsov
#  Date: 15 April 2019
#  Version: 3.0
#  Game classes

import pygame as pg
from math import cos, sin, radians
from random import randrange
from .config import *

class PartBase():
    # by default part is functional
    def __init__(self, ship):
        # every part has the var of a Ship() class
        self.ship = ship
        self._if_functional = 1

    def action(self):
        """
        [summary]
        Method that makes the part work
        """
        print('Yet to be emplimented')

    def fail(self, input):
        """
        [summary]
            Method that brakes the part
        Args:
            input (bool): [if input it breaks the part]
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
        self.ship.image = self.ship._game.ship_img[1]
        self.ship.fuel -= 5
        self.ship.vel.x += self.acc*sin(radians(-self.ship.rot))
        self.ship.vel.y -= self.acc*cos(radians(-self.ship.rot))
    

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
        self.ship.rot = (self.ship.rot + self.rot_speed) % 360


class RightAileron(AleronBase): 
    """
    [summary]
        Right aleron class can rotate ship to the right side
    """
    def __init__(self,ship):
        super().__init__(ship)
            
    def action(self):
        self.ship.rot = (self.ship.rot - self.rot_speed) % 360
    

class Player:
    """
    [summary]
        Player class represents player who has lives and score. Each player
        is assigned to it's ship
    """
    def __init__(self, ship, game):
        self.game = game
        self.ship = ship
        self.score = 0
        self.lives = 3
    
    def get_keys(self):
        """
        [summary]
            Function that gets an input from player
        """
        self.ship.rot_speed = 0
        self.ship.acc.y = GRAVITY        
        key_state = pg.key.get_pressed()
        # TODO WORK ON THE FAILURES
        # if space call thrust
        if key_state[pg.K_SPACE]:
            if self.ship._Engine._if_functional:
                self.ship._Engine.action()
        # if left arrow key call turn left from LeftAleron class
        if key_state[pg.K_LEFT]:
            if self.ship._LeftAileron._if_functional:
                self.ship._LeftAileron.action()
        # if right arrow key call turn right from RightAleron class
        if key_state[pg.K_RIGHT]:
            if self.ship._RightAileron._if_functional:
                self.ship._RightAileron.action()
    
    def if_scored(self):
        """
        [summary]
            Function which checks validity of landing i.e. if it moves too
            fast or to canted. If landing is successful. Game screen will
            get cleared and all the obsticles as well as landing pad
            will get created
        """
        landing = pg.sprite.spritecollide(self.ship,\
            self.game.landing_zones, False)
        for i in landing:
            if self.ship.if_too_canted == False and\
                self.ship.if_fast == False:
                    for i in self.game.landing_zones:
                        if i.overlap(self.ship) == True:                         
                            self.ship.respwan()
                            self.ship._Player.add_score()
                            for obj in self.game.obstacles:
                                obj.kill()
                            self.game.spawn_obstacles()                            
            else:
                self.ship.if_crashed = True
                self.ship.death()   
    
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
            img_rect = self.ship._game.mini_img.get_rect()
            img_rect.x = x + 60 * i
            img_rect.y = y
            surf.blit(self.ship._game.mini_img, img_rect)
    
    def update(self):
        """
        [summary]
            Checks if player has zero lives left and kills ship
            if that is the case
        """
        self.if_scored()
        if self.lives == 0:
            self.ship.kill()        

# class Failures():
#     def __init__(self, ship):
#         self.failure_list = ["engine", "rotation left", "rotation right"]
#         self.ship = ship
#         self.last_update = pg.time.get_ticks()
#         self.now = pg.time.get_ticks()
    
#     def engine_failure(self):
#         self.ship.failure_engine = True
    
#     def rot_left_failure(self):
#         self.ship.failure_rot_left = True
    
#     def rot_right_failure(self):
#         self.ship.failure_rot_right = True
        
#     def fix(self):
#         self.ship.failure_engine = False
#         self.ship.failure_rot_left = False
#         self.ship.failure_rot_right = False        
    
    # TODO TRANSFER TO SHIP CLASS
            
    # def appear(self):
    #     """Function that make failure appear"""
    #     if_failure = randrange(0, 100)
    #     if if_failure == 1:    
    #         self.now = pg.time.get_ticks()
    #         if self.ship.check_failure() == False:
    #             self.random_failure()

    # def fatal_error(self):
    #     self.engine_failure()
    #     self.rot_left_failure()
    #     self.rot_right_failure()
    
    # def random_failure(self):
    #     failure = randrange(0,3)
    #     if failure == 0:
    #         self.engine_failure()
    #     elif failure == 1:
    #         self.rot_left_failure()
    #     else:
    #         self.rot_right_failure()

    # def upadate(self):
    #     self.appear()
    #     self.now = pg.time.get_ticks()
    #     if self.now - self.last_update > 2000:
    #         self.last_update = self.now  
    #         self.fix()        


if __name__ == '__main__':
    e1 = Engine(1)
    print(e1._if_functional)
    e1.fail(0)
    print(e1._if_functional)
    e1.fail(1)
    print(e1._if_functional)
    e1.fix()
    print(e1._if_functional)
    e1.action()
