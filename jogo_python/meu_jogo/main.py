import pgzrun
import random
import math
from pygame import Rect, Color

WIDTH = 800
HEIGHT = 600
TITLE = "Python Adventure"
FPS = 60

ESTADO_MENU = 0
ESTADO_JOGANDO = 1
ESTADO_GAMEOVER = 2
ESTADO_VITORIA = 3
estado = ESTADO_MENU

COR_JOGADOR = (0, 255, 0)
COR_INIMIGO1 = (255, 0, 0)
COR_INIMIGO2 = (255, 165, 0)
COR_CHEFAO = (139, 0, 0)
COR_PLATAFORMA = (100, 70, 40)
COR_FUNDO = (30, 30, 50)
COR_MOEDA = (255, 215, 0)

fases_platforms = None
fases_enemies = None
fases_coins = None
fases_checkpoints = None
fases_finish = None


class SimpleActor:
    def __init__(self, x, y, width=40, height=60, color=COR_JOGADOR):
        self._rect = Rect(x, y, width, height)
        self.color = color
        self.facing_right = True
        self.velocity_y = 0
        self.jumping = False
        self.animation_frame = 0
        self.walk_frames = 4
        self.animation_speed = 0.2

    @property
    def rect(self):
        return self._rect

    @property
    def x(self):
        return self._rect.x

    @x.setter
    def x(self, value):
        self._rect.x = value

    @property
    def y(self):
        return self._rect.y

    @y.setter
    def y(self, value):
        self._rect.y = value

    @property
    def bottom(self):
        return self._rect.bottom

    @bottom.setter
    def bottom(self, value):
        self._rect.bottom = value

    @property
    def top(self):
        return self._rect.top

    @top.setter
    def top(self, value):
        self._rect.top = value

    @property
    def left(self):
        return self._rect.left

    @left.setter
    def left(self, value):
        self._rect.left = value

    @property
    def right(self):
        return self._rect.right

    @right.setter
    def right(self, value):
        self._rect.right = value

    @property
    def centerx(self):
        return self._rect.centerx

    @property
    def centery(self):
        return self._rect.centery

    @property
    def width(self):
        return self._rect.width

    @property
    def height(self):
        return self._rect.height

    def draw(self):
        if abs(self.velocity_y) < 1 and (keyboard.left or keyboard.right):
            self.animation_frame += self.animation_speed
            if self.animation_frame >= self.walk_frames:
                self.animation_frame = 0
            frame = int(self.animation_frame)
            current_height = self.height - (frame * 5 if frame < 2 else (4 - frame) * 5)
            self._rect.height = current_height
        else:
            self._rect.height = 60

        screen.draw.filled_rect(self._rect, self.color)
        eye_offset = 15 if self.facing_right else -15
        eye_y = self.centery - 15
        screen.draw.filled_circle((self.centerx + eye_offset, eye_y), 8, Color('white'))
        screen.draw.filled_circle((self.centerx + eye_offset, eye_y), 4, Color('black'))
        hat_width = self.width + 10
        screen.draw.filled_rect(Rect(self.left - 5, self.top - 10, hat_width, 10), Color('red'))

    def colliderect(self, other):
        if isinstance(other, SimpleActor):
            return self._rect.colliderect(other._rect)
        return self._rect.colliderect(other)


