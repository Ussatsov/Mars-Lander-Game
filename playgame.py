#!/usr/bin/env python3

#  Author: Gordei Ussatsov
#  Date: 15 April 2019
#  Version: 3.0
#  Mars Lander main file

import pygame as pg
from settings import *
from sprites import *
from classes import *
from random import randrange
from os import path, listdir


class Game():
    def __init__(self, death_screen):
        # This atribute should be True or False
        # If it's True death screen would be demonstrated
        # If it's False instead explosion animation will be played
        self.if_death_screen = death_screen
        # initialize game window, start game back ground etc..
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption(TITLE)
        self.clock = pg.time.Clock()
        self.font_name = pg.font.match_font("arial black")
        self.running = True
        self.start_ticks = pg.time.get_ticks() #starter tick 
        self.start_bg = pg.image.load(path.join(path.join(path.dirname(__file__), IMGFILE), BACKGROUNDSTART)).convert()
        self.start_bg_rect = self.start_bg.get_rect()         
    
    def load_data(self):
        # Set gamesprites folders, so that program should run on any machine
        self.game_folder = path.dirname(__file__)
        self.main_folder = path.join(self.game_folder, IMGFILE)
        self.obstacle_folder = path.join(self.main_folder, OBSTICLEFOLDER)
        self.landing_pads_folder = path.join(self.main_folder, LANDINGPADFOLDER)
        self.meteor_folder = path.join(self.main_folder, METEORFOLDER)
        self.explosion_folder = path.join(self.main_folder, EXPLMETEOR)
        self.sound_folder = path.join(self.main_folder, SOUNDFOLDER)
        self.ship_explosion_folder = path.join(self.main_folder, EXPLSHIP)
        # Load all graphics
        self.bg = pg.image.load(path.join(self.main_folder, BACKGROUND)).convert()
        self.bg_rect = self.bg.get_rect()
        self.obstacle_imgs = [pg.image.load(path.join(self.obstacle_folder, img)).convert_alpha() for img in listdir(self.obstacle_folder)]
        self.meteor_imgs = [pg.image.load(path.join(self.meteor_folder, img)).convert_alpha() for img in listdir(self.meteor_folder)]
        self.ship_img = [pg.image.load(path.join(self.main_folder, img)).convert_alpha() for img in listdir(self.main_folder)
                         if img == THRUSTINGSHIP or img == NOTTHRUSTINGSHIP]
        self.mini_img = pg.transform.scale(self.ship_img[0], (60, 43))
        self.landing_pads = [pg.image.load(path.join(self.landing_pads_folder, img)).convert_alpha() for img in listdir(self.landing_pads_folder)]
        # Load explosion animation sprites
        self.explosion_animation = {}
        # Load explosion animation sprites for meteor
        self.explosion_animation["meteor"] = [pg.transform.scale(pg.image.load(path.join(self.explosion_folder, img)).convert_alpha(), (50, 50))
                                            for img in listdir(self.explosion_folder)]
        self.explosion_animation["obsticle"] = [pg.transform.scale(img, (80, 80)) for img in self.explosion_animation["meteor"]]
        # Load explosion animation sprites for ship
        self.explosion_animation["ship"] = [pg.image.load(path.join(self.ship_explosion_folder, img)).convert_alpha()
                                            for img in listdir(self.ship_explosion_folder)]
        
        # Load all sound effects and set their volume
        pg.mixer.music.load(path.join(self.sound_folder, BGMUSIC))
        pg.mixer.music.set_volume(.3)  
        self.allert_sound = pg.mixer.Sound(path.join(self.sound_folder, ALLERTSOUND))
        self.allert_sound.set_volume(.008)
        self.expl_sounds = [pg.mixer.Sound(path.join(self.sound_folder, sound))
                            for sound in listdir(self.sound_folder) if sound in EXPLSOUNDMETEOR]
        for sound in self.expl_sounds:
            sound.set_volume(.05)
    
    def if_end(self):
        if self.if_death_screen == False and self.My_ship._Player.lives ==  0 and\
           not self.My_ship.death_animation.alive():
            self.running = False
            self.playing = False
        
        if self.if_death_screen == True and self.My_ship._Player.lives ==  0:
            self.running = False
            self.playing = False        
    
    def spawn_landing_zones(self):
        """Function which spawns three fixed landing zones at the beginnig of the game"""
        while len(self.landing_zones) < 3:
            landing_zone = LandingPad(self)
            landing_zone.set_position()
            self.all_sprites.add(landing_zone)
            self.landing_zones.add(landing_zone)
    
    def spawn_obstacles(self):
        """Function which spawns five to eight fixed obsticles on the screen"""
        amount = randrange(5, 8)
        while len(self.obstacles) < amount:
            ob = Obstacle(self)
            ob.set_position()
            self.all_sprites.add(ob)
            self.obstacles.add(ob)
    
    def spawn_meteor(self):
        """Function which spawns one meteor"""
        m = Meteor(self)
        self.all_sprites.add(m)
        self.mobs.add(m)
    
    def draw_text(self, surf, text, size, x, y):
        """ Function that draws a text on the screen"""
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect = (x, y)
        surf.blit(text_surface, text_rect)
    
    def write_all(self):
        """ Function what writes all information on the screen"""
        self.draw_text(self.screen, str("{0:.2f}".format(abs(self.My_ship.vel.y)*HEIGTADJUSTMENT)+"m/s"), 14, 280, 57)
        self.draw_text(self.screen, str("{0:.2f}".format(abs(self.My_ship.vel.x)*HEIGTADJUSTMENT)+"m/s"), 14, 280, 34)
        self.draw_text(self.screen, str("{0:.1f}".format(1000 - self.My_ship.height*HEIGTADJUSTMENT))+"m", 14, 260, 12)
        self.draw_text(self.screen, str("{0:.2f}".format(self.seconds)+"sec"), 14, 70, 12)
        self.draw_text(self.screen, str(self.My_ship._Player.score), 14, 70, 82)
        
        if self.My_ship.fuel > 0:
            self.draw_text(self.screen, str(self.My_ship.fuel)+"kg", 14, 70, 34)
        if self.My_ship.fuel <= 0:
            self.draw_text(self.screen, "0kg", 14, 70, 34)
        if self.My_ship.dmg_sustain < 100:
            self.draw_text(self.screen, str(self.My_ship.dmg_sustain)+"%", 14, 90, 57)
        if self.My_ship.dmg_sustain > 100:
            self.draw_text(self.screen, "100%", 14, 90, 57)
        if self.My_ship.check_failure() == True:
            self.draw_text(self.screen, "*ALERT*", 14, 200, 82)
        if self.My_ship.failure_engine == True:
            self.draw_text(self.screen, "!", 14, 300, 82)
        if self.My_ship.failure_rot_left == True:
            self.draw_text(self.screen, "<", 14, 310, 82)
        if self.My_ship.failure_rot_right == True:
            self.draw_text(self.screen, ">", 14, 320, 82)    
    
    def events(self):
        """ Game loop - events"""
        for event in pg.event.get():
            if event.type == pg.QUIT:
                if self.playing:
                    pg.quit()
                    exit(0)
    
    def update(self):
        """ Game loop - update"""
        self.seconds = (pg.time.get_ticks()-self.start_ticks)/1000
        self.all_sprites.update()
        
        # Checks if meteor hit the ship or ship hit any obstacles
        self.hits_meteor = pg.sprite.spritecollide(self.My_ship, self.mobs, True, pg.sprite.collide_circle)
        self.hits_obsticle = pg.sprite.spritecollide(self.My_ship, self.obstacles, True, pg.sprite.collide_circle)
        self.My_ship.colide_with_meteor (self.hits_meteor, METEORDMG, self.spawn_meteor)
        self.My_ship.colide_with_obsticle(self.hits_obsticle, OBSTICLEDMG)
            
        # If ship explode and ship has crashed then game ends
        self.if_end()

    
    def draw(self):
        """ Game loop - draw"""
        self.screen.blit(self.bg, self.bg_rect)
        self.all_sprites.draw(self.screen)
        self.My_ship._Player.draw_lives(self.screen, WIDTH-200, 25)
        self.write_all()
        pg.display.flip()    
    
    def new(self):
        """Function which initilizes sprite groups and calls above functions to setup new game"""
        self.load_data()
        self.all_sprites = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.landing_zones = pg.sprite.Group()
        self.spawn_obstacles()
        self.spawn_landing_zones()
        self.My_ship = Ship(self)
        self.all_sprites.add(self.My_ship)
        for i in range(randrange(5, 10)):
            self.spawn_meteor()             
        self.run()
    
    def run(self):
        """Function which runs game"""
        pg.mixer.music.play(loops=-1)
        # Game Loop
        self.playing = True 
        while self.playing:
            while self.running:
                self.clock.tick(FPS)
                self.events()
                self.update()
                self.draw()
    
    def show_start_screen(self):
        """ Function that shows start screen of the game"""
        self.screen.blit(self.start_bg, (0, 0))
        self.draw_text(self.screen, "Mars Lander", 64, 10, 10)
        self.draw_text(self.screen, "Arrow keys to rotate, Space to thrust", 22,\
                       10, 90)
        self.draw_text(self.screen, "Successful landing gives 50 points", 22,\
                       10, 120)
        self.draw_text(self.screen, "Successful landing: ship lands on a pad,", 22,\
                       10, 150)
        self.draw_text(self.screen, "ship's x and y velocities are less than five m/s and", 22,\
                       10, 180)
        self.draw_text(self.screen, "ship tilt is less than 10 degrees", 22,\
                       10, 210)        
        self.draw_text(self.screen, "Press any key to begin", 18, 10, 240)
        pg.display.flip()
        
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit(0)
                if event.type == pg.KEYUP:
                    waiting = False
    
    def show_death_screen(self):  
        """ Function that shows death screen"""
        self.draw_text(self.screen, "YOU HAVE CRACHED", 35, 400, 400)
        self.draw_text(self.screen, "press any key to continue", 25, 420, 440)
        
        pg.display.flip()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit(0)
                if event.type == pg.KEYUP:
                    waiting = False        
    
    def show_go_screen(self):
        """ Function that shows G/O screen"""    
        self.screen.blit(self.start_bg, (0, 0))          
        self.draw_text(self.screen, "Game Over", 35, 250, 300)
        self.draw_text(self.screen, "Your score is: %d"%(self.My_ship._Player.score), 35, 200, 340)
        pg.display.flip()
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    exit(0)


if __name__ == "__main__":
    pg.init()
    # If True passed to the class cunstructor death
    # screen will be shown after ship crushes
    My_Game = Game(False)
    My_Game.show_start_screen()
    My_Game.new()
    My_Game.show_go_screen()
    
    pg.quit()
