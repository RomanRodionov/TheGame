import pygame
import random
import time

xw = 1131
yw = 707
pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() > 0:
    joy = pygame.joystick.Joystick(0)
    joy.init()
else:
    class Joy:
        def get_button(self, _):
            return False

        def get_hat(self, _):
            return None

        def get_axis(self, _):
            return 0


    joy = Joy()

pygame.mixer.init()
window = pygame.display.set_mode((xw, yw))

pygame.display.set_caption("Guardians of the Galaxy - Starlord Adventures")

max_count_enemy = 5
normal = (0, 0)
hero_health = 5
max_hero_health = 5
max_enemy_health = 5
downLine = 138
damage_bul = 1
damage_att = 3
kills_to_boss = 1  ###

w = 128
h = 128
x = 150
lastx = x
y = yw - h - downLine
speed = 10
g = 4
jumpSpeed = 25
lastMove = 'right'
plasmaSpeed = 25
enemySpeed = 2
fenatt = 5  ## Отталкивание персонажа ударом бота
fhatt = 7  ## Отталкивание бота ударом персонажа
kills = 0

play = True

jump = False
hit = False
attack = False
gunattack = False
hitcircle = 0
attackcircle = 0
circlekills = 0
k = 0
k1 = 0

start_s = pygame.mixer.Sound('Sounds/start.wav')
start_s.set_volume(0.1)
pause1_s = pygame.mixer.Sound('Sounds/pause1.wav')
pause1_s.set_volume(0.1)
bg_menu = pygame.image.load('bgmenu.png')
logo = pygame.image.load("logo.png")

clock = pygame.time.Clock()

animCount = 0  # Счетчик последовательности анимации персонажа при ходьбе

enemyAnimCount = 0  # Счетчик последовательности анимации бота при ходьбе

guncount = 20

all_sprites = pygame.sprite.Group()

def history(pic):
    color_of_text = (124, 252, 0)
    window.blit(pic, (0, 0))
    font = pygame.font.Font(None, 36)
    skip_text = font.render('Press SPACE to skip', True, color_of_text)
    window.blit(skip_text, (870, 670))
    show = True
    while show:
        keys = pygame.key.get_pressed()
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    show = False
            if keys[pygame.K_KP_ENTER] or pygame.mouse.get_pressed()[0] or joy.get_button(
                    6) or joy.get_button(7) or keys[pygame.K_ESCAPE]:
                show = False
        pygame.display.update()



def end():
    win_sound.play()
    congratulation.play()
    k1 = 0
    white = [255, 255, 255]
    font = pygame.font.Font(None, 60)
    font2 = pygame.font.Font(None, 100)
    text1 = font.render("{}, congratulations!".format(player_name), True, white)
    text2 = font.render("You defeated the boss and won the game!", True, white)
    text3 = font.render("Your time:", True, white)
    text4 = font2.render(result, True, white)
    bg_coords = [0, xw]
    while True:

        clock.tick(30)
        k1 += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        for x in range(2):
            window.blit(bg_menu, (bg_coords[x], 0))
            bg_coords[x] -= 3

        if bg_coords[0] < -xw:
            bg_coords = [0, xw]

        window.blit(text1, [350, 130])
        window.blit(text2, [170, 200])
        window.blit(text3, [170, 300])
        window.blit(text4, [400, 285])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] or keys[pygame.K_KP_ENTER] or pygame.mouse.get_pressed()[0] or joy.get_button(
                6) or joy.get_button(7):
            pause1_s.play()
            break

        pygame.display.update()


def draw_health():  # Отображение hp персонажа
    global hero_health, max_hero_health
    for x in range(max_hero_health):
        if x + 1 <= hero_health:
            window.blit(health, (192 + x * 50, 0))
        else:
            window.blit(diehealth, (192 + x * 50, 0))
    if boss:
        for x in range(10):
            if x + 1 <= boss_en.health:
                window.blit(boss_health, (885 - x * 50, 130))
            else:
                window.blit(diehealth, (885 - x * 50, 130))


def draw_time():
    result = round(time.clock() - start_time - pause_time)
    result = str(result // 60) + ' min ' + str(result % 60) + ' sec'
    font = pygame.font.Font(None, 40)
    text = font.render(result, True, (255, 255, 255))
    window.blit(text, (500, 10))


class Particle(pygame.sprite.Sprite):
    fire = [pygame.image.load('b.png')]
    for scale in (9, 12, 22):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.screen_rect = (pos[0] - 75, pos[1] - 400, 140, 400)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = 1

    def update(self):
        self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(self.screen_rect):
            self.kill()


def create_particles(position):
    particle_count = 20
    ny = range(-20, 5)
    nx = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(nx), random.choice(ny))


class Enemy:
    def __init__(self, x, y, speed, health):
        self.x = x
        self.y = y
        self.speed = speed
        self.left = False
        self.right = False
        self.health = health
        self.hurt = False
        self.attack = False
        self.hurtcircle = 0
        self.attackcircle = 0
        self.diecircle = 0
        self.last_attack = 0

    def move(self, x):
        if not (self.attack):
            if x < self.x:
                self.x -= self.speed
                self.left = True
                self.right = False
            elif x > self.x:
                self.x += self.speed
                self.left = False
                self.right = True

    def draw(self, window, image):
        window.blit(image, (self.x, self.y))

    def attack(self, x, y):
        if not (self.hurt):
            self.attack = True


class Plasma:
    def __init__(self, x, y, side):
        self.side = side
        if side < 0:
            self.x = x - 95
        else:
            self.x = x + 65
        self.y = y - 7
        self.speed = plasmaSpeed * side

    def draw(self, window, bullet):
        window.blit(bullet, (self.x, self.y))


class Fire:
    def __init__(self, x, y, window):
        self.window = window
        self.x = x
        self.y = y
        self.sp1 = pygame.image.load('fire1.png')
        self.sp2 = pygame.image.load('fire2.png')

    def draw(self, k):
        if k % 8 < 4:
            window.blit(self.sp1, (self.x, self.y))
        else:
            window.blit(self.sp2, (self.x, self.y))