class Chefao:
    def __init__(self, x, y):
        self._rect = Rect(x, y, 120, 120)
        self.color = COR_CHEFAO
        self.speed = 2
        self.direction = 1
        self.angle = 0
        self.radius = 200
        self.center_x = x
        self.center_y = y
        self.spawn_timer = 0
        self.spawn_interval = 180
        self.health = 3
        self.invincible = 0
        self.hit_timer = 0
        self.target_x = x
        self.target_y = y
        self.pursuit_speed = 1.5

    @property
    def rect(self):
        return self._rect

    def update(self):
        self.spawn_timer += 1

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            return True

        dx = self.target_x - self._rect.x
        dy = self.target_y - self._rect.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist > 0:
            self._rect.x += dx / dist * self.pursuit_speed
            self._rect.y += dy / dist * self.pursuit_speed

        if self.invincible > 0:
            self.invincible -= 1
            self.hit_timer += 1
            if self.hit_timer > 10:
                self.color = COR_CHEFAO
                self.hit_timer = 0
            else:
                self.color = Color('white')

    def set_target(self, x, y):
        self.target_x = x
        self.target_y = y

    def draw(self):
        screen.draw.filled_rect(self._rect, self.color)
        screen.draw.filled_circle((self._rect.centerx - 20, self._rect.centery - 20), 15, Color('white'))
        screen.draw.filled_circle((self._rect.centerx + 20, self._rect.centery - 20), 15, Color('white'))
        screen.draw.filled_circle((self._rect.centerx - 20, self._rect.centery - 20), 7, Color('black'))
        screen.draw.filled_circle((self._rect.centerx + 20, self._rect.centery - 20), 7, Color('black'))
        screen.draw.filled_rect(Rect(self._rect.left + 20, self._rect.top - 10, 40, 10), Color('darkred'))
        screen.draw.filled_rect(Rect(self._rect.right - 60, self._rect.top - 10, 40, 10), Color('darkred'))

    def take_hit(self):
        if self.invincible == 0:
            self.health -= 1
            self.invincible = 30
            self.color = Color('white')
            return True
        return False


player = SimpleActor(100, 400)
player.double_jump = False
player.combo = 0
player.health = 5
player.max_health = 5
player.invincible = 0
player.checkpoint = (100, 400)
player.coins = 0

enemies = []
platforms = []
coins = []
particles = []
fase = 1
MAX_FASES = 3
score = 0
finish_flag = None
checkpoint_flag = None
chefao = None
chefao_active = False
victory_effect = 0


