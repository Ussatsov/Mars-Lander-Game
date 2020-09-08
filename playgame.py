#  Author: Gordei Ussatsov
#  Date: 08 September 2020
#  Version: 4.0
#  Main file of the game

from pathlib import Path

import pygame as pg
from classes.config import *
from classes.Sprites import *
from classes.Classes import *
from random import randrange
from os import listdir


class Game():
    def __init__(self, death_screen):
        # This attribute should be True or False
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
        self.start_bg = pg.image.load(str(BACKGROUND_DIR / 'start.png')).convert()
        self.start_bg_rect = self.start_bg.get_rect()         
    
    def load_data(self):
        # Load all graphics
        self.bg = pg.image.load(str(BACKGROUND_DIR / 'game.png')).convert()
        self.bg_rect = self.bg.get_rect()
        self.obstacle_imgs = [pg.image.load(str(OBSTACLE_FOLDER / name)).convert_alpha()\
            for name in listdir(OBSTACLE_FOLDER)]
        self.meteor_imgs = [pg.image.load(str(METEORS_DIR / name)).convert_alpha()\
            for name in listdir(METEORS_DIR)]
        self.ship_img = [pg.image.load(str(SHIP_DIR / name)).convert_alpha()\
            for name in listdir(SHIP_DIR)]
        self.mini_img = pg.transform.scale(self.ship_img[0], (60, 43))
        self.landing_pads = [pg.image.load(str(LANDING_PADS_DIR / name)).convert_alpha()\
            for name in listdir(LANDING_PADS_DIR)]
        
        # Load explosion animation sprites
        self.explosion_animation = {}
        # Load explosion animation sprites for meteor
        self.explosion_animation["meteor"] = [pg.transform.scale(pg.image.load(str(EXPLOSIONS_DIR / name)).convert_alpha(), (50, 50))
                                            for name in listdir(EXPLOSIONS_DIR)]
        self.explosion_animation["obstacle"] = [pg.transform.scale(img, (80, 80))\
            for img in self.explosion_animation["meteor"]]
        # Load explosion animation sprites for ship
        self.explosion_animation["ship"] = [pg.image.load(str(SHIP_EXPLOSION / name)).convert_alpha()
                                            for name in listdir(SHIP_EXPLOSION)]
        
        # Load all sound effects and set their volume
        pg.mixer.music.load(str(SOUND_EFFECTS / BGMUSIC))
        pg.mixer.music.set_volume(.3)  
        self.allert_sound = pg.mixer.Sound(str(SOUND_EFFECTS / ALLERTSOUND))
        self.allert_sound.set_volume(.008)
        self.explosion_sounds = [pg.mixer.Sound(str(SOUND_EFFECTS / sound))\
            for sound in listdir(SOUND_EFFECTS) if sound in METEOR_EXPLOSION]
        
         # set the volume down
        for s in self.explosion_sounds:
            s.set_volume(.05)
    
    def if_end(self):
        """
        [summary]
            Method that checks if the game is still running
        """
        if not self.if_death_screen and self.My_ship._Player.lives ==  0 and\
           not self.My_ship.death_animation.alive():
            self.running = False
            self.playing = False
        if self.if_death_screen and self.My_ship._Player.lives ==  0:
            self.running = False
            self.playing = False        
    
    def spawn_landing_zones(self):
        """
        [summary]
            Spawn three landing zones
        """
        while len(self.landing_zones) < 3:
            landing_zone = LandingPad(self)
            landing_zone.set_position()
            self.all_sprites.add(landing_zone)
            self.landing_zones.add(landing_zone)
    
    def spawn_obstacles(self):
        """
        [summary]
            Method that spawns five to eight fixed obsticles on the screen
        """
        num = randrange(5, 8)
        while len(self.obstacles) < num:
            ob = Obstacle(self)
            ob.set_position()
            self.all_sprites.add(ob)
            self.obstacles.add(ob)
    
    def spawn_meteor(self):
        """
        [summary]
            Method that spawns a single meteor
        """
        m = Meteor(self)
        self.all_sprites.add(m)
        self.mobs.add(m)
    
    def draw_text(self, surf, text, size, x, y):
        """
        [summary]
            Method that draws text on the passed surface
        Args:
            surf (pg.screen): [where text should be drown]
            text (String): [text to draw]
            size (Int): [Size of the text]
            x (Int): [x coordinate of the right top corner of the text]
            y (Int): [y coordinate of the right top corner of the text]
        """
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, WHITE)
        text_rect = text_surface.get_rect()
        text_rect = (x, y)
        surf.blit(text_surface, text_rect)
    
    def write_all(self):
        """
        [summary]
            Method that write all the text to the game screen
        """
        # uncomment bellow and you will see tilt of the ship
        # useful for the debugging
        # self.draw_text(self.screen, f'{self.My_ship.rot}', 20, 400, 34)

        self.draw_text(self.screen, str("{0:.2f}".format(abs(self.My_ship.vel.y)*HEIGTADJUSTMENT)+"m/s"), 14, 280, 57)
        self.draw_text(self.screen, str("{0:.2f}".format(abs(self.My_ship.vel.x)*HEIGTADJUSTMENT)+"m/s"), 14, 280, 34)
        self.draw_text(self.screen, str("{0:.1f}".format(1000 - self.My_ship.height*HEIGTADJUSTMENT))+"m", 14, 260, 12)
        self.draw_text(self.screen, str("{0:.2f}".format(self.seconds)+"sec"), 14, 70, 12)
        self.draw_text(self.screen, str(self.My_ship._Player.score), 14, 70, 82)
        
        if self.My_ship.fuel > 0:
            self.draw_text(self.screen, f"{self.My_ship.fuel}kg", 14, 70, 34)
        if self.My_ship.fuel <= 0:
            self.draw_text(self.screen, "0kg", 14, 70, 34)
        if self.My_ship.dmg_sustain < 100:
            self.draw_text(self.screen, f"{self.My_ship.dmg_sustain}%", 14, 90, 57)
        if self.My_ship.dmg_sustain > 100:
            self.draw_text(self.screen, "100%", 14, 90, 57)
        
        if self.My_ship.check_failure() == True:
            self.draw_text(self.screen, "*ALERT*", 14, 200, 82)
        if not self.My_ship._Engine._if_functional:
            self.draw_text(self.screen, "!", 14, 300, 82)
        if not self.My_ship._RightAileron._if_functional:
            self.draw_text(self.screen, ">", 14, 310, 82)
        if not self.My_ship._LeftAileron._if_functional:
            self.draw_text(self.screen, "<", 14, 320, 82)    
    
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
        self.hits_obstacle = pg.sprite.spritecollide(self.My_ship, self.obstacles, True, pg.sprite.collide_circle)
        self.My_ship.colide_with_meteor (self.hits_meteor, METEORDMG, self.spawn_meteor)
        self.My_ship.colide_with_obstacle(self.hits_obstacle, OBSTICLEDMG)
            
        # If ship explode or ship has crashed then game ends
        self.if_end()

    
    def draw(self):
        """ Game loop - draw"""
        self.screen.blit(self.bg, self.bg_rect)
        self.all_sprites.draw(self.screen)
        self.My_ship._Player.draw_lives(self.screen, WIDTH-200, 25)
        self.write_all()
        pg.display.flip()    
    
    def new(self):
        """
        [summary]
            Method that initializes sprite groups and calls above functions to setup new game
        """
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
        """
        [summary]
            Method that shows start screen of the game
        """
        self.screen.blit(self.start_bg, (0, 0))
        self.draw_text(self.screen, "Mars Lander", 64, 10, 10)
        self.draw_text(self.screen, "Use arrow keys to rotate the ship and space to thrust",\
            22, 10, 90)
        self.draw_text(self.screen, "Successful landing earns you 50 points",\
            22, 10, 120)
        self.draw_text(self.screen, "Successful landing is when ship lands on a pad,",\
            22, 10, 150)
        self.draw_text(self.screen, "ship's x and y velocities are less than",\
            22, 10, 180)
        self.draw_text(self.screen, "five m/s and ship tilt is less than 10 degrees",\
            22, 10, 210)   
        self.draw_text(self.screen, "Press any key to begin",\
            18, 10, 240)
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
        """
        [summary]
            Method that shows death screen
        """
        self.draw_text(self.screen, "YOU HAVE CRASHED", 35, 400, 400)
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
        """
        [summary]
            Method that shows G/O screen
        """  
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
    # If True passed to the class constructor death
    # screen will be shown after ship crushes
    My_Game = Game(False)
    My_Game.show_start_screen()
    My_Game.new()
    My_Game.show_go_screen()
    
    pg.quit()