class Boss(Enemy):
    crl = [
        pygame.image.load('boss/PNG/crl1.png'),
        pygame.image.load('boss/PNG/crl2.png'),
        pygame.image.load('boss/PNG/crl3.png'),
        pygame.image.load('boss/PNG/crl4.png')
    ]
    crr = [
        pygame.image.load('boss/PNG/crr1.png'),
        pygame.image.load('boss/PNG/crr2.png'),
        pygame.image.load('boss/PNG/crr3.png'),
        pygame.image.load('boss/PNG/crr4.png')
    ]
    runl = [
        pygame.image.load('boss/PNG/runl1.png'),
        pygame.image.load('boss/PNG/runl2.png'),
        pygame.image.load('boss/PNG/runl3.png'),
        pygame.image.load('boss/PNG/runl4.png'),
        pygame.image.load('boss/PNG/runl5.png'),
        pygame.image.load('boss/PNG/runl6.png')
    ]
    runr = [
        pygame.image.load('boss/PNG/runr1.png'),
        pygame.image.load('boss/PNG/runr2.png'),
        pygame.image.load('boss/PNG/runr3.png'),
        pygame.image.load('boss/PNG/runr4.png'),
        pygame.image.load('boss/PNG/runr5.png'),
        pygame.image.load('boss/PNG/runr6.png')
    ]
    boom = [
        pygame.image.load('boom/1.png'),
        pygame.image.load('boom/2.png'),
        pygame.image.load('boom/3.png'),
        pygame.image.load('boom/4.png'),
        pygame.image.load('boom/5.png'),
        pygame.image.load('boom/6.png')
    ]
    hitl = [
        pygame.image.load('boss/PNG/hitl1.png'),
        pygame.image.load('boss/PNG/hitl2.png')
    ]
    hitr = [
        pygame.image.load('boss/PNG/hitr1.png'),
        pygame.image.load('boss/PNG/hitr2.png')
    ]
    stayl = pygame.image.load('boss/PNG/stayl.png')
    stayr = pygame.image.load('boss/PNG/stayr.png')
    plane = pygame.image.load('plane.png')
    bomb = pygame.image.load('bomb.png')
    animCount = 0
    crCount = 0
    pic = 3
    k = 0
    left = True
    change_pos = False
    pos = 'right'
    last_ga = -1
    bullets = []
    ga = 0
    w = 128
    h = 128
    crouch = False
    time_cr = 0
    bombs = []
    bb = []
    dam = False
    go = True
    get_dam = False
    die = False
    end = False
    bomb_s = pygame.mixer.Sound('Sounds/bomb.wav')
    bomb_s.set_volume(0.1)
    boss_attack = pygame.mixer.Sound('Sounds/boss_attack.wav')
    boss_attack.set_volume(0.1)
    boss_hit = pygame.mixer.Sound('Sounds/boss_hit.wav')
    boss_hit.set_volume(0.1)

    def move(self, x):
        if self.health <= 0:
            self.die = True
        if self.go:
            self.x -= 8
            if self.x <= 850:
                self.go = False
                self.attack = True
                self.boss_attack.play()
        if not (self.change_pos):
            if x < self.x:
                self.left = True
                self.side = -1
            else:
                self.left = False
                self.side = 1
        self.k += 1
        if self.attack:
            for r in range(len(self.bombs)):
                self.bombs[r][0] += 2
                self.bombs[r][1] += 15
            self.ga += 1
            if self.ga % 20 == 0:
                self.bombs.append([self.ga * 10 - 276, 80])
            if self.ga > 170:
                self.attack = False
                self.crouch = True
                self.get_dam = True
                self.ga = 0
        if self.die:
            self.x += 8
            if self.x >= 1400:
                self.end = True
        elif self.crouch:
            self.time_cr += 1
            if self.time_cr >= 150 and not (self.hurt):
                self.crouch = False
                self.time_cr = 0
                self.change_pos = True
        if self.change_pos:
            if self.pos == 'right':
                self.x -= self.speed
                if self.x <= 180:
                    self.change_pos = False
                    self.attack = True
                    self.boss_attack.play()
                    self.pos = 'left'
            else:
                self.x += self.speed
                if self.x + w >= 951:
                    self.change_pos = False
                    self.attack = True
                    self.pos = 'right'
        for r in range(len(self.bb)):
            if self.bb[r][1] < 5:
                self.bb[r][1] += 1
            else:
                del self.bb[r]
        bombs_del = []
        if len(self.bombs) > 0:
            for r in range(len(self.bombs)):
                if self.bombs[r][1] >= 480:
                    create_particles((self.bombs[r][0] + 64, self.bombs[r][1] + 64))
                    self.bomb_s.play()
                    if ((x <= self.bombs[r][0] and (x + 128 >= self.bombs[r][0])) or (
                                    x >= self.bombs[r][0] and (x <= self.bombs[r][0] + 80))) and self.y + 50 > \
                            self.bombs[r][1]:
                        self.dam = True
                    self.bombs[r][1] -= 30
                    self.bb.append([self.bombs[r], 0])
                    bombs_del.append(r)
                    break
        for r in bombs_del:
            del self.bombs[r]

    def draw(self, window, image):
        if self.hurt:
            self.hurtcircle += 1
            if self.hurtcircle <= 3:
                self.hit_pic = 0
            else:
                self.hit_pic = 1
            if self.hurtcircle == 30:
                self.hurtcircle = 0
                self.hurt = False
                self.crouch = False
                self.change_pos = True
                self.time_cr = 0
        if self.k % self.pic == 0:
            self.animCount = (self.animCount + 1) % 6
        if self.k % self.pic == 0:
            self.crCount = (self.crCount + 1) % 4
        if self.hurt:
            if self.left:
                window.blit(self.hitl[self.hit_pic], (self.x, self.y))
            else:
                window.blit(self.hitr[self.hit_pic], (self.x, self.y))
        elif self.die:
            window.blit(self.runr[self.animCount], (self.x, self.y))
        elif self.change_pos or self.go:
            if self.pos == 'right':
                window.blit(self.runl[self.animCount], (self.x, self.y))
            else:
                window.blit(self.runr[self.animCount], (self.x, self.y))
        elif self.crouch:
            if self.left:
                window.blit(self.crl[self.crCount], (self.x, self.y))
            else:
                window.blit(self.crr[self.crCount], (self.x, self.y))
        else:
            if self.left:
                window.blit(self.stayl, (self.x, self.y))
            else:
                window.blit(self.stayr, (self.x, self.y))
        for x in self.bb:
            window.blit(self.boom[x[1]], (x[0][0], x[0][1]))
        for x in self.bombs:
            window.blit(self.bomb, (x[0], x[1]))
        if self.attack:
            window.blit(self.plane, (self.ga * 10 - 636, -20))

    def hit(self):
        if self.health <= 0:
            self.die = True
        elif self.crouch:
            self.boss_hit.play()
            self.hurt = True

    def attack_check(self):
        a = self.dam
        self.dam = False
        return a


