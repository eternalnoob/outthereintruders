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

    projectile = []
    project_sheet = Sheet('projectile.png')
    for y in range(0,128,32):
        for x in project_sheet.load_strip((0, y, 32, 32), 4, colorkey=(0,0,0,0)):
            projectile.append(x)

    for x in project_sheet.load_strip((0, 128, 32, 32), 1, colorkey=(0,0,0,0)):
        projectile.append(x)

    return {"chars": images, "projspr": projectile}

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
    def __init__(self, image=spriteimg, max_x=1920, max_y=1080, x=0, y=0, scale=1, movespeed=60):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.scale = scale
        self.image = image
        self.max_x = max_x
        self.max_y = max_y
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.movespeed = movespeed

    def update(self, delta):
        x, y = check_pressed()
        if not (x is 0 and y is 0):
            self.x += x * self.movespeed * (delta/1000) * self.scale
            self.y += y * self.movespeed * (delta/1000) * self.scale
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)

    def getpos(self):
        return (self.rect.x, self.rec.y)

    @property
    def middle(self):
        return self.rect.x

    @property
    def top(self):
        return self.rect.y - self.rect.height/2



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

class Projectile(Sprite):
    def __init__(self, spritepack=None, max_x=1920, max_y=1080, x=0, y=0, scale=1, movespeed=80):
        pygame.sprite.Sprite.__init__(self)
        self.scale = scale
        print(scale)
        self.sprites = []
        for img in spritepack:
            self.sprites.append(pygame.transform.scale(img, (int(img.get_rect().width*self.scale), int(img.get_rect(
            ).height*self.scale))))
        self.max_x = max_x
        self.max_y = max_y
        self.rect = self.sprites[0].get_rect()
        self.y = y
        self.x = y
        self.rect.x = x
        self.rect.y = y
        self.count = 0
        self.movespeed = movespeed

    def update(self, delta):
        self.image = self.sprites[self.count % len(self.sprites)]
        self.y -= self.movespeed * (delta/1000) * self.scale
        self.rect.y = int(self.y)
        self.count += 1

class GameState(object):
    def __init__(self):
        self.displaySize = (DEFAULT_WIDTH,DEFAULT_HEIGHT)
        self.displayInfo = None
        self.aliens = pygame.sprite.RenderUpdates()
        self.display = None
        self.bg = None
        self.charsprites = None
        self.rows = 5
        self.cols = 7
        self.clock = pygame.time.Clock()
        self.scale = 3
        self.pg = pygame.sprite.RenderUpdates()

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
        sprites = get_sprites()
        self.charsprites = sprites['chars']
        self.projsprites = sprites['projspr']
        self.player = None
        self.pg = pygame.sprite.RenderUpdates()
        self.allsprites = pygame.sprite.RenderUpdates()
        self.playerprj = pygame.sprite.RenderUpdates()

    def loop(self):
        self.move_aliens()
        self.update_player()
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    pygame.display.update()
                elif event.type == UPDATE_GAME:
                    self.move_aliens()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        prj = Projectile(spritepack=self.projsprites,
                                         x=self.player.middle,
                                         y=self.player.top,
                                         scale=self.player.scale)
                        prj.add(self.playerprj)

            self.update_projectile()
            self.update_player()
            #self.player.update(delta=self.clock.get_time())

            self.clock.tick()
            pygame.time.wait(20)

    def run(self):
        self.setup_sprites()
        self.loop()

    def update_player(self):
        self.pg.clear(self.display, self.bg)
        self.pg.update(self.clock.get_time())
        pygame.display.update(self.pg.draw(self.display))


    def update_projectile(self):
        self.playerprj.clear(self.display, self.bg)
        self.playerprj.update(self.clock.get_time())
        pygame.display.update(self.playerprj.draw(self.display))
        pygame.sprite.groupcollide(self.playerprj, self.aliens, True, True, collided=pygame.sprite.collide_mask)

    def move_aliens(self):
        self.aliens.clear(self.display, self.bg)
        self.aliens.update()
        pygame.display.update(self.aliens.draw(self.display))
        pygame.time.set_timer(UPDATE_GAME, 500)

    def setup_sprites(self):
        self.player = Player(x=self.displaySize[0]//2, y=self.displaySize[1]//2*1.7,
                             image=self.charsprites[2], max_x=self.displaySize[0], max_y=self.displaySize[1],
                             scale=self.scale)
        self.player.add(self.pg)
        self.player.add(self.allsprites)
        offset = False
        for y in range(0, min(self.rows*base_sprite_y, self.displaySize[1]), base_sprite_y):
            for x in range(0, min(self.rows*base_sprite_x, self.displaySize[0]), base_sprite_x):
                if offset:
                    actualx = x + 75
                else:
                    actualx = x
                invader1 = Invader(image=self.charsprites[0],
                                   y=y,
                                   scale=self.scale,
                                   x=actualx,
                                   max_x=self.displaySize[0],
                                   max_y=self.displaySize[1])
                invader1.add(self.aliens)
                invader1.add(self.allsprites)
            offset = not offset

if __name__ == "__main__":
    x = Game()
    x.run()
