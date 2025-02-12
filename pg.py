import pygame, sys, os, random, time, pickle, math, pdb
from level1 import LEVEL1_LAYOUT, TILE_SIZE, load_tile_images, LEVEL1_TITLE, LEVEL1_BACKGROUND

def load_frames(folder, scale_factor=1.5):
    frames = []
    for filename in sorted(os.listdir(folder)):
        if filename.endswith('.png'):
            frame = pygame.image.load(os.path.join(folder, filename))
            frame = pygame.transform.scale(frame, (int(frame.get_width() * scale_factor),
                                                     int(frame.get_height() * scale_factor)))
            frames.append(frame)
    return frames

def find_grass_tiles(level_layout, tile_size, screen_height):
    grass_tiles = []
    for y in range(len(level_layout)):
        for x in range(len(level_layout[y])):
            if level_layout[y][x] == ".":
                y_pos = screen_height - (len(level_layout) - y) * tile_size
                grass_tiles.append((x * tile_size, y_pos))
    return grass_tiles

def draw_fixed_background(background):
    scaled = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(scaled, (0, 0))

def draw_level(level_layout, tile_images, offset_x):
    for y, row in enumerate(level_layout):
        for x, tile in enumerate(row):
            if tile in tile_images:
                screen.blit(tile_images[tile],
                            (x * TILE_SIZE - offset_x,
                             SCREEN_HEIGHT - (len(level_layout) - y) * TILE_SIZE))

def check_collision(rect, level_layout, tile_size):
    for y, row in enumerate(level_layout):
        for x in range(len(row)):
            if row[x] == "#":
                tile_rect = pygame.Rect(x * tile_size,
                                        SCREEN_HEIGHT - (y + 1) * tile_size,
                                        tile_size, tile_size)
                if rect.colliderect(tile_rect):
                    return True
    return False

def handle_vertical_collision(rect, level_layout, tile_size, dy):
    rect.y += dy
    for y, row in enumerate(level_layout):
        for x in range(len(row)):
            if row[x] == "#":
                tile_rect = pygame.Rect(x * tile_size,
                                        SCREEN_HEIGHT - (y + 1) * tile_size,
                                        tile_size, tile_size)
                if rect.colliderect(tile_rect):
                    if dy > 0:
                        rect.bottom = tile_rect.top
                    elif dy < 0:
                        rect.top = tile_rect.bottom
                    return True
    return False

def apply_health_tint(frame, health_percent):
    tinted = frame.copy()
    if health_percent >= 75:
        return tinted
    elif health_percent >= 50:
        tint = (50, 50, 0, 0)
    elif health_percent >= 25:
        tint = (100, 50, 0, 0)
    else:
        tint = (150, 0, 0, 0)
    tinted.fill(tint, special_flags=pygame.BLEND_RGBA_ADD)
    return tinted