class Rock:
    def __init__(self, x, y, window, im, zombie):
        self.window = window
        self.x = x
        self.y = y
        self.im = im
        self.zombie = zombie
        self.make = False
        self.k = 0
        self.chance = (300, 250, 275, 325)
        self.time = random.choice(self.chance)

    def draw(self, enemies, max_count_enemy):
        self.k += 1
        if self.k >= self.time and max_count_enemy > len(enemies):
            self.k = 0
            self.time = random.choice(self.chance)
            self.make = True
        if self.make:
            self.window.blit(self.zombie, (self.x, 555 - self.k))
        if self.k >= 83 and self.make:
            self.make = False
            enemies.append(Enemy(self.x, yw - 91 - downLine, enemySpeed, max_enemy_health))
        self.window.blit(self.im, (self.x, self.y))


bg_coords = [-xw, 0]


def drawWindow():
    global animCount, enemyAnimCount, normal, die_en, bg_coords, boss

    window.blit(bg, (0, 0))
    for rock in rocks_t:
        rock.draw(enemies, max_count_enemy)
    window.blit(ground, (0, 555))

    for z in range(2):
        window.blit(sky, (bg_coords[z], 0))
        bg_coords[z] += 1

    window.blit(tree2, (-50, 158))
    window.blit(tree1, (830, 165))

    if bg_coords[0] > 0:
        bg_coords = [-xw, 0]

    if animCount + 1 >= 30:
        animCount = 0

    if enemyAnimCount + 1 >= 30:
        enemyAnimCount = 0

    delete_en = []

    for en in die_en:
        if en.diecircle < 11:
            if en.left:
                en.draw(window, zombie_dieLeft[en.diecircle // 2])
            else:
                en.draw(window, zombie_dieRight[en.diecircle // 2])
        elif en.diecircle > 10 and en.diecircle < 100:
            if en.left:
                en.draw(window, zombie_dieLeft[5])
            else:
                en.draw(window, zombie_dieRight[5])
        else:
            delete_en.append(en)

    for en in delete_en:
        if en in die_en:
            die_en.pop(die_en.index(en))

    for en in enemies:
        if en.hurt:
            if en.left:
                en.draw(window, zombie_hurtLeft[en.hurtcircle])
            else:
                en.draw(window, zombie_hurtRight[en.hurtcircle])
        elif en.attack:
            if en.left:
                en.draw(window, zombie_attackLeft[en.attackcircle // 2])
            else:
                en.draw(window, zombie_attackRight[en.attackcircle // 2])
        elif en.left:
            en.draw(window, zombieLeft[enemyAnimCount // 5])
        else:
            en.draw(window, zombieRight[enemyAnimCount // 5])

    if boss:
        for fire in fires:
            fire.draw(k1)

    if (non_damcircle % 4 > 1) or non_damage == False:
        if hit:
            if lastMove == 'left':
                window.blit(hitLeft[hitcircle // 2], (x, y))
            else:
                window.blit(hitRight[hitcircle // 2], (x, y))
        elif gunattack:
            if lastMove == 'right':
                window.blit(gunright[lastgunattack // 2 - 1], (x, y))
            else:
                window.blit(gunleft[lastgunattack // 2 - 1], (x, y))
        elif attack:
            if attackcircle <= 6:
                ac = attackcircle // 3
            else:
                ac = 2
            if lastMove == 'right':
                window.blit(attackright[ac], (x, y))
            else:
                window.blit(attackleft[ac], (x, y))
        elif jump:
            if lastMove == 'right':
                window.blit(jumpRight, (x, y))
            else:
                window.blit(jumpLeft, (x, y))
        elif left:
            window.blit(runLeft[animCount // 5], (x, y))
            animCount += 1
        elif right:
            window.blit(runRight[animCount // 5], (x, y))
            animCount += 1
        elif lastMove == 'right':
            window.blit(starlordright, (x, y))
        elif lastMove == 'left':
            window.blit(starlordleft, (x, y))

    for bullet in bullets:
        bullet.draw(window, bullet_image)

    if not (boss):
        pygame.draw.rect(window, (160, 30, 160), [70, 650, 1000, 20])
        if kills <= kills_to_boss:
            pygame.draw.rect(window, (50, 160, 160), [70, 650, 1000 // kills_to_boss * kills, 20])
        else:
            pygame.draw.rect(window, (50, 160, 160), [70, 650, 1000, 20])
        pygame.draw.rect(window, (165, 165, 165), [73, 652, 994, 5])
        pygame.draw.rect(window, (225, 225, 225), [73, 652, 994, 3])
        window.blit(boss_head, (1050, 600))
        if kills <= kills_to_boss:
            window.blit(headicon, (1000 // kills_to_boss * kills - 20, 580))
        else:
            window.blit(headicon, (1000 - 20, 580))

    if boss:
        boss_en.draw(window, None)

    window.blit(bgicon, (0, 0))
    window.blit(bodyicon, (0, 0))

    if boss:
        window.blit(boss_bgicon, (939, 0))
        window.blit(boss_bodyicon, (939, 0))

    if k1 % 12 == 0:
        normal = [0, 1]
    elif k1 % 8 == 0:
        normal = [0, 0]
    elif k1 % 4 == 0:
        normal = [0, 2]
    window.blit(headicon, normal)
    if boss:
        window.blit(boss_headicon, [939, normal[1] * 2])

    draw_health()
    draw_time()
    all_sprites.update()
    all_sprites.draw(window)

    pygame.display.update()


def drawTrainingWindow():
    global animCount, enemyAnimCount, normal, bg_coords

    window.blit(bgsh, (0, 0))

    if animCount + 1 >= 30:
        animCount = 0

    if (non_damcircle % 4 > 1) or non_damage == False:
        if hit:
            if lastMove == 'left':
                window.blit(hitLeft[hitcircle // 2], (x, y))
            else:
                window.blit(hitRight[hitcircle // 2], (x, y))
        elif gunattack:
            if lastMove == 'right':
                window.blit(gunright[lastgunattack // 2 - 1], (x, y))
            else:
                window.blit(gunleft[lastgunattack // 2 - 1], (x, y))
        elif attack:
            if attackcircle <= 6:
                ac = attackcircle // 3
            else:
                ac = 2
            if lastMove == 'right':
                window.blit(attackright[ac], (x, y))
            else:
                window.blit(attackleft[ac], (x, y))
        elif jump:
            if lastMove == 'right':
                window.blit(jumpRight, (x, y))
            else:
                window.blit(jumpLeft, (x, y))
        elif left:
            window.blit(runLeft[animCount // 5], (x, y))
            animCount += 1
        elif right:
            window.blit(runRight[animCount // 5], (x, y))
            animCount += 1
        elif lastMove == 'right':
            window.blit(starlordright, (x, y))
        elif lastMove == 'left':
            window.blit(starlordleft, (x, y))

    for bullet in bullets:
        bullet.draw(window, bullet_image)

    window.blit(advices[hint], (100, 80))
    window.blit(skip_text, (870, 670))
    if hint == 0:
        window.blit(arl, (490, 20))
        window.blit(arr, (580, 20))
    if hint == 1:
        window.blit(arup, (490, 20))
    if hint == 2:
        window.blit(zbut, (490, 20))
    if hint == 3:
        window.blit(xbut, (490, 20))

    pygame.display.update()


bg = pygame.image.load('bg.png')
bgsh = pygame.image.load('bgsh.png')
bg_die = [
    bg,
    pygame.image.load('bg1.png'),
    pygame.image.load('bg2.png'),
    pygame.image.load('bg3.png'),
    pygame.image.load('bg4.png'),
    pygame.image.load('bg5.png')]
sky = pygame.image.load('sky.png')
tree1 = pygame.image.load('tree1.png')
tree2 = pygame.image.load('tree2.png')
bullet_image = pygame.image.load('bullet.png')
bgicon = pygame.image.load("bgicon.jpg")
bodyicon = pygame.image.load("bodyicon.png")
headicon = pygame.image.load("headicon.png")
boss_head = pygame.image.load("Boss/PNG/head.png")
health = pygame.image.load("health.png")
diehealth = pygame.image.load("diehealth.png")
pygame.mixer.music.load('Sounds/soundtrack.ogg')
attack_s = pygame.mixer.Sound('Sounds/attack.wav')
attack_s.set_volume(0.1)
gunattack_s = pygame.mixer.Sound('Sounds/gunattack.wav')
gunattack_s.set_volume(0.06)
pause0_s = pygame.mixer.Sound('Sounds/pause0.wav')
pause0_s.set_volume(0.1)
hill_s = pygame.mixer.Sound('Sounds/hill.wav')
hill_s.set_volume(0.3)
hit_s = pygame.mixer.Sound('Sounds/hit.wav')
hit_s.set_volume(0.1)
win_sound = pygame.mixer.Sound('Sounds/win.wav')
win_sound.set_volume(0.1)
congratulation = pygame.mixer.Sound('Sounds/congratulation.wav')
congratulation.set_volume(0.1)
zombie_attack = pygame.mixer.Sound('Sounds/zombie_attack.wav')
zombie_attack.set_volume(0.1)
zombie_hit = pygame.mixer.Sound('Sounds/zombie_hit.wav')
zombie_hit.set_volume(0.1)
ground = pygame.image.load("ground.png")
hist1 = pygame.image.load("hist1.png")
hist2 = pygame.image.load("hist2.png")
hist3 = pygame.image.load("hist3.png")
rocks = [
    pygame.image.load("rock1.png"),
    pygame.image.load("rock2.png"),
    pygame.image.load("rock3.png")
]
runLeft = [
    pygame.image.load("Star Lord/PNG/runleft1.png"),
    pygame.image.load("Star Lord/PNG/runleft2.png"),
    pygame.image.load("Star Lord/PNG/runleft3.png"),
    pygame.image.load("Star Lord/PNG/runleft4.png"),
    pygame.image.load("Star Lord/PNG/runleft5.png"),
    pygame.image.load("Star Lord/PNG/runleft6.png")
]
runRight = [
    pygame.image.load("Star Lord/PNG/runright1.png"),
    pygame.image.load("Star Lord/PNG/runright2.png"),
    pygame.image.load("Star Lord/PNG/runright3.png"),
    pygame.image.load("Star Lord/PNG/runright4.png"),
    pygame.image.load("Star Lord/PNG/runright5.png"),
    pygame.image.load("Star Lord/PNG/runright6.png")
]
hitLeft = [
    pygame.image.load("Star Lord/PNG/hitleft1.png"),
    pygame.image.load("Star Lord/PNG/hitleft2.png")
]
hitRight = [
    pygame.image.load("Star Lord/PNG/hitright1.png"),
    pygame.image.load("Star Lord/PNG/hitright2.png")
]
staying = pygame.image.load("Star Lord/PNG/frontal.png")
starlordleft = pygame.image.load("Star Lord/PNG/starlordleft.png")
starlordright = pygame.image.load("Star Lord/PNG/starlordright.png")
jumpLeft = pygame.image.load("Star Lord/PNG/jumpleft.png")
jumpRight = pygame.image.load("Star Lord/PNG/jumpright.png")
gunleft = [
    pygame.image.load("Star Lord/PNG/gunleft1.png"),
    pygame.image.load("Star Lord/PNG/gunleft2.png"),
    pygame.image.load("Star Lord/PNG/gunleft3.png")
]
gunright = [
    pygame.image.load("Star Lord/PNG/gunright1.png"),
    pygame.image.load("Star Lord/PNG/gunright2.png"),
    pygame.image.load("Star Lord/PNG/gunright3.png")
]
attackleft = [
    pygame.image.load("Star Lord/PNG/lattack1.png"),
    pygame.image.load("Star Lord/PNG/lattack2.png"),
    pygame.image.load("Star Lord/PNG/lattack3.png")
]
attackright = [
    pygame.image.load("Star Lord/PNG/rattack1.png"),
    pygame.image.load("Star Lord/PNG/rattack2.png"),
    pygame.image.load("Star Lord/PNG/rattack3.png")
]
zombieLeft = [
    pygame.image.load("Zombie/Walk/left1.png"),
    pygame.image.load("Zombie/Walk/left2.png"),
    pygame.image.load("Zombie/Walk/left3.png"),
    pygame.image.load("Zombie/Walk/left4.png"),
    pygame.image.load("Zombie/Walk/left5.png"),
    pygame.image.load("Zombie/Walk/left6.png")
]
zombieRight = [
    pygame.image.load("Zombie/Walk/right1.png"),
    pygame.image.load("Zombie/Walk/right2.png"),
    pygame.image.load("Zombie/Walk/right3.png"),
    pygame.image.load("Zombie/Walk/right4.png"),
    pygame.image.load("Zombie/Walk/right5.png"),
    pygame.image.load("Zombie/Walk/right6.png")
]
zombie_hurtRight = [
    pygame.image.load("Zombie/Hurt/right1.png"),
    pygame.image.load("Zombie/Hurt/right2.png"),
    pygame.image.load("Zombie/Hurt/right3.png"),
    pygame.image.load("Zombie/Hurt/right4.png"),
    pygame.image.load("Zombie/Hurt/right5.png"),
    pygame.image.load("Zombie/Hurt/right6.png")
]
zombie_hurtLeft = [
    pygame.image.load("Zombie/Hurt/left1.png"),
    pygame.image.load("Zombie/Hurt/left2.png"),
    pygame.image.load("Zombie/Hurt/left3.png"),
    pygame.image.load("Zombie/Hurt/left4.png"),
    pygame.image.load("Zombie/Hurt/left5.png"),
    pygame.image.load("Zombie/Hurt/left6.png")
]
zombie_attackRight = [
    pygame.image.load("Zombie/Attack/right1.png"),
    pygame.image.load("Zombie/Attack/right2.png"),
    pygame.image.load("Zombie/Attack/right3.png"),
    pygame.image.load("Zombie/Attack/right4.png"),
    pygame.image.load("Zombie/Attack/right5.png"),
    pygame.image.load("Zombie/Attack/right6.png")]
zombie_attackLeft = [
    pygame.image.load("Zombie/Attack/left1.png"),
    pygame.image.load("Zombie/Attack/left2.png"),
    pygame.image.load("Zombie/Attack/left3.png"),
    pygame.image.load("Zombie/Attack/left4.png"),
    pygame.image.load("Zombie/Attack/left5.png"),
    pygame.image.load("Zombie/Attack/left6.png")
]
zombie_dieRight = [
    pygame.image.load("Zombie/Die/right1.png"),
    pygame.image.load("Zombie/Die/right2.png"),
    pygame.image.load("Zombie/Die/right3.png"),
    pygame.image.load("Zombie/Die/right4.png"),
    pygame.image.load("Zombie/Die/right5.png"),
    pygame.image.load("Zombie/Die/right6.png")
]
zombie_dieLeft = [
    pygame.image.load("Zombie/Die/left1.png"),
    pygame.image.load("Zombie/Die/left2.png"),
    pygame.image.load("Zombie/Die/left3.png"),
    pygame.image.load("Zombie/Die/left4.png"),
    pygame.image.load("Zombie/Die/left5.png"),
    pygame.image.load("Zombie/Die/left6.png")
]
arl = pygame.image.load("arl.png")
arr = pygame.image.load("arr.png")
arup = pygame.image.load("arup.png")
xbut = pygame.image.load("x.png")
zbut = pygame.image.load("z.png")
boss_bgicon = pygame.image.load('bgicon2.jpg')
boss_headicon = pygame.image.load("headicon2.png")
boss_bodyicon = pygame.image.load("bodyicon2.png")
boss_health = pygame.image.load("health2.png")


def input_name(screen):
    bg = pygame.image.load('bgt.jpg')
    font = pygame.font.Font(None, 46)
    clock = pygame.time.Clock()
    input_box = pygame.Rect(445, 315, 180, 40)
    color_inactive = (255, 160, 122)
    color_active = (255, 99, 71)
    color_of_text = (124, 252, 0)
    color = color_inactive
    active = False
    text = ''

    while True:
        screen.blit(bg, (0, 0))
        textrect = font.render(text, True, color_of_text)
        t = font.render('YOUR NAME:', True, color_of_text)
        width = max(220, textrect.get_width() + 10)
        input_box.w = width
        screen.blit(textrect, (input_box.x + 5, input_box.y + 5))
        screen.blit(t, (455, 270))
        pygame.draw.rect(screen, color, input_box, 2)

        pygame.display.flip()
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if text != '':
                        return text
                    else:
                        return 'player'
                if active:
                    if event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode


def start_window():
    global k1, bg_coords, pause
    white = [255, 255, 255]
    font = pygame.font.Font(None, 50)
    text = font.render("Press space to play", True, white)
    pause0_s.play()
    time = 0
    while True:

        clock.tick(30)
        k1 += 1
        time += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        for x in range(2):
            window.blit(bg_menu, (bg_coords[x], 0))
            bg_coords[x] -= 3

        if bg_coords[0] < -xw:
            bg_coords = [0, xw]

        window.blit(logo, [50, 100])

        if not (k1 % 30 > 15):
            window.blit(text, [400, 570])

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_SPACE] or keys[pygame.K_KP_ENTER] or pygame.mouse.get_pressed()[0] or joy.get_button(
                6) or joy.get_button(7) or keys[pygame.K_ESCAPE]) and time > 5:
            pause1_s.play()
            break

        pygame.display.update()


def pause():
    global k1, bg_coords, pause, pause_time
    white = [255, 255, 255]
    font = pygame.font.Font(None, 50)
    text = font.render("Press space to continue", True, white)
    pygame.mixer.music.pause()
    time = 0
    while True:

        clock.tick(30)
        k1 += 1
        time += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        for x in range(2):
            window.blit(bg_menu, (bg_coords[x], 0))
            bg_coords[x] -= 3

        if bg_coords[0] < -xw:
            bg_coords = [0, xw]

        if not (k1 % 30 > 15):
            window.blit(text, [400, 570])

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_SPACE] or keys[pygame.K_KP_ENTER] or pygame.mouse.get_pressed()[0] or joy.get_button(
                6) or joy.get_button(7) or keys[pygame.K_ESCAPE]) and time > 5:
            pause1_s.play()
            break

        pygame.display.update()


def die():
    global x, y, play
    play = False
    white = [255, 255, 255]
    font = pygame.font.Font(None, 50)
    text = font.render("GAME OVER", True, white)
    pygame.mixer.music.stop()
    time = 0
    k = 0
    while True:

        clock.tick(30)
        time += 1

        y += -25 + 1 * k
        k += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        if time // 10 < 5:
            window.blit(bg_die[time // 10], (0, 0))
        else:
            break

        window.blit(staying, (x, y))

        window.blit(text, [450, 50])

        if time // 10 > 10:
            pygame.quit()

        pygame.display.update()


def leaderboard():
    bg = pygame.image.load('bgt.jpg')
    with open('leaderboard.txt', 'a') as file:
        file.write(player_name + '$' + str(round(time.clock() - start_time - pause_time)) + '\n')
    board = [line.rstrip('\n').split('$') for line in open('leaderboard.txt', 'r').readlines()]
    for n in range(len(board)):
        board[n] = (int(board[n][1]), board[n][0])
    board.sort()
    board = board[:10]
    color = (255, 160, 122)
    color1 = (255, 99, 71)
    color2 = (124, 252, 0)
    font = pygame.font.Font(None, 50)
    font1 = pygame.font.Font(None, 36)
    text = font.render("LEADERBOARD", True, color2)
    while True:
        window.blit(bg, (0, 0))
        window.blit(text, (350, 50))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        for n in range(len(board)):
            time1 = str(board[n][0] // 60) + ' min ' + str(board[n][0] % 60) + ' sec'
            text1 = font1.render(board[n][1], True, color)
            text2 = font1.render(time1, True, color1)
            window.blit(text1, (100, n * 30 + 200))
            window.blit(text2, (650, n * 30 + 200))

        keys = pygame.key.get_pressed()

        if (keys[pygame.K_SPACE] or keys[pygame.K_KP_ENTER] or pygame.mouse.get_pressed()[0] or joy.get_button(
                6) or joy.get_button(7) or keys[pygame.K_ESCAPE]):
            break

        clock.tick(30)
        pygame.display.update()


while True:  # главный цикл
    pygame.mixer.music.stop()
    pygame.mixer.music.load('Sounds/music.ogg')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.4)
    player_name = input_name(window)
    start_window()
    history(hist1)
    y = yw - h - downLine + 2
    lastMove = 'right'
    plasmaSpeed = 25
    enemySpeed = 2
    kills = 0
    hero_health = max_hero_health
    pygame.mixer.music.set_volume(0.3)

    play = True

    jump = False
    hit = False
    attack = False
    gunattack = False
    non_damage = False
    non_damcircle = 0
    hitcircle = 0
    attackcircle = 0
    circlekills = 0
    k = 0
    k1 = 0
    animCount = 0  # Счетчик последовательности анимации персонажа при ходьбе

    enemyAnimCount = 0  # Счетчик последовательности анимации бота при ходьбе

    guncount = 20
    left = False
    right = False
    boss = False
    jumps = 0
    lastgunattack = 0
    lastpause = 0
    bullets = []  # Количество снарядов на экране
    enemies = []  # Количество ботов на экране
    rem_bul = []
    die_en = []
    rocks_t = [Rock(230, 497, window, rocks[0], zombie_dieRight[1]),
               Rock(440, 500, window, rocks[1], zombie_dieRight[1]),
               Rock(820, 500, window, rocks[2], zombie_dieLeft[1])]
    color_of_text = (124, 252, 0)
    font = pygame.font.Font(None, 36)
    advices = [
        font.render('Use arrows left and right to move', True, color_of_text),
        font.render('Use arrow up to jump', True, color_of_text),
        font.render('Use Z to use blaster', True, color_of_text),
        font.render('Use X to beat', True, color_of_text)
    ]
    pygame.mixer.music.stop()
    pygame.mixer.music.load('Sounds/training.ogg')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.2)
    skip_text = font.render('Press SPACE to skip', True, color_of_text)
    hint = 0

    while play:  # Обучение

        clock.tick(60)
        if gunattack:
            guncount += 1

        lastpause += 1

        if attack:
            attackcircle += 1
            if attackcircle > 12:
                attack = False
                attackcircle = 0

        if non_damage:
            non_damcircle += 1
            if non_damcircle > 45:
                non_damage = False
                non_damcircle = 0

        if gunattack:
            lastgunattack += 1
        if lastgunattack > 6:
            gunattack = False
            lastgunattack = 0

        k1 += 1

        xc = 0
        yc = 0
        pygame.time.delay(25)

        keys = pygame.key.get_pressed()

        if (joy.get_button(2) or keys[pygame.K_x]) and not (keys[pygame.K_LEFT]) and not (
                keys[pygame.K_RIGHT]) and not (jump) and not (hit):
            if hint == 3:
                hint = 0
            attack = True
            if lastMove == 'left':
                xa1 = x + 3
                xa2 = x + 40
            else:
                xa1 = x + 115
                xa2 = x + 88


        elif (joy.get_button(3) or keys[pygame.K_z]) and not (keys[pygame.K_LEFT]) and not (
                keys[pygame.K_RIGHT]) and not (jump) and not (hit):
            if hint == 2:
                hint = 3
            gunattack = True
            gunattack_s.play()
            if lastMove == 'right':
                side = 1
            else:
                side = -1
            if guncount > 5:
                bullets.append(Plasma(round(x + w // 2), round(y + h // 2), side))
                guncount = 0

        if (joy.get_hat(0) == (-1, 0) or keys[pygame.K_LEFT] or joy.get_axis(0) < -0.05) and not (attack) and not (
                gunattack):
            if hint == 0:
                hint = 1
            xc = -speed
            left = True
            right = False
            lastMove = 'left'

        elif (joy.get_hat(0) == (1, 0) or keys[pygame.K_RIGHT] or joy.get_axis(0) > 0.05) and not (attack) and not (
                gunattack):
            if hint == 0:
                hint = 1
            xc = speed
            left = False
            right = True
            lastMove = 'right'

        else:
            left = False
            right = False

        if (joy.get_button(0) or keys[pygame.K_UP]) and not (hit) and not (attack) and not (gunattack) and (
                        jumps == 0 or k >= 3 and jumps == 1):
            if hint == 1:
                hint = 2
            k = 0
            jumps += 1
            jump = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    play = False

        damm = True

        for bullet in bullets:
            if bullet.x < xw and bullet.x > 0:
                bullet.x += bullet.speed
            else:
                bullets.pop(bullets.index(bullet))

            for bul in rem_bul:
                bullets.pop(bullets.index(bul))
            rem_bul = []

        if jump:
            move = -jumpSpeed + g * k
            k += 1
            if move + y > yw - h - downLine + 2:
                move = yw - h - downLine + 2 - y
                k = 0
                jump = False
                jumps = 0
            yc = move
        x = x + xc
        y = y + yc

        if x < 0:
            x = 0

        if x > xw - w:
            x = xw - w

        if y == yw - h - downLine:
            lastx = x

        drawTrainingWindow()

    history(hist2)

    play = True

    start_time = time.clock()
    pause_time = 0
    x = 150
    lastx = x
    y = yw - h - downLine
    pygame.mixer.music.stop()
    pygame.mixer.music.load('Sounds/soundtrack.ogg')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.5)

    while play:  # Цикл предбоссового уровня

        clock.tick(60)

        if gunattack:
            guncount += 1

        lastpause += 1

        if circlekills == 10:  # Добавляет единицу hp за количество фрагов, кратное 10
            hill_s.play()
            if hero_health < max_hero_health:
                hero_health += 1
            circlekills = 0

        if attack:
            attackcircle += 1
            if attackcircle > 12:
                attack = False
                attackcircle = 0

        if kills >= kills_to_boss:
            pygame.mixer.music.stop()
            pygame.mixer.music.load('Sounds/final_boss.ogg')
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.2)
            boss = True
            break

        if hit:
            hitcircle += 1
            if hitcircle > 2:
                hit = False
                hitcircle = 0
                non_damage = True

        if non_damage:
            non_damcircle += 1
            if non_damcircle > 45:
                non_damage = False
                non_damcircle = 0

        if gunattack:
            lastgunattack += 1
        if lastgunattack > 6:
            gunattack = False
            lastgunattack = 0

        k1 += 1

        enemyAnimCount += 1

        if k1 % random.choice([60, 40, 180]) == 0 and (len(enemies) < max_count_enemy):
            enemies.append(Enemy(random.choice([-84, xw + 83]), yw - 91 - downLine, enemySpeed, max_enemy_health))

        xc = 0
        yc = 0
        pygame.time.delay(25)

        keys = pygame.key.get_pressed()

        if (joy.get_button(7) or keys[pygame.K_ESCAPE]) and lastpause > 5:
            st = time.clock()
            pause()
            pause_time += time.clock() - st
            lastpause = 0

        if (joy.get_button(2) or keys[pygame.K_x]) and not (keys[pygame.K_LEFT]) and not (
                keys[pygame.K_RIGHT]) and not (jump) and not (hit):
            attack = True
            if lastMove == 'left':
                xa1 = x + 3
                xa2 = x + 40
            else:
                xa1 = x + 115
                xa2 = x + 88

        if attack and attackcircle == 6:
            for en in enemies:
                if (xa1 > (en.x + 13)) and (xa1 < (en.x + 66)) or (xa2 > (en.x + 13)) and (xa2 < (en.x + 66)):
                    attack_s.play()
                    zombie_hit.play()
                    if en.health > damage_att:
                        en.health -= damage_att
                        en.hurt = True
                    else:
                        die_en.append(en)
                        kills += 1
                        circlekills += 1
                    if lastMove == 'left':
                        en.x -= fhatt
                    else:
                        en.x += fhatt
                    break


        elif (joy.get_button(3) or keys[pygame.K_z]) and not (keys[pygame.K_LEFT]) and not (
                keys[pygame.K_RIGHT]) and not (jump) and not (hit):
            gunattack = True
            gunattack_s.play()
            if lastMove == 'right':
                side = 1
            else:
                side = -1
            if guncount > 5:
                bullets.append(Plasma(round(x + w // 2), round(y + h // 2), side))
                guncount = 0

        if (joy.get_hat(0) == (-1, 0) or keys[pygame.K_LEFT] or joy.get_axis(0) < -0.05) and not (attack) and not (
                gunattack):
            xc = -speed
            left = True
            right = False
            lastMove = 'left'

        elif (joy.get_hat(0) == (1, 0) or keys[pygame.K_RIGHT] or joy.get_axis(0) > 0.05) and not (attack) and not (
                gunattack):
            xc = speed
            left = False
            right = True
            lastMove = 'right'

        else:
            left = False
            right = False

        if (joy.get_button(0) or keys[pygame.K_UP]) and not (hit) and not (attack) and not (gunattack) and (
                        jumps == 0 or k >= 3 and jumps == 1):
            k = 0
            jumps += 1
            jump = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        damm = True
        for en in enemies:
            if damm:
                en.last_attack += 1
                en.move(lastx)
                if en.hurt:
                    en.hurtcircle += 1
                if en.hurtcircle > 5:
                    en.hurt = False
                    en.hurtcircle = 0
                if not (en.hurt) and (en.last_attack > 5):
                    if ((en.x > x) and (en.x + 60 < x + w)) or ((en.x + 83 - 50 > x) and (en.x + 83 < x + w)):
                        if y > en.y - h:
                            en.attack = True
                            zombie_attack.play()
                if en.attack:
                    en.attackcircle += 1
                if en.attackcircle > 11:
                    en.attack = False
                    en.last_attack = 0
                    en.attackcircle = 0
                    if ((en.x > x) and (en.x + 60 < x + w)) or ((en.x + 83 - 50 > x) and (en.x + 83 < x + w)):
                        if y + 76 > en.y and not (non_damage):
                            damm = False
                            hero_health -= 1
                            if en.left:
                                x -= fenatt
                            else:
                                x += fenatt
                            if hero_health > 0:
                                hit = True
                                hit_s.play()
                                hitcircle = 0
                            else:
                                die()

        for bullet in bullets:
            if bullet.x < xw and bullet.x > 0:
                bullet.x += bullet.speed
            else:
                bullets.pop(bullets.index(bullet))

        for en in enemies:
            for bullet in bullets:
                if (bullet.x > (en.x + 15)) and (bullet.x < (en.x + 68)):
                    rem_bul.append(bullet)
                    zombie_hit.play()
                    if en.health > damage_bul:
                        en.health -= damage_bul
                        en.hurt = True
                    else:
                        die_en.append(en)
                        kills += 1
                        circlekills += 1

            for bul in rem_bul:
                bullets.pop(bullets.index(bul))
            rem_bul = []

        for en in die_en:
            if en in enemies:
                enemies.pop(enemies.index(en))
            en.diecircle += 1

        if jump:
            move = -jumpSpeed + g * k
            k += 1
            if move + y > yw - h - downLine:
                move = yw - h - downLine - y
                k = 0
                jump = False
                jumps = 0
            yc = move
        x = x + xc
        y = y + yc

        if x < 0:
            x = 0

        if x > xw - w:
            x = xw - w

        if y == yw - h - downLine:
            lastx = x

        drawWindow()

    history(hist3)

    fires = []
    k2 = 0
    boss_en = Boss(1183, yw - 128 - downLine, 12, 10)
    boss_en.bombs = []
    boss_en.bb = []
    for rock in rocks_t:
        rock.chance = (250, 275, 225, 150)
    while play:  # Битва с боссом
        clock.tick(60)

        if gunattack:
            guncount += 1

        lastpause += 1

        if k2 == 20:
            fires.append(Fire(0, 496, window))
            fires.append(Fire(1070, 496, window))
        if k2 == 40:
            fires.append(Fire(60, 496, window))
            fires.append(Fire(1010, 496, window))
        if k2 == 60:
            fires.append(Fire(120, 496, window))
            fires.append(Fire(950, 496, window))

        boss_en.move(x)

        if k2 % 15 == 0:
            for fire in fires:
                if ((x + 43 < fire.x and (x + 88) > fire.x) or (x + 43 < (fire.x + 60) and x + 43 > fire.x)) and (
                            y + 116) > 555:
                    if not (non_damage):
                        hero_health -= 1
                        if hero_health > 0:
                            hit = True
                            hit_s.play()
                            hitcircle = 0
                        else:
                            die()
                        break

        if circlekills == 10:  # Добавляет единицу hp за количество фрагов, кратное 10
            hill_s.play()
            if hero_health < max_hero_health:
                hero_health += 1
            circlekills = 0

        if attack:
            attackcircle += 1
            if attackcircle > 12:
                attack = False
                attackcircle = 0

        if hit:
            hitcircle += 1
            if hitcircle > 2:
                hit = False
                hitcircle = 0
                non_damage = True

        if non_damage:
            non_damcircle += 1
            if non_damcircle > 45:
                non_damage = False
                non_damcircle = 0

        if gunattack:
            lastgunattack += 1
        if lastgunattack > 6:
            gunattack = False
            lastgunattack = 0

        k1 += 1
        k2 += 1

        enemyAnimCount += 1

        xc = 0
        yc = 0
        pygame.time.delay(25)

        keys = pygame.key.get_pressed()

        if (joy.get_button(7) or keys[pygame.K_ESCAPE]) and lastpause > 5:
            st = time.clock()
            pause()
            pause_time += time.clock() - st
            pauseb = True
            lastpause = 0

        if (joy.get_button(2) or keys[pygame.K_x]) and not (keys[pygame.K_LEFT]) and not (
                keys[pygame.K_RIGHT]) and not (
                jump) and not (hit):
            attack = True
            if lastMove == 'left':
                xa1 = x + 3
                xa2 = x + 40
            else:
                xa1 = x + 115
                xa2 = x + 88

        if attack and attackcircle == 6:
            if (xa1 > (boss_en.x + 40)) and (xa1 < (boss_en.x + 88)) or (xa2 > (boss_en.x + 40)) and (
                        xa2 < (boss_en.x + 88)):
                attack_s.play()
                boss_en.hit()
                boss_en.health -= 2
            else:
                for en in enemies:
                    if (xa1 > (en.x + 13)) and (xa1 < (en.x + 66)) or (xa2 > (en.x + 13)) and (xa2 < (en.x + 66)):
                        attack_s.play()
                        zombie_hit.play()
                        if en.health > damage_att:
                            en.health -= damage_att
                            en.hurt = True
                        else:
                            die_en.append(en)
                            kills += 1
                            circlekills += 1
                        if lastMove == 'left':
                            en.x -= fhatt
                        else:
                            en.x += fhatt
                        break


        elif (joy.get_button(3) or keys[pygame.K_z]) and not (keys[pygame.K_LEFT]) and not (
                keys[pygame.K_RIGHT]) and not (
                jump) and not (hit):
            gunattack = True
            gunattack_s.play()
            if lastMove == 'right':
                side = 1
            else:
                side = -1
            if guncount > 5:
                bullets.append(Plasma(round(x + w // 2), round(y + h // 2), side))
                guncount = 0

        if (joy.get_hat(0) == (-1, 0) or keys[pygame.K_LEFT] or joy.get_axis(0) < -0.05 or (
                        x > 863 and k2 < 70)) and not (attack) and not (
                gunattack):
            xc = -speed
            left = True
            right = False
            lastMove = 'left'

        elif (joy.get_hat(0) == (1, 0) or keys[pygame.K_RIGHT] or joy.get_axis(0) > 0.05 or (
                        x < 140 and k2 < 70)) and not (attack) and not (
                gunattack):
            xc = speed
            left = False
            right = True
            lastMove = 'right'

        else:
            left = False
            right = False

        if (joy.get_button(0) or keys[pygame.K_UP]) and not (hit) and not (attack) and not (gunattack) and (
                        jumps == 0 or k >= 3 and jumps == 1):
            k = 0
            jumps += 1
            jump = True

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        damm = True
        for en in enemies:
            if damm:
                en.last_attack += 1
                en.move(lastx)
                if en.hurt:
                    en.hurtcircle += 1
                if en.hurtcircle > 5:
                    en.hurt = False
                    en.hurtcircle = 0
                if not (en.hurt) and (en.last_attack > 5):
                    if ((en.x > x) and (en.x + 60 < x + w)) or ((en.x + 83 - 50 > x) and (en.x + 83 < x + w)):
                        if y > en.y - h:
                            en.attack = True
                            zombie_attack.play()
                if en.attack:
                    en.attackcircle += 1
                if en.attackcircle > 11:
                    en.attack = False
                    en.last_attack = 0
                    en.attackcircle = 0
                    if ((en.x > x) and (en.x + 60 < x + w)) or ((en.x + 83 - 50 > x) and (en.x + 83 < x + w)):
                        if y + 76 > en.y and not (non_damage):
                            damm = False
                            hero_health -= 1
                            if en.left:
                                x -= fenatt
                            else:
                                x += fenatt
                            if hero_health > 0:
                                hit = True
                                hit_s.play()
                                hitcircle = 0
                            else:
                                die()
        if ((x + 35) <= (boss_en.x + 35) and (x + 93) >= (boss_en.x + 35)) or (
                        (x + 93) >= (boss_en.x + 93) and (x + 35) <= (boss_en.x + 93)):
            if y >= 400 and not (non_damage) and not (boss_en.crouch):
                hero_health -= 1
                if boss_en.pos == 'right':
                    x -= 50
                else:
                    x += 50
                if hero_health > 0:
                    hit = True
                    hit_s.play()
                    hitcircle = 0
                else:
                    die()

        if boss_en.attack_check() and not (non_damage):
            hero_health -= 1
            if hero_health > 0:
                hit = True
                hit_s.play()
                hitcircle = 0
            else:
                die()

        for bullet in bullets:
            if bullet.x < xw and bullet.x > 0:
                bullet.x += bullet.speed
            else:
                bullets.pop(bullets.index(bullet))

        for bullet in bullets:
            if (bullet.x > (boss_en.x + 40)) and (bullet.x < (boss_en.x + 88)):
                rem_bul.append(bullet)
                if boss_en.get_dam:
                    boss_en.health -= 1
                boss_en.get_dam = False
                boss_en.hit()
            else:
                for en in enemies:
                    if (bullet.x > (en.x + 15)) and (bullet.x < (en.x + 68)):
                        rem_bul.append(bullet)
                        zombie_hit.play()
                        if en.health > damage_bul:
                            en.health -= damage_bul
                            en.hurt = True
                        else:
                            die_en.append(en)
                            kills += 1
                            circlekills += 1
                        break

            for bul in rem_bul:
                bullets.pop(bullets.index(bul))
            rem_bul = []

        for en in die_en:
            if en in enemies:
                enemies.pop(enemies.index(en))
            en.diecircle += 1

        if jump:
            move = -jumpSpeed + g * k
            k += 1
            if move + y > yw - h - downLine:
                move = yw - h - downLine - y
                k = 0
                jump = False
                jumps = 0
            yc = move
        x = x + xc
        y = y + yc

        if x < 0:
            x = 0

        if x > xw - w:
            x = xw - w

        if y == yw - h - downLine:
            lastx = x

        drawWindow()
        if boss_en.end:
            result = round(time.clock() - start_time - pause_time)
            result = str(result // 60) + ' min ' + str(result % 60) + ' sec'
            pygame.mixer.music.stop()
            pygame.mixer.music.load('Sounds/music.ogg')
            pygame.mixer.music.play(-1)
            pygame.mixer.music.set_volume(0.4)
            end()
            leaderboard()
            break

pygame.quit()
