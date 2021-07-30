import pygame
import random
import time
import os
from pygame import mixer

pygame.init()
pygame.font.init()
width, height = 1500, 750
tank_width, tank_height = 510, 244
missile_width, missile_height = 200, 100
WIN = pygame.display.set_mode((width, height))
pygame.display.set_caption("Tank War")

# main_tank
main_tank = pygame.transform.scale(pygame.image.load(os.path.join("assets", "tank1.png")), (tank_width, tank_height))

# enemy_tank
enemy_tank_1 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "tank2.png")), (tank_width, tank_height))
enemy_tank_2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "tank3.png")), (tank_width, tank_height))
enemy_tank_3 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "tank4.png")), (tank_width, tank_height))
enemy_tank_4 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "tank5.png")), (tank_width, tank_height))

# tank_missile
main_missile = pygame.transform.scale(pygame.image.load(os.path.join("assets", "missile.png")),
                                      (missile_width, missile_height))
enemy_missile_1 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "missile2.png")),
                                         (missile_width, missile_height))
enemy_missile_2 = pygame.transform.scale(pygame.image.load(os.path.join("assets", "missile3.png")),
                                         (missile_width, missile_height))

# background_image
bg = pygame.transform.scale(pygame.image.load(os.path.join("assets", "background.jpg")), (width, height))

# missile_sound
missile_sound = pygame.mixer.Sound("sound\missile.wav")

# tank moving sound
tank_moving_sound = pygame.mixer.Sound("sound\Tank.wav")

# explosion sound
explosion_sound = pygame.mixer.Sound("sound\explosion.wav")


# missile
class Missile:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.x += vel

    def off_screen(self, breadth):
        return not (breadth >= self.x >= 0)

    def collision(self, obj):
        return collide(self, obj)


# abstract class
class Tank:
    COOLDOWN = 100

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.tank_img = None
        self.missile_img = None
        self.missiles = []
        self.cool_down_counter = 0

    def draw(self, window):
        # pygame.draw.rect(window, (255, 0, 0), (self.x, self.y, 50, 50) )
        window.blit(self.tank_img, (self.x, self.y))
        for missile in self.missiles:
            missile.draw(window)

    def move_missile(self, vel, obj):
        self.cooldown()
        for missile in self.missiles:

            missile.move(vel)
            if missile.off_screen(width):
                self.missiles.remove(missile)
            elif missile.collision(obj):
                obj.health -= 10
                explosion_sound.play()
                self.missiles.remove(missile)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            missile = Missile(self.x + self.get_width(), self.y + 50, self.missile_img)
            self.missiles.append(missile)
            self.cool_down_counter = 1

    def get_width(self):
        return self.tank_img.get_width()

    def get_height(self):
        return self.tank_img.get_height()


class Player(Tank):
    score = 0

    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.tank_img = main_tank
        self.missile_img = main_missile
        self.mask = pygame.mask.from_surface(self.tank_img)
        self.max_health = health

    def draw(self, window):
        super().draw(window)

    def move_missile(self, vel, objs):
        self.cooldown()
        for missile in self.missiles:
            missile.move(vel)
            if missile.off_screen(width):
                self.missiles.remove(missile)
            else:
                for obj in objs:
                    if missile.collision(obj):
                        self.score += 1
                        explosion_sound.play()
                        objs.remove(obj)
                        if missile in self.missiles:
                            self.missiles.remove(missile)

    def missile_collision(self, mobjs):
        for missile in self.missiles:
            for obj in mobjs:
                if missile.collision(obj):
                    explosion_sound.play()
                    mobjs.remove(obj)
                    if missile in self.missiles:
                        self.missiles.remove(missile)

    def draw(self, window):
        super().draw(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.tank_img.get_height() + 10, self.tank_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.tank_img.get_height() + 10,
            self.tank_img.get_width() * (self.health / self.max_health),
            10))


