import pygame
import  sys
from pygame.locals import *
from pygame.sprite import Sprite, Group
from spritesheet import Sheet
from IPython import embed

agents = []
player = None

white = (255,255,255)
black = (0,0,0)
scale = 5
spriteimg = pygame.transform.scale(pygame.image.load('sprite1.png'), (int(32 * scale), int(32 * scale)))
DEFAULT_WIDTH = 1920
DEFAULT_HEIGHT = 1080
base_sprite_x = 150
base_sprite_y = 100
UPDATE_PLAYER = pygame.USEREVENT + 1
UPDATE_GAME = pygame.USEREVENT + 2
CAN_SHOOT = pygame.USEREVENT + 3

def get_sprites():
    sprite_locs = []
    invaders_sheet = Sheet('invaders.gif')
    sprite_locs.append((20, 14, 109, 80))
    sprite_locs.append((160, 15, 115, 80))
    sprite_locs.append((310, 15, 85, 80))
    images = invaders_sheet.images_at(sprite_locs, colorkey=(0,0,0,0))
    return images

def check_pressed():
    pressed = pygame.key.get_pressed()
    y = 0
    x = 0
    if pressed[pygame.K_UP]:
        y -= 1
    if pressed[pygame.K_DOWN]:
        y += 1
    if pressed[pygame.K_LEFT]:
        x -= 1
    if pressed[pygame.K_RIGHT]:
        x += 1
    return (x, y)


class Player(Sprite):
    def __init__(self, image = spriteimg, max_x=1920, max_y=1080, x=0, y=0, scale=1, movespeed=40):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.scale = scale
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.movespeed = movespeed

    def update(self, delta):
        x, y = check_pressed()
        if not (x is 0 and y is 0):
            self.x += x * self.movespeed * (delta/1000)
            self.y += y * self.movespeed * (delta/1000)
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)


class Invader(Sprite):
    def test(self):
        print("x")

    def __init__(self, image=spriteimg, max_x=1920, max_y=1080, x=0, y=0, scale=1):
        pygame.sprite.Sprite.__init__(self)
        self.scale = scale
        self.image = image
        self.max_x = max_x
        self.max_y = max_y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self):
        self.rect.x += 5*self.scale
        if self.rect.x >= self.max_x:
            self.rect.x = 0
            self.rect.y += 5*self.scale

    def getpos(self):
        return (self.x, self.y)

class GameState(object):
    def __init__(self):
        self.displaySize = (DEFAULT_WIDTH,DEFAULT_HEIGHT)
        self.displayInfo = None
        self.aliens = pygame.sprite.RenderUpdates()
        self.display = None
        self.bg = None
        self.sprites = None
        self.rows = 5
        self.cols = 7
        self.clock = pygame.time.Clock()
        self.scale = 3

class Game(GameState):
    def __init__(self):
        GameState.__init__(self)
        pygame.init()
        self.displayInfo = pygame.display.Info()
        self.displaySize = (self.displayInfo.current_w, self.displayInfo.current_h)
        self.display = pygame.display.set_mode(self.displaySize)
        self.display.fill(black)
        self.aliens = pygame.sprite.RenderUpdates()
        self.bg = pygame.Surface(self.displaySize)
        self.bg.fill(black)
        self.sprites = get_sprites()
        self.player = None
        self.pg = pygame.sprite.RenderUpdates()

    def loop(self):
        self.move_aliens()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    pygame.display.update()
                elif event.type == UPDATE_GAME:
                    self.move_aliens()

            #self.player.update(delta=self.clock.get_time())
            self.update_player()

            self.clock.tick()
            pygame.time.wait(20)
            print(self.player.rect)

    def run(self):
        self.setup_sprites()
        self.loop()

    def update_player(self):
        self.pg.clear(self.display, self.bg)
        self.pg.update(self.clock.get_time())
        pygame.display.update(self.pg.draw(self.display))


    def move_aliens(self):
        self.aliens.clear(self.display, self.bg)
        self.aliens.update()
        pygame.display.update(self.aliens.draw(self.display))
        pygame.time.set_timer(UPDATE_GAME, 500)

    def setup_sprites(self):
        self.player = Player(x=self.displaySize[0]//2, y=self.displaySize[1],
                             image=self.sprites[0])
        self.player.add(self.pg)
        offset = False
        for y in range(0, min(self.rows*base_sprite_y, self.displaySize[1]), base_sprite_y):
            for x in range(0, min(self.rows*base_sprite_x, self.displaySize[0]), base_sprite_x):
                if offset:
                    actualx = x + 75
                else:
                    actualx = x
                invader1 = Invader(image=self.sprites[0],
                                   y=y,
                                   scale=self.scale,
                                   x=actualx,
                                   max_x=self.displaySize[0],
                                   max_y=self.displaySize[1])
                invader1.add(self.aliens)
            offset = not offset

if __name__ == "__main__":
    x = Game()
    x.run()
