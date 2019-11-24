#!/usr/bin/env python3

#  Author: Gordei Ussatsov
#  Date: 15 April 2019
#  Version: 3.0
#  Game classes

import pygame as pg
from settings import *
from math import cos, sin, radians
from random import randrange


class Player:
    def __init__(self, ship, game):
        self.game = game
        self.ship = ship
        self.score = 0
        self.lives = 3
    
    def get_keys(self):
        """Function that gets an input from player"""
        self.ship.rot_speed = 0
        self.ship.acc.y = GRAVITY        
        key_state = pg.key.get_pressed()
        if key_state[pg.K_SPACE]:
            if not self.ship.failure_engine:
                self.ship._Engine.thrust()
        if key_state[pg.K_LEFT]:
            if not self.ship.failure_rot_left:
                self.ship.rot_speed = SHIP_ROT_SPEED
        if key_state[pg.K_RIGHT]:
            if not self.ship.failure_rot_right:
                self.ship.rot_speed = -SHIP_ROT_SPEED
    
    def if_scored(self):
        """Function which checks validity of landing a.k.a if it moves too fast or to canted
        If landing is successful all fixed obsticles will be delited and 'spawn_obsticles' 
        will be called"""
        landing = pg.sprite.spritecollide(self.ship, self.game.landing_zones, False)
        for i in landing:
            if self.ship.if_too_canted == False and self.ship.if_fast == False:
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
        """Function that adds 50 points to playr score"""
        self.score += 50
    
    def draw_lives(self, surf, x, y):
        """Function that draws player lives on top right corner"""
        for i in range(self.lives):
            img_rect = self.ship.game.mini_img.get_rect()
            img_rect.x = x + 60 * i
            img_rect.y = y
            surf.blit(self.ship.game.mini_img, img_rect)
    
    def update(self):
        # Checks if player has zero lives left and kills ship if that is the case
        self.if_scored()
        if self.lives == 0:
            self.ship.kill()        
          

class Engine():
    def __init__(self, ship):
        self.ship = ship
        self.acc = ENGINE_ACC
    
    def thrust(self):
        """Function that moves ship"""
        self.ship.image = self.ship.game.ship_img[1]
        self.ship.fuel -= 5
        self.ship.vel.x += self.acc*sin(radians(-self.ship.rot))
        self.ship.vel.y -= self.acc*cos(radians(-self.ship.rot))





class Failures():
    def __init__(self, ship):
        self.failure_list = ["engine", "rotation left", "rotation right"]
        self.ship = ship
        self.last_update = pg.time.get_ticks()
        self.now = pg.time.get_ticks()
    
    def engine_failure(self):
        self.ship.failure_engine = True
    
    def rot_left_failure(self):
        self.ship.failure_rot_left = True
    
    def rot_right_failure(self):
        self.ship.failure_rot_right = True
        
    def fix(self):
        self.ship.failure_engine = False
        self.ship.failure_rot_left = False
        self.ship.failure_rot_right = False        
    
    def appear(self):
        """Function that make failure appear"""
        if_failure = randrange(0, 100)
        if if_failure == 1:    
            self.now = pg.time.get_ticks()
            if self.ship.check_failure() == False:
                self.random_failure()
            
    def fatal_error(self):
        self.engine_failure()
        self.rot_left_failure()
        self.rot_right_failure()
    
    def random_failure(self):
        failure = randrange(0,3)
        if failure == 0:
            self.engine_failure()
        elif failure == 1:
            self.rot_left_failure()
        else:
            self.rot_right_failure()

    def upadate(self):
        self.appear()
        self.now = pg.time.get_ticks()
        if self.now - self.last_update > 2000:
            self.last_update = self.now  
            self.fix()        