class Enemy(Tank):
    COLOR_MAP = {
        "grey": (enemy_tank_1, enemy_missile_1),
        "camo": (enemy_tank_2, enemy_missile_2),
        "yellow": (enemy_tank_3, enemy_missile_1),
        "dark": (enemy_tank_4, enemy_missile_2)
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.tank_img, self.missile_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.tank_img)

    def move(self, vel):
        self.x -= vel

    def shoot(self):
        if self.cool_down_counter == 0:
            missile = Missile(self.x, self.y + 35, self.missile_img)
            self.missiles.append(missile)
            self.cool_down_counter = 1


def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None


def main():
    run = True
    FPS = 60
    clock = pygame.time.Clock()
    level = 0
    lives = 5
    player_vel = 2
    enemy_vel = 1
    missile_vel = 2
    enemies = []
    wave_length = 0
    main_font = pygame.font.SysFont("comicsans", 50)
    lost_font = pygame.font.SysFont("comicsans", 70)
    score_font = pygame.font.SysFont("comicsans", 50)
    win_font = pygame.font.SysFont("comicsans", 70)
    player_tank = Player(0, 370)
    lost = False
    win = False
    lost_count = 0
    win_count = 0

    def redraw_window():
        WIN.blit(bg, (0, 0))
        level_label = main_font.render(f"Level: {level}", 1, (255, 0, 0))
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 0, 0))
        score_label = score_font.render(f"Score: {player_tank.score}", 1, (255, 0, 0))
        WIN.blit(level_label, (10, 10))
        WIN.blit(lives_label, (width - level_label.get_width() - 10, 10))
        WIN.blit(score_label, (width / 2 - score_label.get_width() / 2, 10))
        player_tank.draw(WIN)
        for enemy in enemies:
            enemy.draw(WIN)  # using draw method in tank class

        if win:
            win_label = win_font.render(f"You Win!!!", 1, (255, 0, 0))
            WIN.blit(win_label, (width / 2 - win_label.get_width() / 2, height / 2))

        if lost:
            lost_label = lost_font.render(f"You Lost!!!", 1, (255, 0, 0))
            WIN.blit(lost_label, (width / 2 - lost_label.get_width() / 2, height / 2))

        pygame.display.update()

    while run:
        clock.tick(FPS)
        redraw_window()

        if level == 5:
            win = True
            win_count += 1

        if win:
            if win_count > FPS * 3:
                run = False
            else:
                continue

        if lives <= 0 or player_tank.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else:
                continue

        if len(enemies) == 0:
            level += 1
            wave_length += 2
            for i in range(wave_length):
                enemy = Enemy(random.randrange(1500, 3000), 370, random.choice(["grey", "camo", "yellow", "dark"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a] and player_tank.x + player_vel > 0:  # left
            # tank_moving_sound.play()
            player_tank.x -= player_vel

        if keys[pygame.K_d] and player_tank.x + player_vel < width / 2 - player_tank.get_width():  # right
            # tank_moving_sound.play()
            player_tank.x += player_vel

        if keys[pygame.K_SPACE]:
            player_tank.shoot()
            missile_sound.play()

        for enemy in enemies[:]:
            enemy.move(enemy_vel)
            enemy.move_missile(-missile_vel, player_tank)
            if random.randrange(0, 4 * FPS) == 1:
                enemy.shoot()

            if collide(enemy, player_tank):
                explosion_sound.play()
                player_tank.health -= 10
                enemies.remove(enemy)

            elif enemy.x + enemy.get_width() < 0:
                lives -= 1
                enemies.remove(enemy)

        player_tank.move_missile(missile_vel, enemies)
        player_tank.missile_collision(enemy.missiles)


def main_menu():
    title_font = pygame.font.SysFont("comicsans", 70)
    run = True
    while run:
        WIN.blit(bg, (0, 0))
        title_label = title_font.render("Press the mouse to begin....", 1, (255, 0, 0))
        WIN.blit(title_label, (width / 2 - title_label.get_width() / 2, height / 2))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()
    pygame.quit()


main_menu()