def setup_fases():
    global fases_platforms, fases_enemies, fases_coins, fases_checkpoints, fases_finish

    level_width = 5000

    fases_platforms = {
        1: [
            Rect(0, 550, 300, 50),
            Rect(350, 450, 100, 20), Rect(350, 550, 100, 50),
            Rect(550, 550, 200, 50),
            Rect(800, 400, 100, 20), Rect(800, 550, 100, 50),
            Rect(1000, 550, 200, 50),
            Rect(1250, 350, 100, 20), Rect(1250, 550, 100, 50),
            Rect(1450, 550, 200, 50),
            Rect(1700, 300, 100, 20), Rect(1700, 550, 100, 50),
            Rect(1900, 550, 300, 50),
            Rect(2250, 450, 100, 20), Rect(2250, 550, 100, 50),
            Rect(2450, 550, 300, 50),
            Rect(2800, 400, 100, 20), Rect(2800, 550, 100, 50),
            Rect(3000, 550, 300, 50),
            Rect(3350, 350, 100, 20), Rect(3350, 550, 100, 50),
            Rect(3550, 550, 300, 50),
            Rect(3900, 450, 100, 20), Rect(3900, 550, 100, 50),
            Rect(4100, 550, 300, 50),
            Rect(4500, 550, 500, 50)
        ],
        2: [
            Rect(0, 550, 250, 50),
            Rect(300, 450, 80, 20), Rect(300, 550, 80, 50),
            Rect(480, 550, 170, 50),
            Rect(700, 350, 80, 20), Rect(700, 550, 80, 50),
            Rect(880, 550, 170, 50),
            Rect(1100, 450, 80, 20), Rect(1100, 550, 80, 50),
            Rect(1280, 550, 170, 50),
            Rect(1500, 300, 300, 20), Rect(1500, 550, 300, 50),
            Rect(1900, 400, 100, 20), Rect(1900, 550, 100, 50),
            Rect(2100, 550, 300, 50),
            Rect(2450, 500, 100, 20), Rect(2450, 550, 100, 50),
            Rect(2650, 550, 300, 50),
            Rect(3000, 400, 100, 20), Rect(3000, 550, 100, 50),
            Rect(3200, 550, 300, 50),
            Rect(3550, 300, 200, 20), Rect(3550, 550, 200, 50),
            Rect(3850, 550, 300, 50),
            Rect(4200, 500, 100, 20), Rect(4200, 550, 100, 50),
            Rect(4400, 550, 600, 50)
        ],
        3: [
            Rect(0, 550, 200, 50),
            Rect(250, 450, 50, 20), Rect(250, 550, 50, 50),
            Rect(400, 550, 200, 50),
            Rect(650, 350, 50, 20), Rect(650, 550, 50, 50),
            Rect(800, 550, 200, 50),
            Rect(1050, 250, 50, 20), Rect(1050, 550, 50, 50),
            Rect(1200, 550, 200, 50),
            Rect(1450, 450, 50, 20), Rect(1450, 550, 50, 50),
            Rect(1600, 550, 200, 50),
            Rect(1850, 80, 700, 20), Rect(1850, 550, 700, 50),
            Rect(2650, 550, 200, 50),
            Rect(2900, 350, 50, 20), Rect(2900, 550, 50, 50),
            Rect(3050, 550, 200, 50),
            Rect(3300, 300, 200, 20), Rect(3300, 550, 200, 50),
            Rect(3600, 550, 200, 50),
            Rect(3850, 400, 100, 20), Rect(3850, 550, 100, 50),
            Rect(4050, 550, 200, 50),
            Rect(4300, 500, 100, 20), Rect(4300, 550, 100, 50),
            Rect(4500, 550, 500, 50)
        ]
    }

    fases_enemies = {
        1: [
            (800, 400, 1.5, COR_INIMIGO1, False),
            (1250, 350, 1.7, COR_INIMIGO2, False),
            (1950, 300, 1.8, COR_INIMIGO1, False),
            (2650, 250, 2.0, COR_INIMIGO2, False),
            (4350, 350, 1.7, COR_INIMIGO2, False)
        ],
        2: [
            (480, 400, 1.7, COR_INIMIGO1, False),
            (780, 300, 2.0, COR_INIMIGO2, True),
            (1080, 400, 1.7, COR_INIMIGO1, False),
            (1680, 400, 1.8, COR_INIMIGO1, False),
            (2280, 250, 2.2, COR_INIMIGO2, True),
            (2980, 350, 2.1, COR_INIMIGO2, False),
            (4250, 350, 1.7, COR_INIMIGO1, False)
        ],
        3: [
            (300, 400, 2.5, COR_INIMIGO1, False),
            (700, 300, 3.0, COR_INIMIGO2, False),
            (1100, 200, 2.7, COR_INIMIGO1, False),
            (1500, 400, 2.8, COR_INIMIGO1, False),
            (1900, 80, 2.5, COR_INIMIGO2, False),
            (2700, 350, 3.2, COR_INIMIGO2, False),
            (3500, 400, 3.0, COR_INIMIGO1, False),
            (4300, 350, 2.8, COR_INIMIGO2, False)
        ]
    }

    fases_coins = {
        1: [(x, 300) for x in range(200, 4800, 150)] +
           [(x, 250) for x in range(400, 4700, 300)],
        2: [(x, 300) for x in range(200, 4800, 120)] +
           [(x, 250) for x in range(350, 4700, 200)] +
           [(x, 200) for x in range(500, 4600, 350)],
        3: [(x, 300) for x in range(200, 4800, 80)] +
           [(x, 100) for x in range(400, 4700, 120)] +
           [(x, 70) for x in range(600, 4600, 180)]
    }

    fases_checkpoints = {
        1: (1200, 500),
        2: (1800, 500),
        3: (3800, 500)
    }

    fases_finish = {
        1: (4600, 500),
        2: (4600, 500),
        3: (4800, 500)
    }


def init_level():
    global enemies, platforms, coins, finish_flag, checkpoint_flag, chefao, chefao_active

    if fases_finish is None:
        setup_fases()

    platforms = fases_platforms.get(fase, []).copy()

    enemies = []
    for enemy_data in fases_enemies.get(fase, []):
        x, y, speed, color, flying = enemy_data
        enemy = SimpleActor(x, y, color=color)
        enemy.speed = speed
        enemy.flying = flying
        if flying:
            enemy.original_y = y
            enemy.float_offset = 0
            enemy.float_speed = random.uniform(0.05, 0.1)
        enemies.append(enemy)

    coins = [Rect(x, y, 20, 20) for x, y in fases_coins.get(fase, [])]

    checkpoint_x, checkpoint_y = fases_checkpoints.get(fase, (400, 500))
    checkpoint_flag = Rect(checkpoint_x, checkpoint_y, 40, 50)

    finish_x, finish_y = fases_finish.get(fase, (4500, 500))
    finish_flag = Rect(finish_x, finish_y, 40, 50)

    if fase == MAX_FASES:
        chefao = Chefao(2000, 200)
        chefao_active = True
    else:
        chefao = None
        chefao_active = False

    player.x = 100
    player.y = 400
    player.checkpoint = (100, 400)
    player.velocity_y = 0
    player.double_jump = False