def draw_health_bar(health, max_health, x, y):
    index = max(0, (int(health) // 10) * 10)
    screen.blit(health_bar_frames[index], (x, y))

def draw_mana_bar(mana, max_mana):
    index = (int(mana) // 10) * 10
    screen.blit(mana_bar_frames[index], (10, 40))

def set_state(new_state, frames, delay):
    global player_state, current_frames, frame_index, frame_delay
    if player_state != new_state:
        player_state = new_state
        current_frames = frames
        frame_index = 0
        frame_delay = delay

pygame.init()
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Sacred")
DEBUG = True

medieval_font_path = os.path.join('fonts', 'upheavtt.ttf')
medieval_font = pygame.font.Font(medieval_font_path, 74)
small_medieval_font = pygame.font.Font(medieval_font_path, 36)
level_background = pygame.image.load(LEVEL1_BACKGROUND)

health_bar_frames = {
    100: pygame.image.load(os.path.join('UI','HealthFull.png')).convert_alpha(),
    90: pygame.image.load(os.path.join('UI','Health90%.png')).convert_alpha(),
    80: pygame.image.load(os.path.join('UI','Health80%.png')).convert_alpha(),
    70: pygame.image.load(os.path.join('UI','Health70%.png')).convert_alpha(),
    60: pygame.image.load(os.path.join('UI','Health60%.png')).convert_alpha(),
    50: pygame.image.load(os.path.join('UI','Health50%.png')).convert_alpha(),
    40: pygame.image.load(os.path.join('UI','Health40%.png')).convert_alpha(),
    30: pygame.image.load(os.path.join('UI','Health30%.png')).convert_alpha(),
    20: pygame.image.load(os.path.join('UI','Health20%.png')).convert_alpha(),
    10: pygame.image.load(os.path.join('UI','Health10%.png')).convert_alpha(),
    0: pygame.image.load(os.path.join('UI','Health0%.png')).convert_alpha()
}
mana_bar_frames = {
    100: pygame.image.load(os.path.join('UI','ManaFull.png')).convert_alpha(),
    90: pygame.image.load(os.path.join('UI','Mana90%.png')).convert_alpha(),
    80: pygame.image.load(os.path.join('UI','Mana80%.png')).convert_alpha(),
    70: pygame.image.load(os.path.join('UI','Mana70%.png')).convert_alpha(),
    60: pygame.image.load(os.path.join('UI','Mana60%.png')).convert_alpha(),
    50: pygame.image.load(os.path.join('UI','Mana50%.png')).convert_alpha(),
    40: pygame.image.load(os.path.join('UI','Mana40%.png')).convert_alpha(),
    30: pygame.image.load(os.path.join('UI','Mana30%.png')).convert_alpha(),
    20: pygame.image.load(os.path.join('UI','Mana20%.png')).convert_alpha(),
    10: pygame.image.load(os.path.join('UI','Mana10%.png')).convert_alpha(),
    0: pygame.image.load(os.path.join('UI','Mana0%.png')).convert_alpha()
}

idle_frames = load_frames(os.path.join('icons', 'MCIdleRight'))
idle_left_frames = load_frames(os.path.join('icons', 'MCIdleLeft'))
walk_left_frames = load_frames(os.path.join('icons', 'MCWalkLeft'))
walk_right_frames = load_frames(os.path.join('icons', 'MCWalkRight'))
draw_sword_frames = load_frames(os.path.join('icons', 'MCDrawSword'))
attack_right_frames = load_frames(os.path.join('icons', 'MCAttackRight'))
attack_left_frames = load_frames(os.path.join('icons', 'MCAttackLeft'))
jump_attack_right_frames = load_frames(os.path.join('icons', 'MCJumpAttackRight'))
jump_attack_left_frames = load_frames(os.path.join('icons', 'MCJumpAttackLeft'))
jump_right_frames = load_frames(os.path.join('icons', 'MCJumpRight'))
jump_left_frames = load_frames(os.path.join('icons', 'MCJumpLeft'))

if idle_frames:
    main_character_rect = idle_frames[0].get_rect()
else:
    main_character_rect = pygame.Rect(0, 0, 50, 50)
player_hitbox = main_character_rect.copy()
player_hitbox.inflate_ip(-10, -10)

player_state = "idle"
current_frames = idle_frames
frame_index = 0
frame_delay = 200
attack_damage_done = False
attack1_done_time = 0
player_vx = 0
attack_cycle = 0
last_direction = "right"

class AttributeTree:
    def __init__(self):
        self.attributes = {
            "Physical Damage": 10,
            "Magical Damage": 0,
            "Sacred Damage": 0,
            "Physical Resistance": 1,
            "Magical Resistance": 1,
            "Sacred Resistance": 1,
            "Attack Speed": 1.0,
            "Health Regeneration": 1,
            "Mana Regeneration": 1
        }
        self.selected_attribute = 0
        self.attribute_names = list(self.attributes.keys())
    def draw(self):
        screen.fill(BLACK)
        title = medieval_font.render("Attribute Tree", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, attr in enumerate(self.attribute_names):
            color = WHITE if i == self.selected_attribute else GRAY
            text = small_medieval_font.render(f"{attr}: {self.attributes[attr]}", True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 150 + i * 50))
        pygame.display.flip()
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_attribute = (self.selected_attribute - 1) % len(self.attribute_names)
            elif event.key == pygame.K_DOWN:
                self.selected_attribute = (self.selected_attribute + 1) % len(self.attribute_names)
            elif event.key == pygame.K_RETURN:
                self.attributes[self.attribute_names[self.selected_attribute]] += 1

attribute_tree = AttributeTree()
player_stats = {"health": 100, "max_health": 100, "mana": 100, "max_mana": 100}
grass_tiles = find_grass_tiles(LEVEL1_LAYOUT, TILE_SIZE, SCREEN_HEIGHT)
tile_images = load_tile_images()

ground_attack_delay = 50
jump_attack_delay = 50
jump_attack_cooldown_value = 700
jump_attack_horizontal_speed = 3

class Particle:
    def __init__(self, pos):
        self.pos = list(pos)
        self.radius = random.randint(3, 6)
        self.life = random.randint(20, 40)
        self.vel = [random.uniform(-1, 1), random.uniform(-2, -0.5)]
        self.color = (150, 150, 150)
    def update(self):
        self.life -= 1
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]
        fade = max(0, int(255 * (self.life / 40)))
        self.color = (fade, fade, fade)
    def draw(self, surface):
        if self.life > 0:
            pygame.draw.circle(surface, self.color, (int(self.pos[0]), int(self.pos[1])), self.radius)

particles = []

class Wolf(pygame.sprite.Sprite):
    def __init__(self, x, y, attribute_tree, scale_factor=1.0):
        super().__init__()
        self.scale_factor = scale_factor
        self.speed = 2
        self.patrol_distance = 3 * TILE_SIZE
        self.direction = random.choice(["left", "right"])
        self.state = "patrolling"
        self.chase_cooldown = 2000
        self.last_attack_time = 0
        self.frame_index = 0
        self.last_frame_update = pygame.time.get_ticks()
        self.attack_move_distance = TILE_SIZE
        self.attack_move_progress = 0
        self.max_health = 50
        self.health = self.max_health
        self.last_damage_time = 0
        self.damage_cooldown = 1000
        self.attack_duration = 400
        self.original_speed = 2
        self.current_speed = self.original_speed
        self.can_deal_damage = False
        self.attribute_tree = attribute_tree
        self.jump_offset = 0
        self.images = {
            "walk_right": load_frames(os.path.join('enemies','WolfWalkRight'), self.scale_factor),
            "walk_left": load_frames(os.path.join('enemies','WolfWalkLeft'), self.scale_factor),
            "idle_right": load_frames(os.path.join('enemies','WolfIdleRight'), self.scale_factor),
            "idle_left": load_frames(os.path.join('enemies','WolfIdleLeft'), self.scale_factor),
            "attack_right": load_frames(os.path.join('enemies','WolfAttackRight'), self.scale_factor),
            "attack_left": load_frames(os.path.join('enemies','WolfAttackLeft'), self.scale_factor)
        }
        self.image = self.images["idle_right"][0]
        self.rect = self.image.get_rect(topleft=(x, y))
        self.hitbox = self.rect.copy()
        self.hitbox.inflate_ip(-10, -10)
        self.patrol_start_x = self.rect.x
        self.physical_damage = 19
        self.physical_resistance = 2
        self.magical_resistance = 1
    def update(self, player_hitbox, player_stats):
        now = pygame.time.get_ticks()
        distance = abs(self.rect.x - player_hitbox.x)
        if self.state != "attacking":
            self.state = "chasing" if distance < TILE_SIZE * 4 else "patrolling"
        if self.state == "patrolling":
            if self.direction == "right":
                self.rect.x += self.speed
                if self.rect.x >= self.patrol_start_x + self.patrol_distance:
                    self.direction = "left"
            else:
                self.rect.x -= self.speed
                if self.rect.x <= self.patrol_start_x - self.patrol_distance:
                    self.direction = "right"
        elif self.state == "chasing":
            if self.rect.colliderect(player_hitbox):
                self.attack(player_hitbox)
            else:
                self.rect.x += self.speed if self.rect.x < player_hitbox.x else -self.speed
        elif self.state == "attacking":
            if now - self.last_attack_time > self.attack_duration:
                self.state = "chasing"
        self.hitbox = self.rect.copy()
        self.hitbox.inflate_ip(-10, -10)
        self.animate()
        if self.state == "attacking" and self.can_deal_damage and self.hitbox.colliderect(player_hitbox):
            damage = max(0, (5 + attribute_tree.attributes["Physical Damage"]) - self.attribute_tree.attributes["Physical Resistance"])
            print(f"Wolf dealt {damage} damage to player!")
            player_stats["health"] -= damage
            self.can_deal_damage = False
    def attack(self, player_hitbox):
        now = pygame.time.get_ticks()
        if now - self.last_attack_time >= self.chase_cooldown:
            self.last_attack_time = now
            self.state = "attacking"
            self.attack_move_progress = 0
            self.jump_offset = -10
            self.direction = "right" if player_hitbox.centerx > self.rect.centerx else "left"
    def animate(self):
        now = pygame.time.get_ticks()
        delay = 100 if self.state == "attacking" else 150
        if now - self.last_frame_update > delay:
            if self.state == "attacking":
                anim = f"attack_{self.direction}"
                self.can_deal_damage = True if 2 <= self.frame_index < 4 else False
            else:
                self.can_deal_damage = False
            if self.state == "attacking":
                anim = f"attack_{self.direction}"
                if self.attack_move_progress < TILE_SIZE:
                    move_amt = 4
                    self.rect.x += move_amt if self.direction == "right" else -move_amt
                    self.attack_move_progress += move_amt
                if self.jump_offset < 0:
                    self.jump_offset += 1
            elif self.state in ["patrolling", "chasing"]:
                anim = f"walk_{self.direction}"
            else:
                anim = f"idle_{self.direction}"
            self.frame_index = (self.frame_index + 1) % len(self.images[anim])
            self.image = self.images[anim][self.frame_index]
            self.last_frame_update = now
    def take_damage(self, damage):
        print(f"Wolf took {damage} damage (Health: {self.health} -> {self.health-damage})")
        self.health -= max(0, damage)
        self.last_damage_time = pygame.time.get_ticks()
        if self.health <= 0:
            self.kill()
    def draw_health_bar(self, screen, offset_x):
        if self.health <= 0:
            return
        bar_width = 50
        bar_height = 5
        curr_width = (self.health / self.max_health) * bar_width
        x = self.rect.x - offset_x + (self.rect.width - bar_width) // 2
        y = self.rect.y - 10
        pygame.draw.rect(screen, (100, 100, 100), (x-2, y-2, bar_width+4, bar_height+4), 1)
        pygame.draw.rect(screen, (128, 0, 0), (x, y, bar_width, bar_height))
        for i in range(int(curr_width)):
            g = max(0, min(255, int(0.5 * (255 - i * 255 / bar_width))))
            b = max(0, min(255, int(0.5 * (255 - i * 255 / bar_width))))
            color = (255, g, b)
            pygame.draw.line(screen, color, (x + i, y), (x + i, y + bar_height))

class WolfSpawner:
    def __init__(self, player_rect, attribute_tree):
        self.player_rect = player_rect
        self.attribute_tree = attribute_tree
        self.spawn_interval = 10000
        self.last_spawn_time = 0
        self.wolves = pygame.sprite.Group()
        self.max_wolves = 8
    def spawn(self, force=False):
        if len(self.wolves) >= self.max_wolves:
            return
        now = pygame.time.get_ticks()
        if force or (now - self.last_spawn_time >= self.spawn_interval):
            positions = find_grass_tiles(LEVEL1_LAYOUT, TILE_SIZE, SCREEN_HEIGHT)
            if not positions:
                print("No grass tiles found.")
                return
            player_tile = self.player_rect.x // TILE_SIZE
            valid = [pos for pos in positions if 5 <= abs((pos[0] // TILE_SIZE) - player_tile) <= 15]
            if not valid:
                print(f"No valid spawns. Player at tile {player_tile}")
                return
            x, y = random.choice(valid)
            is_baby = random.random() < 0.2
            if is_baby:
                wolf = Wolf(x, y, self.attribute_tree, scale_factor=1.0)
                wolf.max_health = math.ceil(50 * 0.75)
                wolf.health = wolf.max_health
                wolf.physical_damage = math.ceil(19 * 0.75)
                wolf.physical_resistance = math.ceil(2 * 0.75)
                wolf.speed = math.ceil(2 * 1.10)
                print(f"Spawned baby wolf at ({x}, {y})")
            else:
                wolf = Wolf(x, y, self.attribute_tree, scale_factor=2.0)
                print(f"Spawned normal wolf at ({x}, {y})")
            wolf.rect.bottom = y
            self.wolves.add(wolf)
            self.last_spawn_time = now
    def update(self, player_hitbox, player_stats):
        self.spawn()
        for wolf in list(self.wolves):
            wolf.update(player_hitbox, player_stats)
            if wolf.health <= 0:
                wolf.kill()

def main_menu():
    menu_font = pygame.font.Font(medieval_font_path, 50)
    button_font = pygame.font.Font(medieval_font_path, 36)
    options = ["Start Game", "Resume Game", "Talent Tree", "Quit"]
    selected = 0
    while True:
        screen.fill(BLACK)
        title = menu_font.render("Sacred", True, WHITE)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, opt in enumerate(options):
            color = RED if i == selected else WHITE
            text = button_font.render(opt, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200 + i * 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    if options[selected] == "Start Game":
                        return "start"
                    elif options[selected] == "Resume Game":
                        return "resume"
                    elif options[selected] == "Talent Tree":
                        return "talent"
                    elif options[selected] == "Quit":
                        pygame.quit(); sys.exit()

def game_over_menu():
    menu_font = pygame.font.Font(medieval_font_path, 50)
    button_font = pygame.font.Font(medieval_font_path, 36)
    options = ["Back to Title Screen", "Quit"]
    selected = 0
    while True:
        screen.fill(BLACK)
        title = menu_font.render("You Died", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, opt in enumerate(options):
            color = RED if i == selected else WHITE
            text = button_font.render(opt, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200 + i * 60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected].lower().split()[0]

def save_game_state():
    state = {
        "player_pos": (main_character_rect.x, main_character_rect.y),
        "player_health": player_stats["health"],
        "attributes": attribute_tree.attributes
    }
    with open("savegame.pkl", "wb") as f:
        pickle.dump(state, f)

def load_game_state():
    if os.path.exists("savegame.pkl"):
        with open("savegame.pkl", "rb") as f:
            state = pickle.load(f)
        if state.get("player_health", 0) <= 0:
            return False
        main_character_rect.x, main_character_rect.y = state.get("player_pos", (main_character_rect.x, main_character_rect.y))
        player_stats["health"] = state.get("player_health", player_stats["health"])
        attribute_tree.attributes = state.get("attributes", attribute_tree.attributes)
        temp = main_character_rect.copy()
        temp.inflate_ip(-10, -10)
        return True
    return False

def talent_tree_menu():
    font = pygame.font.Font(medieval_font_path, 50)
    text = font.render("Talent Tree - Coming Soon!", True, WHITE)
    screen.fill(BLACK)
    screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()//2))
    pygame.display.flip()
    pygame.time.wait(2000)

def start_game():
    global player_state, current_frames, frame_index, attack_damage_done, spawner, last_jump_attack_time, jump_anim_time, player_hitbox, player_vx, last_direction
    last_direction = "right"
    set_state("idle", idle_frames, 200)
    attack_damage_done = False
    player_stats["health"] = player_stats["max_health"]
    main_character_rect.topleft = (grass_tiles[0][0],
                                   grass_tiles[0][1] - main_character_rect.height)
    player_hitbox = main_character_rect.copy()
    player_hitbox.inflate_ip(-10, -10)
    for frame in draw_sword_frames:
        draw_fixed_background(level_background)
        draw_level(LEVEL1_LAYOUT, tile_images, 0)
        screen.blit(frame, main_character_rect.topleft)
        pygame.display.flip()
        pygame.time.wait(150)
    sword_frame = draw_sword_frames[-1]
    intro_font = pygame.font.Font(medieval_font_path, 50)
    intro_text = intro_font.render("Level 1", True, WHITE)
    draw_fixed_background(level_background)
    draw_level(LEVEL1_LAYOUT, tile_images, 0)
    screen.blit(sword_frame, main_character_rect.topleft)
    screen.blit(intro_text, (SCREEN_WIDTH//2 - intro_text.get_width()//2, SCREEN_HEIGHT//2 - intro_text.get_height()//2 - 50))
    pygame.display.flip()
    pygame.time.wait(2000)
    spawner = WolfSpawner(main_character_rect, attribute_tree)
    last_jump_attack_time = 0
    jump_anim_time = 0
    player_vx = 0
    game_loop()

def resume_game():
    if not load_game_state():
        start_game()
    else:
        global spawner, last_jump_attack_time, jump_anim_time
        spawner = WolfSpawner(main_character_rect, attribute_tree)
        last_jump_attack_time = 0
        jump_anim_time = 0
        game_loop()

def game_loop():
    global player_state, current_frames, frame_index, attack_damage_done, last_jump_attack_time, attack1_done_time, jump_anim_time, player_vx, player_hitbox, attack_cycle, last_direction
    clock = pygame.time.Clock()
    running = True
    speed = 5
    air_speed_factor = 0.8
    jump_speed = 15
    gravity = 0.5
    is_jumping = False
    jump_velocity = 0
    last_update = pygame.time.get_ticks()
    last_regen_time = pygame.time.get_ticks()
    idle_frame_delay = 200
    walk_frame_delay = 100
    ground_attack_delay = 50
    jump_attack_delay = 50
    frame_delay = idle_frame_delay
    offset_x = 0
    last_direction = "right"
    player_vx = 0
    attack_cycle = 0

    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                save_game_state(); pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_u:
                    talent_tree_menu()
                if event.key == pygame.K_w and not is_jumping:
                    is_jumping = True
                    jump_velocity = -jump_speed
                    set_state("jump", jump_right_frames if last_direction=="right" else jump_left_frames, 100)
                if event.key in [pygame.K_a, pygame.K_d]:
                    if player_state.startswith("attack"):
                        if last_direction=="left":
                            set_state("idle", idle_left_frames, idle_frame_delay)
                        else:
                            set_state("idle", idle_frames, idle_frame_delay)
                        attack_cycle = 0
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if is_jumping:
                    if now - last_jump_attack_time >= jump_attack_cooldown_value:
                        set_state("jump_attack", jump_attack_right_frames if last_direction=="right" else jump_attack_left_frames, jump_attack_delay)
                        attack_damage_done = False
                        last_jump_attack_time = now
                        jump_velocity = 3
                else:
                    if player_state == "idle":
                        set_state("attack1", attack_right_frames[0:5] if last_direction=="right" else attack_left_frames[0:5], ground_attack_delay)
                        attack_damage_done = False
                        attack_cycle = 1
                    elif player_state == "attack1_done":
                        set_state("attack2", attack_right_frames[5:9] if last_direction=="right" else attack_left_frames[5:9], ground_attack_delay)
                        attack_damage_done = False
                        attack_cycle = 2

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            player_vx = -speed
            last_direction = "left"
        elif keys[pygame.K_d]:
            player_vx = speed
            last_direction = "right"
        else:
            if not is_jumping:
                player_vx = 0

        vx = int(player_vx * air_speed_factor) if is_jumping else player_vx
        main_character_rect.x += vx

        if not player_state.startswith("attack") and not is_jumping:
            if player_vx > 0:
                set_state("walk_right", walk_right_frames, walk_frame_delay)
            elif player_vx < 0:
                set_state("walk_left", walk_left_frames, walk_frame_delay)
            else:
                if last_direction=="left":
                    set_state("idle", idle_left_frames, idle_frame_delay)
                else:
                    set_state("idle", idle_frames, idle_frame_delay)

        if player_state.startswith("attack"):
            if keys[pygame.K_a]:
                last_direction = "left"
                if attack_cycle == 1:
                    current_frames = attack_left_frames[0:5]
                elif attack_cycle == 2:
                    current_frames = attack_left_frames[5:9]
            elif keys[pygame.K_d]:
                last_direction = "right"
                if attack_cycle == 1:
                    current_frames = attack_right_frames[0:5]
                elif attack_cycle == 2:
                    current_frames = attack_right_frames[5:9]

        if player_state.startswith("attack") and not attack_damage_done:
            extra = 20
            if last_direction=="right":
                atk_box = pygame.Rect(main_character_rect.right, main_character_rect.centery-20, int(TILE_SIZE//1.5)+extra, 40)
            else:
                atk_box = pygame.Rect(main_character_rect.left - int(TILE_SIZE//1.5)-extra, main_character_rect.centery-20, int(TILE_SIZE//1.5)+extra, 40)
            hit_frame = 2 if attack_cycle == 1 else 1
            if frame_index == hit_frame:
                for wolf in spawner.wolves:
                    if atk_box.colliderect(wolf.hitbox):
                        damage = max(0, (5 + attribute_tree.attributes["Physical Damage"]) - wolf.physical_resistance)
                        wolf.take_damage(damage)
                attack_damage_done = True

        if player_state == "attack1":
            if frame_index >= len(current_frames)-1:
                set_state("attack1_done", current_frames, ground_attack_delay)
                attack1_done_time = now
        elif player_state == "attack1_done":
            if now - attack1_done_time > 500:
                if last_direction=="left":
                    set_state("idle", idle_left_frames, idle_frame_delay)
                else:
                    set_state("idle", idle_frames, idle_frame_delay)
                attack_cycle = 0
                attack_damage_done = False
        elif player_state == "attack2":
            if frame_index >= len(current_frames)-1:
                if last_direction=="left":
                    set_state("idle", idle_left_frames, idle_frame_delay)
                else:
                    set_state("idle", idle_frames, idle_frame_delay)
                attack_cycle = 0
                attack_damage_done = False

        if is_jumping:
            if handle_vertical_collision(main_character_rect, LEVEL1_LAYOUT, TILE_SIZE, jump_velocity * gravity):
                is_jumping = False
                jump_velocity = 0
                if last_direction=="left":
                    set_state("idle", idle_left_frames, idle_frame_delay)
                else:
                    set_state("idle", idle_frames, idle_frame_delay)
            else:
                main_character_rect.y += jump_velocity * gravity
                jump_velocity += gravity

        if player_state == "jump":
            display_frame = (jump_right_frames[0] if last_direction=="right" else jump_left_frames[0]) if jump_velocity < 0 else (jump_right_frames[1] if last_direction=="right" else jump_left_frames[1])
        elif player_state in ["attack1", "attack2", "attack1_done"]:
            if now - last_update > frame_delay:
                frame_index += 1
                last_update = now
                if frame_index >= len(current_frames):
                    frame_index = len(current_frames)-1
            display_frame = current_frames[frame_index]
        elif player_state == "jump_attack":
            if now - last_update > frame_delay:
                frame_index = (frame_index + 1) % len(current_frames)
                last_update = now
            display_frame = current_frames[frame_index]
        else:
            if now - last_update > frame_delay:
                frame_index = (frame_index + 1) % len(current_frames)
                last_update = now
            display_frame = current_frames[frame_index]

        offset_x = main_character_rect.x - SCREEN_WIDTH//2
        if offset_x < 0:
            offset_x = 0

        player_hitbox = main_character_rect.copy()
        player_hitbox.inflate_ip(-10, -10)

        for p in particles[:]:
            p.update()
            if p.life <= 0:
                particles.remove(p)

        if now - last_regen_time > 1000:
            player_stats["health"] = min(player_stats["max_health"], player_stats["health"] + 1)
            last_regen_time = now

        draw_fixed_background(level_background)
        draw_level(LEVEL1_LAYOUT, tile_images, offset_x)
        screen.blit(apply_health_tint(display_frame, player_stats["health"] / player_stats["max_health"] * 100),
                    (main_character_rect.x - offset_x, main_character_rect.y))
        draw_health_bar(player_stats["health"], player_stats["max_health"], 10, 10)
        draw_mana_bar(player_stats["mana"], player_stats["max_mana"])
        spawner.update(player_hitbox, player_stats)
        for wolf in spawner.wolves:
            screen.blit(wolf.image, (wolf.rect.x - offset_x, wolf.rect.y + wolf.jump_offset))
            wolf.draw_health_bar(screen, offset_x)
        for p in particles:
            p.draw(screen)
        if DEBUG:
            pygame.draw.rect(screen, (0,255,0), player_hitbox, 2)
            if player_state.startswith("attack"):
                extra = 20
                if last_direction=="right":
                    atk_box = pygame.Rect(main_character_rect.right, main_character_rect.centery-20, int(TILE_SIZE//1.5)+extra, 40)
                else:
                    atk_box = pygame.Rect(main_character_rect.left - int(TILE_SIZE//1.5)-extra, main_character_rect.centery-20, int(TILE_SIZE//1.5)+extra, 40)
                pygame.draw.rect(screen, (255,0,0), atk_box, 2)
            if player_state=="jump_attack":
                atk_box = pygame.Rect(main_character_rect.x-30, main_character_rect.bottom-10, main_character_rect.width+60, 45)
                pygame.draw.rect(screen, (255,0,0), atk_box, 2)
            for wolf in spawner.wolves:
                pygame.draw.rect(screen, (0,0,255), wolf.hitbox, 2)
        pygame.display.flip()
        clock.tick(60)
        if player_stats["health"] <= 0:
            choice = game_over_menu()
            if choice=="back":
                main_menu_loop()
            else:
                pygame.quit(); sys.exit()
    pygame.quit()

def main_menu_loop():
    choice = main_menu()
    if choice=="start":
        start_game()
    elif choice=="resume":
        resume_game()
    elif choice=="talent":
        talent_tree_menu()
        main_menu_loop()
    elif choice=="quit":
        pygame.quit(); sys.exit()

def start_game():
    global player_state, current_frames, frame_index, attack_damage_done, spawner, last_jump_attack_time, jump_anim_time, player_hitbox, player_vx, last_direction
    last_direction = "right"
    set_state("idle", idle_frames, 200)
    attack_damage_done = False
    player_stats["health"] = player_stats["max_health"]
    main_character_rect.topleft = (grass_tiles[0][0],
                                   grass_tiles[0][1] - main_character_rect.height)
    player_hitbox = main_character_rect.copy()
    player_hitbox.inflate_ip(-10, -10)
    for frame in draw_sword_frames:
        draw_fixed_background(level_background)
        draw_level(LEVEL1_LAYOUT, tile_images, 0)
        screen.blit(frame, main_character_rect.topleft)
        pygame.display.flip()
        pygame.time.wait(150)
    sword_frame = draw_sword_frames[-1]
    intro_font = pygame.font.Font(medieval_font_path, 50)
    intro_text = intro_font.render("Level 1", True, WHITE)
    draw_fixed_background(level_background)
    draw_level(LEVEL1_LAYOUT, tile_images, 0)
    screen.blit(sword_frame, main_character_rect.topleft)
    screen.blit(intro_text, (SCREEN_WIDTH//2 - intro_text.get_width()//2, SCREEN_HEIGHT//2 - intro_text.get_height()//2 - 50))
    pygame.display.flip()
    pygame.time.wait(2000)
    spawner = WolfSpawner(main_character_rect, attribute_tree)
    last_jump_attack_time = 0
    jump_anim_time = 0
    player_vx = 0
    game_loop()

def resume_game():
    if not load_game_state():
        start_game()
    else:
        global spawner, last_jump_attack_time, jump_anim_time
        spawner = WolfSpawner(main_character_rect, attribute_tree)
        last_jump_attack_time = 0
        jump_anim_time = 0
        game_loop()

def talent_tree_menu():
    font = pygame.font.Font(medieval_font_path, 50)
    text = font.render("Talent Tree - Coming Soon!", True, WHITE)
    screen.fill(BLACK)
    screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, SCREEN_HEIGHT//2 - text.get_height()//2))
    pygame.display.flip()
    pygame.time.wait(2000)

def game_over_menu():
    font = pygame.font.Font(medieval_font_path, 50)
    options = ["Back to Title Screen", "Quit"]
    selected = 0
    while True:
        screen.fill(BLACK)
        title = font.render("You Died", True, RED)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
        for i, opt in enumerate(options):
            color = RED if i==selected else WHITE
            text = pygame.font.Font(medieval_font_path, 36).render(opt, True, color)
            screen.blit(text, (SCREEN_WIDTH//2 - text.get_width()//2, 200+i*60))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_UP:
                    selected = (selected-1)%len(options)
                elif event.key==pygame.K_DOWN:
                    selected = (selected+1)%len(options)
                elif event.key==pygame.K_RETURN:
                    return options[selected].lower().split()[0]

def save_game_state():
    state = {
        "player_pos": (main_character_rect.x, main_character_rect.y),
        "player_health": player_stats["health"],
        "attributes": attribute_tree.attributes
    }
    with open("savegame.pkl", "wb") as f:
        pickle.dump(state, f)

def load_game_state():
    if os.path.exists("savegame.pkl"):
        with open("savegame.pkl", "rb") as f:
            state = pickle.load(f)
        if state.get("player_health", 0) <= 0:
            return False
        main_character_rect.x, main_character_rect.y = state.get("player_pos", (main_character_rect.x, main_character_rect.y))
        player_stats["health"] = state.get("player_health", player_stats["health"])
        attribute_tree.attributes = state.get("attributes", attribute_tree.attributes)
        temp = main_character_rect.copy()
        temp.inflate_ip(-10,-10)
        return True
    return False

def main_menu_main():
    main_menu_loop()

if __name__ == "__main__":
    main_menu_main()
