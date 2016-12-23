import pygame
from random import choice
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

RAW_TIMESTEP = 500

def get_sprites():
    sprite_locs = []
    invaders_sheet = Sheet('invaders.gif')
    sprite_locs.append((20, 14, 109, 80))
    sprite_locs.append((160, 15, 115, 80))
    sprite_locs.append((310, 15, 85, 80))
    images = invaders_sheet.images_at(sprite_locs,colorkey=-1)

    projectile = []
    project_sheet = Sheet('projectile.png')
    for y in range(0,128,32):
        for x in project_sheet.load_strip((0, y, 32, 32), 4, colorkey=-1):
            projectile.append(x)
    for x in project_sheet.load_strip((0, 128, 32, 32), 1, colorkey=-1):
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

class SpritePropMix(object):
    @property
    def middle(self):
        return self.rect.x

    @property
    def top(self):
        return self.rect.y - self.rect.height/2


class Player(Sprite, SpritePropMix):
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

class Invader(Sprite, SpritePropMix):
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
    def __init__(self, spritepack=None, max_x=1920, max_y=1080, x=0, y=0, scale=1, movespeed=80,
                 color=(0,0,0)):
        pygame.sprite.Sprite.__init__(self)
        self.scale = scale
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

    def move(self, delta):
        self.y -= self.movespeed * (delta/1000) * self.scale
        self.rect.y = int(self.y)

    def update(self, delta, oob_check):
        self.image = self.sprites[self.count % len(self.sprites)]
        self.move(delta)
        self.count += 1
        oob_check(self)

class EnemyProjectile(Projectile):

    def move(self, delta):
        self.y += self.movespeed * (delta/1000) * self.scale
        self.rect.y = int(self.y)

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

class CountDown(object):
    def __init__(self, period):
        self.count = 0
        self.period = period
        self.isTime = False

    def incr(self):
        self.count += 1
        if self.count >= self.period:
            self.isTime = True
        else:
            self.isTime = False
        self.count = self.count % self.period

    def reset(self):
        self.count = 0

    def checkTime(self):
        return self.isTime is True

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
        self.playerprj = pygame.sprite.RenderUpdates()
        self.score = 0
        self.oldscore = -1
        self.font = pygame.font.SysFont('Arial', 30)
        self.score_text = None
        self.enemyprj = pygame.sprite.RenderUpdates()

        self.shootcounter = CountDown(5)
        self.count = 0

    def loop(self):
        self.move_aliens()
        self.update_player()
        while True:
            self.count += 1
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                    pygame.display.update()
                elif event.type == UPDATE_GAME:
                    self.move_aliens()
                    self.alien_shoots(3)
                    self.shootcounter.incr()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.shootcounter.checkTime():
                            self.shootcounter.reset()
                            self.player_fire()

            # Projectiles move more than the rest of things
            self.update_projectile()
            self.update_enemy_prj()
            self.update_player()
            self.update_score_display()

            self.clock.tick()
            pygame.time.wait(20)

    def player_fire(self):
        prj = Projectile(spritepack=self.projsprites,
                         x=self.player.middle,
                         y=self.player.top,
                         scale=self.player.scale,
                         color=(255,255,255))
        prj.add(self.playerprj)

    def enemy_fire(self, enemy):
        prj = EnemyProjectile(spritepack=self.projsprites,
                              x= enemy.middle, y=enemy.top,
                              scale=self.player.scale,
                              color=(255,255,0))
        prj.add(self.enemyprj)

    def run(self):
        self.setup_sprites()
        self.loop()

    def generate_score_text(self):
        self.score_text = self.font.render('Your Score: {}'.format(self.score), True, (255,0,0))

    def update_player(self):
        self.pg.clear(self.display, self.bg)
        self.pg.update(self.clock.get_time())
        pygame.display.update(self.pg.draw(self.display))


    def does_collide(self, x, y):
        a = pygame.sprite.collide_mask(x, y)
        if a:
            self.score += 100
            print(self.score)
        return a

    def enemy_proj_hit(self, x, y):
        a = pygame.sprite.collide_mask(x, y)
        if a:
            self.score -= 100
            print(self.score)
        return a

    def update_projectile(self):
        self.playerprj.clear(self.display, self.bg)
        self.playerprj.update(self.clock.get_time(), self.is_out_bounds)
        if pygame.sprite.groupcollide(self.playerprj, self.aliens, True, True, collided=self.does_collide):
            self.aliens.clear(self.display, self.bg)
            pygame.display.update(self.aliens.draw(self.display))
            self.playerprj.clear(self.display, self.bg)
        pygame.display.update(self.playerprj.draw(self.display))

    def update_enemy_prj(self):
        self.enemyprj.clear(self.display, self.bg)
        self.enemyprj.update(self.clock.get_time(), self.is_out_bounds)
        if pygame.sprite.groupcollide(self.enemyprj, self.pg, True, False, collided=self.enemy_proj_hit):
            self.enemyprj.clear(self.display, self.bg)
            self.enemyprj.update(self.clock.get_time())
        pygame.display.update(self.enemyprj.draw(self.display))

    def update_score_display(self):
        x = 0
        y = self.displaySize[1]-200
        if self.oldscore != self.score:
            self.generate_score_text()
        self.oldscore = self.score
        self.display.fill((0,0,0), (x, y, 300, 50))
        self.display.blit(self.score_text, (x, y))
        pygame.display.update()

    def move_aliens(self):
        self.aliens.clear(self.display, self.bg)
        self.aliens.update()
        pygame.display.update(self.aliens.draw(self.display))

        pygame.time.set_timer(UPDATE_GAME, int(RAW_TIMESTEP*.5))

    def alien_shoots(self, period):
        if self.count % period == 0:
            alienlist = list([x for x in self.aliens])
            shooting_alien = choice(alienlist)
            self.enemy_fire(shooting_alien)
        self.count = self.count % period

    def is_out_bounds(self, sprite):
        if 0 <= sprite.rect.x  <= self.displaySize[0] and 0 <= sprite.rect.y <= self.displaySize[1]:
            return False
        else:
            sprite.kill()
            return True


    def setup_sprites(self):
        self.player = Player(x=self.displaySize[0]//2, y=int(self.displaySize[1]//2*1.7),
                             image=self.charsprites[2], max_x=self.displaySize[0], max_y=self.displaySize[1],
                             scale=self.scale)
        self.player.add(self.pg)
        offset = False
        for y in range(0, min(self.rows*base_sprite_y, self.displaySize[1]), base_sprite_y):
            for x in range(0, min(self.rows*base_sprite_x, self.displaySize[0]), base_sprite_x):
                if offset:
                    actualx = x + 75
                else:
                    actualx = x
                invader1 = Invader(image=choice(self.charsprites),
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