def draw_ui():
    for i in range(player.max_health):
        color = 'red' if i < player.health else 'darkred'
        screen.draw.filled_rect(Rect(20 + i * 40, 20, 30, 30), Color(color))

    screen.draw.text(f"Score: {score}", (WIDTH - 200, 20), fontsize=30, color='white')
    screen.draw.text(f"Fase: {fase}/{MAX_FASES}", (WIDTH - 200, 60), fontsize=30, color='white')
    screen.draw.text(f"Moedas: {player.coins}", (WIDTH - 200, 100), fontsize=30, color='yellow')

    if player.combo > 1:
        screen.draw.text(f"COMBO x{player.combo}!", (WIDTH // 2 - 50, 50), fontsize=25, color='yellow')

    if player.double_jump:
        screen.draw.text("DJ READY!", (WIDTH // 2 - 30, 20), fontsize=20, color='cyan')

    if chefao_active and chefao:
        screen.draw.text("CHEFÃO:", (WIDTH // 2 - 100, HEIGHT - 40), fontsize=25, color='red')
        for i in range(chefao.health):
            screen.draw.filled_rect(Rect(WIDTH // 2 + i * 40, HEIGHT - 40, 30, 30), Color('red'))


def draw():
    screen.fill(COR_FUNDO)
    camera_x = player.x - WIDTH // 2
    camera_x = max(0, min(camera_x, 5000 - WIDTH))

    for plat in platforms:
        screen.draw.filled_rect(Rect(plat.x - camera_x, plat.y, plat.width, plat.height), COR_PLATAFORMA)

    for coin in coins:
        screen.draw.filled_circle((coin.x - camera_x + 10, coin.y + 10), 10, COR_MOEDA)

    for enemy in enemies:
        screen.draw.filled_rect(Rect(enemy.x - camera_x, enemy.y, enemy.width, enemy.height), enemy.color)
        eye_offset = 10 if enemy.speed > 0 else -10
        screen.draw.filled_circle((enemy.x - camera_x + enemy.width // 2 + eye_offset, enemy.y + 15), 5, Color('white'))

    if checkpoint_flag:
        screen.draw.filled_rect(
            Rect(checkpoint_flag.x - camera_x, checkpoint_flag.y, checkpoint_flag.width, checkpoint_flag.height),
            Color('blue'))
        screen.draw.filled_rect(Rect(checkpoint_flag.x - camera_x + 15, checkpoint_flag.y - 30, 10, 30), Color('white'))
        screen.draw.filled_rect(Rect(checkpoint_flag.x - camera_x + 25, checkpoint_flag.y - 30, 15, 20), Color('blue'))

    if finish_flag:
        screen.draw.filled_rect(Rect(finish_flag.x - camera_x, finish_flag.y, finish_flag.width, finish_flag.height),
                                Color('white'))
        screen.draw.filled_rect(Rect(finish_flag.x - camera_x + 15, finish_flag.y - 40, 10, 40), Color('white'))
        screen.draw.filled_rect(Rect(finish_flag.x - camera_x + 25, finish_flag.y - 40, 20, 20), Color('gold'))

    if chefao_active and chefao:
        chefao.draw()

    player.x = WIDTH // 2
    if player.invincible % 10 < 5 or estado != ESTADO_JOGANDO:
        player.draw()

    for p in particles:
        screen.draw.filled_circle((p[0] - camera_x, p[1]), p[2], p[3])

    if victory_effect > 0:
        for _ in range(10):
            x = random.randint(0, WIDTH)
            y = random.randint(0, HEIGHT)
            size = random.randint(5, 15)
            screen.draw.filled_circle((x, y), size, Color('gold'))

    draw_ui()

    if estado == ESTADO_MENU:
        screen.draw.text("PYTHON ADVENTURE", center=(WIDTH / 2, HEIGHT / 2 - 50), fontsize=60, color='white')
        screen.draw.text("Pressione ENTER para jogar", center=(WIDTH / 2, HEIGHT / 2 + 50), fontsize=30,
                         color='lightblue')
        screen.draw.text("Controles: SETAS mover, ESPAÇO pular, CIMA double jump", center=(WIDTH / 2, HEIGHT / 2 + 100),
                         fontsize=20, color='yellow')

    elif estado == ESTADO_GAMEOVER:
        screen.draw.text("GAME OVER", center=(WIDTH / 2, HEIGHT / 2 - 50), fontsize=72, color='red')
        screen.draw.text(f"Score: {score}", center=(WIDTH / 2, HEIGHT / 2 + 30), fontsize=40, color='white')
        screen.draw.text("Pressione R para reiniciar", center=(WIDTH / 2, HEIGHT / 2 + 100), fontsize=30,
                         color='lightgray')

    elif estado == ESTADO_VITORIA:
        screen.draw.text("PARABÉNS!", center=(WIDTH / 2, HEIGHT / 2 - 50), fontsize=72, color='gold')
        screen.draw.text(f"Score Final: {score}", center=(WIDTH / 2, HEIGHT / 2 + 30), fontsize=40, color='white')
        screen.draw.text(f"Moedas: {player.coins}", center=(WIDTH / 2, HEIGHT / 2 + 80), fontsize=30, color='yellow')
        screen.draw.text("Pressione R para jogar novamente", center=(WIDTH / 2, HEIGHT / 2 + 130), fontsize=30,
                         color='lightgray')


def update():
    global estado, fase, score, chefao_active, victory_effect

    if estado == ESTADO_JOGANDO:
        handle_movement()
        player.velocity_y += 0.5
        player.y += player.velocity_y

        handle_collisions()
        handle_coin_collision()
        update_enemies()
        update_particles()

        if chefao_active and chefao:
            chefao.set_target(player.x + (player.x - WIDTH // 2), player.y)
            if chefao.update():
                spawn_minion(chefao.rect.x, chefao.rect.y, COR_INIMIGO1)
                spawn_minion(chefao.rect.x, chefao.rect.y, COR_INIMIGO2)

            handle_chefao_collision()
            if chefao.health <= 0:
                victory_effect = 60
                estado = ESTADO_VITORIA

        if victory_effect > 0:
            victory_effect -= 1

        camera_x = player.x - WIDTH // 2
        camera_x = max(0, min(camera_x, 5000 - WIDTH))

        if checkpoint_flag and player.colliderect(
                Rect(checkpoint_flag.x - camera_x + WIDTH // 2, checkpoint_flag.y, checkpoint_flag.width,
                     checkpoint_flag.height)):
            player.checkpoint = (checkpoint_flag.x, checkpoint_flag.y - 50)
            create_particles(checkpoint_flag.x + 20, checkpoint_flag.y, 20, Color('blue'))

        if finish_flag and player.colliderect(
                Rect(finish_flag.x - camera_x + WIDTH // 2, finish_flag.y, finish_flag.width, finish_flag.height)):
            next_level()

        if player.invincible > 0:
            player.invincible -= 1


def spawn_minion(x, y, color):
    enemy = SimpleActor(x, y, color=color)
    enemy.speed = random.uniform(2.0, 3.0)
    enemy.flying = True
    enemy.original_y = y
    enemy.float_offset = 0
    enemy.float_speed = random.uniform(0.05, 0.1)
    enemies.append(enemy)


def handle_movement():
    world_speed = 0
    if keyboard.left:
        world_speed = -5
        player.facing_right = False
    if keyboard.right:
        world_speed = 5
        player.facing_right = True

    if world_speed != 0:
        for plat in platforms:
            plat.x -= world_speed
        for coin in coins:
            coin.x -= world_speed
        for enemy in enemies:
            enemy.x -= world_speed
        if checkpoint_flag:
            checkpoint_flag.x -= world_speed
        if finish_flag:
            finish_flag.x -= world_speed
        for p in particles:
            p[0] -= world_speed

    player.x = WIDTH // 2


def handle_collisions():
    player.jumping = True
    camera_x = player.x - WIDTH // 2
    camera_x = max(0, min(camera_x, 5000 - WIDTH))

    for plat in platforms:
        plat_rect = Rect(plat.x - camera_x, plat.y, plat.width, plat.height)
        if (
                player.velocity_y > 0 and player.bottom < plat_rect.top + 20 and player.right > plat_rect.left + 10 and player.left < plat_rect.right - 10):
            if player.bottom > plat_rect.top:
                player.bottom = plat_rect.top
                player.velocity_y = 0
                player.jumping = False
                break

    if player.top > HEIGHT + 50:
        player_damage(1)
        player.x, player.y = player.checkpoint
        player.velocity_y = 0


def handle_chefao_collision():
    global score

    camera_x = player.x - WIDTH // 2
    camera_x = max(0, min(camera_x, 5000 - WIDTH))

    if chefao and chefao_active:
        chefao_rect = Rect(chefao.rect.x - camera_x, chefao.rect.y, chefao.rect.width, chefao.rect.height)

        if player.colliderect(chefao_rect):
            if player.velocity_y > 0 and player.bottom < chefao_rect.top + 15 and player.bottom > chefao_rect.top - 5:
                if chefao.take_hit():
                    player.velocity_y = -15
                    score += 100
                    create_particles(chefao.rect.centerx, chefao.rect.top, 20, Color('gold'))
            else:
                player_damage(1)


def handle_coin_collision():
    global score, coins

    camera_x = player.x - WIDTH // 2
    camera_x = max(0, min(camera_x, 5000 - WIDTH))

    for coin in coins[:]:
        coin_rect = Rect(coin.x - camera_x, coin.y, coin.width, coin.height)
        if player.colliderect(coin_rect):
            coins.remove(coin)
            player.coins += 1
            score += 10
            create_particles(coin.x + 10, coin.y + 10, 8, COR_MOEDA)


def update_enemies():
    global score

    camera_x = player.x - WIDTH // 2
    camera_x = max(0, min(camera_x, 5000 - WIDTH))

    for enemy in enemies[:]:
        if getattr(enemy, 'flying', False):
            enemy.float_offset += enemy.float_speed
            enemy.y = enemy.original_y + math.sin(enemy.float_offset) * 50
            enemy.x += enemy.speed * 0.5
        else:
            enemy.x += enemy.speed

        if enemy.left < 20 or enemy.right > 5000 - 20:
            enemy.speed *= -1

        enemy_rect = Rect(enemy.x - camera_x, enemy.y, enemy.width, enemy.height)
        if player.colliderect(enemy_rect) and player.invincible == 0:
            if (player.velocity_y > 0 and player.bottom < enemy_rect.top + 15 and player.bottom > enemy_rect.top - 5):
                player.velocity_y = -12
                player.combo += 1
                score += 20 * player.combo
                create_particles(enemy.x, enemy.y, 15, Color('yellow'))
                if player.combo >= 2 and not player.double_jump:
                    player.double_jump = True
                    create_particles(player.x, player.y, 20, Color('cyan'))
                enemies.remove(enemy)
            else:
                player_damage(1)


def update_particles():
    for p in particles[:]:
        p[0] += p[4]
        p[1] += p[5]
        p[2] = max(0, p[2] - 0.1)
        if p[2] <= 0:
            particles.remove(p)


def create_particles(x, y, count, color):
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(1, 3)
        particles.append([
            x, y,
            random.randint(3, 6),
            color,
            math.cos(angle) * speed,
            math.sin(angle) * speed
        ])


def player_damage(amount):
    global estado, fase

    player.health -= amount
    player.invincible = 60
    player.combo = 0
    create_particles(player.x, player.y, 15, Color('red'))

    if player.health <= 0:
        estado = ESTADO_GAMEOVER
        fase = 1
        player.health = player.max_health
        player.coins = 0
        score = 0


def next_level():
    global estado, fase, chefao_active

    if fase < MAX_FASES:
        fase += 1
        init_level()
        player.health = player.max_health
    else:
        estado = ESTADO_VITORIA
        chefao_active = False


def on_key_down(key):
    global estado, fase, score, player

    if estado == ESTADO_MENU and key == keys.RETURN:
        setup_fases()
        estado = ESTADO_JOGANDO
        fase = 1
        score = 0
        player.coins = 0
        player.health = player.max_health
        init_level()

    elif (estado == ESTADO_GAMEOVER or estado == ESTADO_VITORIA) and key == keys.R:
        estado = ESTADO_MENU

    elif estado == ESTADO_JOGANDO:
        if key == keys.SPACE and not player.jumping:
            player.velocity_y = -15
            player.jumping = True
        elif key == keys.UP and player.double_jump and player.jumping:
            player.velocity_y = -18
            player.double_jump = False
            create_particles(player.x, player.y, 20, Color('cyan'))


setup_fases()
pgzrun.go()