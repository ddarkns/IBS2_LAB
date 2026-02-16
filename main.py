# the_last_wick.py - Complete Game with Hand-Drawn Detailed Sprites
import pygame
import random
import math
import time
import sys

# Initialize Pygame
pygame.init()

# Get display info for fullscreen
display_info = pygame.display.Info()
FULLSCREEN_WIDTH = display_info.current_w
FULLSCREEN_HEIGHT = display_info.current_h

# Constants
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
FPS = 60
TITLE = "The Last Wick - A Vengeance for Peace"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
DARK_RED = (150, 0, 0)
GREEN = (50, 255, 50)
DARK_GREEN = (0, 100, 0)
BLUE = (50, 150, 255)
DARK_BLUE = (0, 0, 150)
YELLOW = (255, 255, 0)
GOLD = (255, 215, 0)
ORANGE = (255, 150, 0)
DARK_ORANGE = (200, 100, 0)
PURPLE = (180, 100, 255)
DARK_PURPLE = (100, 0, 100)
GRAY = (100, 100, 100)
DARK_GRAY = (30, 30, 30)
LIGHT_GRAY = (200, 200, 200)
BROWN = (139, 69, 19)
LIGHT_BROWN = (205, 133, 63)
DARK_BROWN = (101, 67, 33)
TAN = (210, 180, 140)
CREAM = (255, 253, 208)
CYAN = (100, 255, 255)
MAGENTA = (255, 0, 255)
STEEL = (70, 130, 180)
BRONZE = (205, 127, 50)
SILVER = (192, 192, 192)

# Game settings
PLAYER_START_X = 400
PLAYER_START_Y = 550
PLAYER_WIDTH = 40
PLAYER_HEIGHT = 50
PLAYER_SPEED = 5
PLAYER_JUMP_POWER = -15
PLAYER_GRAVITY = 0.8
PLAYER_MAX_HEALTH = 100

ATTACK_DAMAGE = 15
ATTACK_DURATION = 8
ATTACK_COOLDOWN = 20

# PARRY SETTINGS
PARRY_DURATION = 10
PARRY_WINDOW_START = 3
PARRY_WINDOW_END = 6
PARRY_COOLDOWN = 45

DODGE_DURATION = 15
DODGE_SPEED = 12
DODGE_COOLDOWN = 30
IFRAME_DURATION = 40

GROUND_Y = 600

# Setup display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Fonts
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 32)
font_cutscene = pygame.font.Font(None, 36)

class Particle:
    def __init__(self, x, y, color, velocity):
        self.x = x
        self.y = y
        self.color = color
        self.vx, self.vy = velocity
        self.life = 255
        self.size = random.randint(2, 5)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2
        self.vx *= 0.98
        self.vy *= 0.98
        self.life -= 6
        return self.life > 0
        
    def draw(self, screen, camera_x):
        if self.life > 0:
            alpha = min(255, self.life)
            color_with_alpha = (self.color[0], self.color[1], self.color[2], alpha)
            
            surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            pygame.draw.circle(surf, color_with_alpha, (self.size, self.size), self.size)
            screen.blit(surf, (self.x - camera_x - self.size, self.y - self.size))

class FloatingText:
    def __init__(self, x, y, text, color, size=28):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.font = pygame.font.Font(None, size)
        self.life = 60
        self.vy = -2
        self.scale = 1.0
        
    def update(self):
        self.y += self.vy
        self.life -= 2
        self.scale = 1.0 + (self.life / 60) * 0.5
        return self.life > 0
        
    def draw(self, screen, camera_x):
        if self.life <= 0:
            return
            
        alpha = min(255, self.life * 4)
        text_surf = self.font.render(self.text, True, self.color)
        text_surf.set_alpha(alpha)
        
        # Scale effect
        scaled_width = int(text_surf.get_width() * self.scale)
        scaled_height = int(text_surf.get_height() * self.scale)
        if scaled_width > 0 and scaled_height > 0:
            text_surf = pygame.transform.scale(text_surf, (scaled_width, scaled_height))
            
        screen.blit(text_surf, (self.x - camera_x - text_surf.get_width()//2, self.y - 30))

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.speed = PLAYER_SPEED
        self.health = PLAYER_MAX_HEALTH
        self.max_health = PLAYER_MAX_HEALTH
        self.facing_right = True
        self.on_ground = True
        
        # Animation
        self.animation_timer = 0
        self.leg_phase = 0
        
        # Attack
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_phase = 0
        
        # Parry
        self.is_parrying = False
        self.parry_timer = 0
        self.parry_window_active = False
        self.parry_success = False
        self.parry_cooldown = 0
        self.parry_window_frames = 0
        self.parry_glow = 0
        
        # Dodge
        self.is_dodging = False
        self.dodge_timer = 0
        self.dodge_cooldown = 0
        self.dodge_direction = 1
        self.dodge_trail = []
        
        # Invincibility
        self.invincible = False
        self.invincible_timer = 0
        
        # Score tracking
        self.perfect_parries = 0
        self.damage_taken = 0
        
    def handle_input(self, keys, mouse_buttons):
        self.vel_x = 0
        
        if not self.is_dodging:
            if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                self.vel_x = -self.speed
                self.facing_right = False
                self.animation_timer += 1
                if self.animation_timer > 5:
                    self.animation_timer = 0
                    self.leg_phase = 1 - self.leg_phase
            if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                self.vel_x = self.speed
                self.facing_right = True
                self.animation_timer += 1
                if self.animation_timer > 5:
                    self.animation_timer = 0
                    self.leg_phase = 1 - self.leg_phase
                    
            if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
                self.vel_y = PLAYER_JUMP_POWER
                self.on_ground = False
                
        if mouse_buttons[0] and self.attack_cooldown <= 0 and not self.is_parrying and not self.is_dodging:
            self.is_attacking = True
            self.attack_timer = ATTACK_DURATION
            self.attack_cooldown = ATTACK_COOLDOWN
            self.attack_phase = 0
            
        if mouse_buttons[2] and self.parry_cooldown <= 0 and not self.is_attacking and not self.is_dodging:
            self.is_parrying = True
            self.parry_timer = PARRY_DURATION
            self.parry_window_frames = 0
            self.parry_window_active = False
            self.parry_success = False
            self.parry_cooldown = PARRY_COOLDOWN
            self.parry_glow = 255
            
        if (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]) and self.dodge_cooldown <= 0 and not self.is_dodging:
            self.is_dodging = True
            self.dodge_timer = DODGE_DURATION
            self.dodge_direction = 1 if self.facing_right else -1
            self.dodge_cooldown = DODGE_COOLDOWN
            self.invincible = True
            self.invincible_timer = IFRAME_DURATION
            self.dodge_trail = []
            
    def update(self):
        self.vel_y += PLAYER_GRAVITY
        if self.y >= GROUND_Y:
            self.y = GROUND_Y
            self.vel_y = 0
            self.on_ground = True
            
        if self.is_dodging:
            self.vel_x = self.dodge_direction * DODGE_SPEED
            # Save trail position
            self.dodge_trail.append((self.x, self.y, 20))
            if len(self.dodge_trail) > 5:
                self.dodge_trail.pop(0)
                
        self.x += self.vel_x
        self.y += self.vel_y
        self.x = max(50, min(self.x, 2000))
        
        # Update trail alpha
        for i, trail in enumerate(self.dodge_trail):
            x, y, alpha = trail
            self.dodge_trail[i] = (x, y, alpha - 2)
        self.dodge_trail = [t for t in self.dodge_trail if t[2] > 0]
        
        if self.attack_timer > 0:
            self.attack_timer -= 1
            self.attack_phase += 1
            if self.attack_timer <= 0:
                self.is_attacking = False
                self.attack_phase = 0
                
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
            
        if self.parry_timer > 0:
            self.parry_timer -= 1
            self.parry_window_frames += 1
            self.parry_glow = max(0, self.parry_glow - 15)
            
            if self.parry_window_frames >= PARRY_WINDOW_START and self.parry_window_frames <= PARRY_WINDOW_END:
                self.parry_window_active = True
                self.parry_glow = 255
            else:
                self.parry_window_active = False
                
            if self.parry_timer <= 0:
                self.is_parrying = False
                self.parry_window_active = False
                
        if self.parry_cooldown > 0:
            self.parry_cooldown -= 1
            
        if self.dodge_timer > 0:
            self.dodge_timer -= 1
            if self.dodge_timer <= 0:
                self.is_dodging = False
                
        if self.dodge_cooldown > 0:
            self.dodge_cooldown -= 1
            
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
                
    def try_parry(self, enemy_x, enemy_y, attack_frame, attack_windup):
        if self.parry_window_active and not self.parry_success:
            distance = abs(enemy_x - self.x)
            if distance < 100:
                in_front = (enemy_x > self.x and self.facing_right) or (enemy_x < self.x and not self.facing_right)
                if in_front and attack_frame >= attack_windup - 3 and attack_frame <= attack_windup:
                    self.parry_success = True
                    self.parry_window_active = False
                    self.perfect_parries += 1
                    return True
        return False
        
    def take_damage(self, amount):
        if not self.invincible and not self.is_parrying and not self.is_dodging:
            self.health -= amount
            self.damage_taken += amount
            self.invincible = True
            self.invincible_timer = IFRAME_DURATION
            return True
        return False
        
    def get_attack_rect(self):
        attack_width = 60
        if self.facing_right:
            return pygame.Rect(self.x + self.width, self.y, attack_width, self.height)
        else:
            return pygame.Rect(self.x - attack_width, self.y, attack_width, self.height)
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        
        # Dodge trail
        for trail_x, trail_y, alpha in self.dodge_trail:
            trail_screen_x = trail_x - camera_x
            trail_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            trail_color = (*MAGENTA, alpha)
            pygame.draw.rect(trail_surf, trail_color, (0, 0, self.width, self.height))
            screen.blit(trail_surf, (trail_screen_x, trail_y))
        
        # Draw player with invincibility flash
        if self.invincible and (self.invincible_timer // 5) % 2 == 0:
            # Draw ghostly outline
            for offset in range(0, 360, 45):
                rad = math.radians(offset)
                ghost_x = screen_x + math.cos(rad) * 5
                ghost_y = self.y + math.sin(rad) * 5
                self.draw_knight(screen, ghost_x, ghost_y, WHITE, 100)
        
        # Draw main knight
        if self.is_parrying:
            if self.parry_window_active:
                self.draw_knight(screen, screen_x, self.y, CYAN, 255)
                # Parry glow
                glow_size = 40 + math.sin(pygame.time.get_ticks() * 0.02) * 10
                glow_surf = pygame.Surface((int(glow_size * 2), int(glow_size * 2)), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (255, 255, 100, self.parry_glow), 
                                 (int(glow_size), int(glow_size)), int(glow_size))
                screen.blit(glow_surf, (screen_x + self.width//2 - int(glow_size), self.y - int(glow_size)))
            else:
                self.draw_knight(screen, screen_x, self.y, (100, 200, 200), 200)
        elif self.is_dodging:
            self.draw_knight(screen, screen_x, self.y, MAGENTA, 255)
        elif self.is_attacking:
            self.draw_knight(screen, screen_x, self.y, (255, 200, 100), 255, self.attack_phase)
        else:
            self.draw_knight(screen, screen_x, self.y, BLUE, 255)
            
    def draw_knight(self, screen, x, y, armor_color, alpha=255, attack_phase=0):
        # Body (torso)
        body_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Chest plate
        pygame.draw.rect(body_surf, armor_color, (10, 10, 20, 25))
        # Shoulder pads
        pygame.draw.ellipse(body_surf, DARK_GRAY, (5, 8, 10, 12))
        pygame.draw.ellipse(body_surf, DARK_GRAY, (25, 8, 10, 12))
        
        # Helmet
        helmet_color = SILVER if armor_color == BLUE else armor_color
        pygame.draw.ellipse(body_surf, helmet_color, (12, 0, 16, 12))
        # Visor
        if self.facing_right:
            pygame.draw.rect(body_surf, BLACK, (20, 4, 4, 3))
        else:
            pygame.draw.rect(body_surf, BLACK, (16, 4, 4, 3))
            
        # Cape
        cape_color = DARK_RED if armor_color == BLUE else DARK_PURPLE
        pygame.draw.polygon(body_surf, cape_color, [(18, 15), (8, 30), (28, 30)])
        
        # Legs with walking animation
        leg_offset = 3 if self.leg_phase else -3
        pygame.draw.rect(body_surf, DARK_GRAY, (12, 35, 6, 10))
        pygame.draw.rect(body_surf, DARK_GRAY, (22, 35, 6, 10))
        # Moving leg
        if abs(self.vel_x) > 0 and self.on_ground:
            pygame.draw.rect(body_surf, GRAY, (12 + leg_offset, 40, 6, 8))
            pygame.draw.rect(body_surf, GRAY, (22 - leg_offset, 40, 6, 8))
            
        # Sword during attack
        if self.is_attacking:
            sword_color = SILVER
            if attack_phase < 4:
                # Windup
                sword_x = 35 if self.facing_right else -15
                pygame.draw.line(body_surf, sword_color, (25, 20), (25 + sword_x, 10), 4)
            else:
                # Strike
                sword_x = 45 if self.facing_right else -25
                pygame.draw.line(body_surf, sword_color, (25, 20), (25 + sword_x, 15), 6)
                # Sword trail
                trail_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.line(trail_surf, (255, 255, 100, 100), (10, 10), (20, 5), 4)
                if self.facing_right:
                    body_surf.blit(trail_surf, (35, 5))
                else:
                    body_surf.blit(pygame.transform.flip(trail_surf, True, False), (-25, 5))
        
        # Shield during parry
        if self.is_parrying:
            shield_x = 25 if self.facing_right else -5
            shield_color = CYAN if self.parry_window_active else (100, 200, 200)
            pygame.draw.ellipse(body_surf, shield_color, (shield_x, 15, 15, 20))
            pygame.draw.ellipse(body_surf, SILVER, (shield_x + 2, 17, 11, 16), 2)
            
        screen.blit(body_surf, (x, y))

class Enemy:
    def __init__(self, x, y, enemy_type="soldier", wave=1):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 40
        self.type = enemy_type
        self.wave = wave
        self.vel_x = 0  # Added vel_x for movement animation
        
        if enemy_type == "soldier":
            self.health = 60 + wave * 10
            self.max_health = self.health
            self.damage = 8 + wave
            self.speed = 1.5
            self.color = RED
            self.armor_color = DARK_RED
            self.weapon = "sword"
            
        elif enemy_type == "assassin":
            self.health = 45 + wave * 8
            self.max_health = self.health
            self.damage = 12 + wave
            self.speed = 2.5
            self.color = PURPLE
            self.armor_color = DARK_PURPLE
            self.weapon = "dagger"
            
        else:  # brute
            self.health = 90 + wave * 15
            self.max_health = self.health
            self.damage = 6 + wave
            self.speed = 1.0
            self.color = BROWN
            self.armor_color = DARK_BROWN
            self.weapon = "club"
            self.width = 35
            self.height = 45
            
        self.attack_cooldown = 0
        self.attack_windup = 0
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_duration = 30
        self.attack_delay = random.randint(40, 70)
        self.hit_timer = 0
        self.stunned = False
        self.stun_timer = 0
        
        # Animation
        self.animation_timer = 0
        self.leg_phase = 0
        self.facing_right = random.choice([True, False])
        
    def update(self, player_x):
        if self.stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.stunned = False
            return
            
        if not self.is_attacking and abs(self.x - player_x) > 60:
            if self.x < player_x:
                self.vel_x = self.speed
                self.x += self.speed
                self.facing_right = True
                self.animation_timer += 1
                if self.animation_timer > 5:
                    self.animation_timer = 0
                    self.leg_phase = 1 - self.leg_phase
            else:
                self.vel_x = -self.speed
                self.x -= self.speed
                self.facing_right = False
                self.animation_timer += 1
                if self.animation_timer > 5:
                    self.animation_timer = 0
                    self.leg_phase = 1 - self.leg_phase
        else:
            self.vel_x = 0
                
        if self.attack_cooldown <= 0 and not self.is_attacking:
            if abs(self.x - player_x) < 90:
                if random.random() < 0.02:
                    self.is_attacking = True
                    self.attack_windup = random.randint(20, 35)
                    self.attack_frame = 0
                
        if self.is_attacking:
            self.attack_frame += 1
            
            if self.attack_frame < self.attack_windup:
                pass
            elif self.attack_frame == self.attack_windup:
                self.attack_cooldown = random.randint(30, 60)
            elif self.attack_frame > self.attack_windup + 15:
                self.is_attacking = False
                
    def can_deal_damage(self):
        return (self.is_attacking and self.attack_frame == self.attack_windup)
        
    def get_attack_frame(self):
        return self.attack_frame if self.is_attacking else 0
        
    def get_attack_windup(self):
        return self.attack_windup if self.is_attacking else 0
        
    def take_damage(self, amount, is_perfect_parry=False):
        if is_perfect_parry:
            self.health = 0
            return True
        else:
            self.health -= amount
            self.hit_timer = 10
            self.stunned = True
            self.stun_timer = 10
            return self.health <= 0
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        
        # Hit flash
        if self.hit_timer > 0:
            self.hit_timer -= 1
            if (self.hit_timer // 2) % 2 == 0:
                self.draw_enemy(screen, screen_x, self.y, WHITE)
            else:
                self.draw_enemy(screen, screen_x, self.y, self.color)
        elif self.stunned:
            self.draw_enemy(screen, screen_x, self.y, GRAY)
        else:
            self.draw_enemy(screen, screen_x, self.y, self.color)
            
        # Attack indicator
        if self.is_attacking:
            if self.attack_frame < self.attack_windup:
                progress = self.attack_frame / self.attack_windup
                size = 20 + int(progress * 30)
                
                if self.attack_frame >= self.attack_windup - 5:
                    # Parry window
                    if (self.attack_frame // 2) % 2 == 0:
                        indicator_color = YELLOW
                    else:
                        indicator_color = GOLD
                    
                    if self.attack_frame >= self.attack_windup - 3:
                        parry_text = font_small.render("PARRY NOW!", True, YELLOW)
                        screen.blit(parry_text, (screen_x + self.width//2 - 50, self.y - 60))
                else:
                    indicator_color = ORANGE
                    
                # Draw attack indicator
                indicator_surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(indicator_surf, (*indicator_color, 200), (size, size), size, 3)
                screen.blit(indicator_surf, (screen_x + self.width//2 - size, self.y - size - 20))
            else:
                # Attack active
                if (self.attack_frame // 2) % 2 == 0:
                    attack_surf = pygame.Surface((40, 40), pygame.SRCALPHA)
                    pygame.draw.circle(attack_surf, (255, 0, 0, 200), (20, 20), 20, 4)
                    screen.blit(attack_surf, (screen_x + self.width//2 - 20, self.y - 40))
                             
        # Health bar
        bar_width = 50
        bar_height = 6
        health_percent = self.health / self.max_health
        bar_x = screen_x + (self.width - bar_width) // 2
        pygame.draw.rect(screen, DARK_RED, (bar_x, self.y - 15, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, self.y - 15, int(bar_width * health_percent), bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, self.y - 15, bar_width, bar_height), 1)
        
    def draw_enemy(self, screen, x, y, color):
        # Body
        body_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Armor
        pygame.draw.rect(body_surf, color, (5, 5, self.width-10, self.height-10))
        
        # Helmet
        helmet_color = DARK_GRAY if color == RED else color
        pygame.draw.ellipse(body_surf, helmet_color, (8, 0, self.width-16, 12))
        
        # Eyes
        if self.facing_right:
            eye_x = self.width - 12
        else:
            eye_x = 8
        pygame.draw.circle(body_surf, WHITE, (eye_x, 6), 2)
        pygame.draw.circle(body_surf, BLACK, (eye_x, 6), 1)
        
        # Weapon
        if self.weapon == "sword":
            if self.facing_right:
                pygame.draw.line(body_surf, GRAY, (self.width-5, 15), (self.width+15, 5), 4)
            else:
                pygame.draw.line(body_surf, GRAY, (5, 15), (-15, 5), 4)
        elif self.weapon == "dagger":
            if self.facing_right:
                pygame.draw.line(body_surf, SILVER, (self.width-5, 20), (self.width+10, 10), 2)
            else:
                pygame.draw.line(body_surf, SILVER, (5, 20), (-10, 10), 2)
        else:  # club
            if self.facing_right:
                pygame.draw.circle(body_surf, BROWN, (self.width+5, 15), 6)
            else:
                pygame.draw.circle(body_surf, BROWN, (-5, 15), 6)
                
        # Legs with animation
        leg_offset = 2 if self.leg_phase else -2
        pygame.draw.rect(body_surf, DARK_GRAY, (8, self.height-8, 5, 8))
        pygame.draw.rect(body_surf, DARK_GRAY, (self.width-13, self.height-8, 5, 8))
        if abs(self.vel_x) > 0:
            pygame.draw.rect(body_surf, GRAY, (8 + leg_offset, self.height-4, 5, 6))
            pygame.draw.rect(body_surf, GRAY, (self.width-13 - leg_offset, self.height-4, 5, 6))
            
        screen.blit(body_surf, (x, y))

class Boss:
    def __init__(self, x, y, boss_number):
        self.x = x
        self.y = y
        self.width = 80
        self.height = 100
        self.boss_number = boss_number
        self.vel_x = 0  # Added for consistency
        
        if boss_number == 1:
            self.name = "Gatekeeper"
            self.color = DARK_RED
            self.accent_color = GOLD
            self.health = 300
            self.max_health = 300
        elif boss_number == 2:
            self.name = "Shadow Assassin"
            self.color = DARK_PURPLE
            self.accent_color = SILVER
            self.health = 400
            self.max_health = 400
        else:
            self.name = "Ninja Lord"
            self.color = DARK_GRAY
            self.accent_color = GOLD
            self.health = 500
            self.max_health = 500
            
        self.perfect_parries_landed = 0
        self.perfect_parries_needed = 3
        self.is_stunned = False
        self.stun_timer = 0
        
        self.attack_patterns = []
        self.current_pattern = 0
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_type = ""
        self.attack_warning = False
        self.facing_right = True
        
        self.setup_attacks()
        
        # Animation
        self.float_offset = 0
        self.float_direction = 1
        self.glow_timer = 0
        
    def setup_attacks(self):
        if self.boss_number == 1:
            self.attack_patterns = [
                {"name": "Overhead Smash", "windup": 35, "damage_frame": 32, "damage": 15},
                {"name": "Shield Bash", "windup": 25, "damage_frame": 22, "damage": 12},
                {"name": "Wide Sweep", "windup": 40, "damage_frame": 37, "damage": 18}
            ]
        elif self.boss_number == 2:
            self.attack_patterns = [
                {"name": "Quick Slash", "windup": 20, "damage_frame": 17, "damage": 12},
                {"name": "Delayed Strike", "windup": 45, "damage_frame": 42, "damage": 20},
                {"name": "Shadow Dance", "windup": 30, "damage_frame": 27, "damage": 15}
            ]
        elif self.boss_number == 3:
            self.attack_patterns = [
                {"name": "Combo Starter", "windup": 25, "damage_frame": 22, "damage": 12},
                {"name": "Spin Attack", "windup": 35, "damage_frame": 32, "damage": 18},
                {"name": "Finishing Blow", "windup": 50, "damage_frame": 47, "damage": 25}
            ]
            
    def update(self, player_x):
        # Floating animation
        self.float_offset += 0.05 * self.float_direction
        if abs(self.float_offset) > 5:
            self.float_direction *= -1
            
        self.glow_timer += 1
            
        if self.is_stunned:
            self.stun_timer -= 1
            if self.stun_timer <= 0:
                self.is_stunned = False
                self.perfect_parries_landed = 0
            return
            
        # Face player
        self.facing_right = player_x > self.x
            
        if abs(self.x - player_x) > 100 and not self.is_attacking:
            if self.x < player_x:
                self.vel_x = 1
                self.x += 1
            else:
                self.vel_x = -1
                self.x -= 1
        else:
            self.vel_x = 0
                
        if self.attack_cooldown <= 0 and not self.is_attacking and not self.is_stunned:
            self.current_pattern = random.randint(0, len(self.attack_patterns) - 1)
            self.is_attacking = True
            self.attack_frame = 0
            self.attack_type = self.attack_patterns[self.current_pattern]["name"]
            self.attack_cooldown = random.randint(90, 150)
        else:
            self.attack_cooldown -= 1
            
        if self.is_attacking:
            self.attack_frame += 1
            pattern = self.attack_patterns[self.current_pattern]
            
            if self.attack_frame < pattern["windup"] - 10:
                self.attack_warning = True
            else:
                self.attack_warning = False
                
            if self.attack_frame > pattern["windup"] + 30:
                self.is_attacking = False
                
    def can_deal_damage(self):
        if not self.is_attacking or self.is_stunned:
            return False
        pattern = self.attack_patterns[self.current_pattern]
        return self.attack_frame == pattern["damage_frame"]
        
    def get_attack_frame(self):
        return self.attack_frame if self.is_attacking else 0
        
    def get_attack_windup(self):
        if self.is_attacking:
            pattern = self.attack_patterns[self.current_pattern]
            return pattern["windup"]
        return 0
        
    def get_current_damage(self):
        if self.is_attacking:
            pattern = self.attack_patterns[self.current_pattern]
            return pattern["damage"]
        return 0
        
    def take_damage(self, amount, is_perfect_parry=False):
        if is_perfect_parry and not self.is_stunned:
            self.perfect_parries_landed += 1
            if self.perfect_parries_landed >= self.perfect_parries_needed:
                self.is_stunned = True
                self.stun_timer = 120
                self.is_attacking = False
                return False
        elif not self.is_stunned:
            self.health -= amount
            return self.health <= 0
        return False
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
        
    def draw(self, screen, camera_x):
        screen_x = self.x - camera_x
        y = self.y + self.float_offset
        
        if self.is_stunned:
            color = GRAY
            accent = LIGHT_GRAY
        else:
            color = self.color
            accent = self.accent_color
            
        # Boss body
        body_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Main body
        pygame.draw.rect(body_surf, color, (10, 10, self.width-20, self.height-20))
        
        # Armor details
        if self.boss_number == 1:
            # Gatekeeper helmet
            pygame.draw.rect(body_surf, accent, (25, 0, 30, 15))
            pygame.draw.rect(body_surf, GRAY, (15, 5, 50, 5))
            # Shield
            pygame.draw.ellipse(body_surf, BRONZE, (40, 30, 25, 40))
        elif self.boss_number == 2:
            # Assassin mask
            pygame.draw.circle(body_surf, BLACK, (40, 20), 12)
            pygame.draw.circle(body_surf, RED, (35, 15), 3)
            pygame.draw.circle(body_surf, RED, (45, 15), 3)
            # Daggers
            pygame.draw.line(body_surf, SILVER, (60, 25), (75, 10), 4)
            pygame.draw.line(body_surf, SILVER, (20, 25), (5, 10), 4)
        elif self.boss_number == 3:
            # Ninja Lord armor
            pygame.draw.polygon(body_surf, accent, [(35, -5), (45, -15), (55, -5)])
            pygame.draw.line(body_surf, accent, (20, 20), (60, 20), 3)
            # Shoulder pads
            pygame.draw.ellipse(body_surf, DARK_GRAY, (0, 10, 15, 25))
            pygame.draw.ellipse(body_surf, DARK_GRAY, (65, 10, 15, 25))
            
        # Eyes (follow player slightly)
        if self.facing_right:
            eye_x = 45
        else:
            eye_x = 35
        pygame.draw.circle(body_surf, WHITE, (eye_x, 25), 4)
        pygame.draw.circle(body_surf, BLACK, (eye_x, 25), 2)
        
        screen.blit(body_surf, (screen_x, y))
        
        # Attack warning glow
        if self.attack_warning:
            glow_size = 80 + int(math.sin(self.glow_timer * 0.1) * 10)
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            alpha = 100 + int(math.sin(self.glow_timer * 0.05) * 50)
            pygame.draw.circle(glow_surf, (255, 0, 0, alpha), (glow_size, glow_size), glow_size)
            screen.blit(glow_surf, (screen_x + self.width//2 - glow_size, y - glow_size))
            
        # Attack animation
        if self.is_attacking:
            pattern = self.attack_patterns[self.current_pattern]
            progress = self.attack_frame / pattern["windup"]
            
            if self.attack_frame < pattern["windup"]:
                weapon_size = 25 + int(progress * 50)
                # Parry window indicator
                if self.attack_frame >= pattern["windup"] - 5:
                    color = YELLOW if (self.attack_frame // 2) % 2 == 0 else GOLD
                    if self.attack_frame >= pattern["windup"] - 3:
                        parry_text = font_medium.render("PARRY NOW!", True, YELLOW)
                        screen.blit(parry_text, (screen_x + 10, y - 80))
                else:
                    color = ORANGE if progress < 0.7 else RED
                    
                weapon_surf = pygame.Surface((weapon_size * 2, weapon_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(weapon_surf, (*color, 200), (weapon_size, weapon_size), weapon_size, 5)
                if self.facing_right:
                    screen.blit(weapon_surf, (screen_x + self.width, y + 20 - weapon_size))
                else:
                    screen.blit(weapon_surf, (screen_x - weapon_size * 2, y + 20 - weapon_size))
            else:
                # Attack active
                if (self.attack_frame // 3) % 2 == 0:
                    attack_surf = pygame.Surface((100, 100), pygame.SRCALPHA)
                    if self.facing_right:
                        pygame.draw.line(attack_surf, RED, (0, 50), (100, 50), 10)
                        screen.blit(attack_surf, (screen_x + self.width, y + 30))
                    else:
                        pygame.draw.line(attack_surf, RED, (100, 50), (0, 50), 10)
                        screen.blit(attack_surf, (screen_x - 100, y + 30))
                                   
        # Perfect parry counter
        for i in range(self.perfect_parries_needed):
            x_pos = screen_x + (i * 30)
            circle_y = y - 50
            if i < self.perfect_parries_landed:
                # Landed parry
                pygame.draw.circle(screen, GOLD, (x_pos + 15, circle_y), 12)
                pygame.draw.circle(screen, YELLOW, (x_pos + 15, circle_y), 8)
            else:
                # Needed parry
                pygame.draw.circle(screen, GRAY, (x_pos + 15, circle_y), 12, 3)
                
        # Health bar
        bar_width = 200
        bar_height = 20
        bar_x = screen_x + (self.width - bar_width) // 2
        health_percent = self.health / self.max_health
        pygame.draw.rect(screen, DARK_RED, (bar_x, y - 80, bar_width, bar_height))
        pygame.draw.rect(screen, GREEN, (bar_x, y - 80, int(bar_width * health_percent), bar_height))
        pygame.draw.rect(screen, WHITE, (bar_x, y - 80, bar_width, bar_height), 2)
        
        # Boss name
        name_surf = font_medium.render(self.name, True, self.accent_color)
        screen.blit(name_surf, (screen_x, y - 110))

class Game:
    def __init__(self):
        self.fullscreen = False
        self.state = "intro_cutscene"
        self.cutscene_page = 0
        self.cutscene_timer = 0
        
        self.level = 0
        self.score = 0
        self.start_time = 0
        self.best_time = self.load_best_time()
        
        self.player = None
        self.enemies = []
        self.boss = None
        self.particles = []
        self.floating_texts = []
        
        self.wave_count = 0
        self.camera_x = 0
        
        self.intro_text = [
            "The night the shadows came...",
            "Your clan fought bravely...",
            "But one by one, the candles were extinguished.",
            "Your brothers and sisters fell...",
            "You alone escaped... the last candle.",
            "You don't seek revenge...",
            "You seek peace for their restless souls.",
            "To relight the great hearth...",
            "And let them finally rest.",
            "",
            "Press SPACE to continue..."
        ]
        
        self.outro_text = [
            "You stand before the great hearth...",
            "The last candle flickers in your hand...",
            "As you light the flame...",
            "Ghostly figures appear around you...",
            "Your brothers and sisters... finally at peace.",
            "They smile and fade into the light.",
            "The castle is warm again.",
            "You are alone... but no longer lonely.",
            "",
            "THE END",
            "",
            "Press SPACE to return to menu"
        ]
        
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            screen = pygame.display.set_mode((FULLSCREEN_WIDTH, FULLSCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            
    def load_best_time(self):
        try:
            with open("best_time.txt", "r") as f:
                return float(f.read())
        except:
            return 999999
            
    def save_best_time(self):
        with open("best_time.txt", "w") as f:
            f.write(str(self.best_time))
            
    def new_game(self):
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)
        self.enemies = []
        self.boss = None
        self.level = 1
        self.wave_count = 0
        self.score = 0
        self.start_time = time.time()
        self.state = "playing"
        self.spawn_next_wave()
        
    def spawn_next_wave(self):
        self.wave_count += 1
        num_enemies = min(self.wave_count + 2, 6)
        
        for i in range(num_enemies):
            x = 800 + random.randint(0, 400) + i * 100
            y = GROUND_Y
            enemy_type = random.choice(["soldier", "assassin", "brute"])
            self.enemies.append(Enemy(x, y, enemy_type, self.level))
            
    def spawn_boss(self):
        self.boss = Boss(800, GROUND_Y - 50, self.level)
        self.enemies = []
        
    def add_particle_effect(self, x, y, color, count=10):
        for _ in range(count):
            vel = [random.uniform(-5, 5), random.uniform(-8, 0)]
            self.particles.append(Particle(x, y, color, vel))
            
    def add_floating_text(self, x, y, text, color):
        self.floating_texts.append(FloatingText(x, y, text, color))
        
    def update(self):
        if self.state == "intro_cutscene":
            self.cutscene_timer += 1
            
        elif self.state == "victory_cutscene":
            self.cutscene_timer += 1
            
        elif self.state == "playing":
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            
            self.player.handle_input(keys, mouse_buttons)
            self.player.update()
            self.camera_x = self.player.x - 400
            
            if self.wave_count >= 3 and not self.enemies and not self.boss:
                self.spawn_boss()
                self.state = "boss"
                
            for enemy in self.enemies[:]:
                enemy.update(self.player.x)
                
                if self.player.try_parry(enemy.x, enemy.y, enemy.get_attack_frame(), enemy.get_attack_windup()):
                    if enemy.take_damage(0, is_perfect_parry=True):
                        self.score += 200
                        self.add_particle_effect(enemy.x + enemy.width//2, enemy.y + enemy.height//2, GOLD, 20)
                        self.add_floating_text(enemy.x, enemy.y, "PERFECT PARRY!", GOLD)
                        self.enemies.remove(enemy)
                        
                if self.player.is_attacking:
                    attack_rect = self.player.get_attack_rect()
                    if attack_rect.colliderect(enemy.get_rect()):
                        if enemy.take_damage(ATTACK_DAMAGE, is_perfect_parry=False):
                            self.score += 100
                            self.add_particle_effect(enemy.x + enemy.width//2, enemy.y + enemy.height//2, RED, 15)
                            self.add_floating_text(enemy.x, enemy.y, str(ATTACK_DAMAGE), WHITE)
                            self.enemies.remove(enemy)
                        else:
                            self.add_floating_text(enemy.x, enemy.y, str(ATTACK_DAMAGE), WHITE)
                            
                if enemy.can_deal_damage():
                    if self.player.try_parry(enemy.x, enemy.y, enemy.get_attack_frame(), enemy.get_attack_windup()):
                        if enemy.take_damage(0, is_perfect_parry=True):
                            self.score += 200
                            self.add_particle_effect(enemy.x + enemy.width//2, enemy.y + enemy.height//2, GOLD, 20)
                            self.add_floating_text(enemy.x, enemy.y, "COUNTER!", GOLD)
                            self.enemies.remove(enemy)
                    else:
                        if self.player.take_damage(enemy.damage):
                            self.add_particle_effect(self.player.x + self.player.width//2, 
                                                   self.player.y + self.player.height//2, RED, 10)
                            self.add_floating_text(self.player.x, self.player.y, f"-{enemy.damage}", RED)
                            
            if not self.enemies and self.state == "playing" and self.wave_count < 3:
                self.spawn_next_wave()
                
        elif self.state == "boss":
            if self.boss:
                keys = pygame.key.get_pressed()
                mouse_buttons = pygame.mouse.get_pressed()
                self.player.handle_input(keys, mouse_buttons)
                self.player.update()
                self.camera_x = self.player.x - 400
                
                self.boss.update(self.player.x)
                
                if self.player.try_parry(self.boss.x, self.boss.y, self.boss.get_attack_frame(), self.boss.get_attack_windup()):
                    if self.boss.take_damage(0, is_perfect_parry=True):
                        self.add_particle_effect(self.boss.x + self.boss.width//2, 
                                               self.boss.y + self.boss.height//2, GOLD, 30)
                        self.add_floating_text(self.boss.x, self.boss.y, "PARRY!", GOLD)
                        
                        if self.boss.is_stunned:
                            self.add_floating_text(self.boss.x, self.boss.y, "STUNNED!", CYAN)
                            
                if self.player.is_attacking:
                    attack_rect = self.player.get_attack_rect()
                    if attack_rect.colliderect(self.boss.get_rect()):
                        if self.boss.take_damage(ATTACK_DAMAGE, is_perfect_parry=False):
                            self.score += 1000
                            self.add_particle_effect(self.boss.x + self.boss.width//2, 
                                                   self.boss.y + self.boss.height//2, GOLD, 50)
                            self.add_floating_text(self.boss.x, self.boss.y, "BOSS DEFEATED!", GOLD)
                            
                            if self.level >= 3:
                                final_time = time.time() - self.start_time
                                if final_time < self.best_time:
                                    self.best_time = final_time
                                    self.save_best_time()
                                self.state = "victory_cutscene"
                                self.cutscene_page = 0
                                self.cutscene_timer = 0
                                self.boss = None
                            else:
                                self.level += 1
                                self.wave_count = 0
                                self.boss = None
                                self.state = "playing"
                                self.spawn_next_wave()
                                
                if self.boss and self.boss.can_deal_damage():
                    if self.player.try_parry(self.boss.x, self.boss.y, self.boss.get_attack_frame(), self.boss.get_attack_windup()):
                        self.add_floating_text(self.boss.x, self.boss.y, "PARRY!", CYAN)
                        self.boss.take_damage(0, is_perfect_parry=True)
                    else:
                        damage = self.boss.get_current_damage()
                        if self.player.take_damage(damage):
                            self.add_particle_effect(self.player.x + self.player.width//2, 
                                                   self.player.y + self.player.height//2, RED, 15)
                            self.add_floating_text(self.player.x, self.player.y, f"-{damage}", RED)
                            
        if self.player and self.player.health <= 0:
            self.state = "game_over"
            
        self.particles = [p for p in self.particles if p.update()]
        self.floating_texts = [f for f in self.floating_texts if f.update()]
        
    def draw(self):
        # Sky gradient
        for i in range(WINDOW_HEIGHT):
            color_value = int(30 + (i / WINDOW_HEIGHT) * 50)
            pygame.draw.line(screen, (color_value, color_value, color_value), 
                           (0, i), (WINDOW_WIDTH, i))
        
        if self.state == "intro_cutscene":
            self.draw_intro_cutscene()
        elif self.state == "victory_cutscene":
            self.draw_victory_cutscene()
        elif self.state == "menu":
            self.draw_menu()
        elif self.state in ["playing", "boss"]:
            self.draw_game()
        elif self.state == "game_over":
            self.draw_game_over()
            
        pygame.display.flip()
        
    def draw_intro_cutscene(self):
        # Dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        # Draw candles
        for i in range(5):
            x = 200 + i * 200
            y = 300
            
            if i < 4:
                # Extinguished candles
                pygame.draw.rect(screen, GRAY, (x, y, 20, 80))
                pygame.draw.rect(screen, DARK_GRAY, (x, y, 20, 80), 3)
                # Smoke
                for s in range(3):
                    smoke_x = x + 10 + random.randint(-5, 5)
                    smoke_y = y - 20 - s * 10
                    pygame.draw.circle(screen, (50, 50, 50), (smoke_x, smoke_y), 8 + s)
            else:
                # Last standing candle
                pygame.draw.rect(screen, WHITE, (x, y, 20, 80))
                pygame.draw.rect(screen, GOLD, (x, y, 20, 80), 3)
                # Flame
                flame_points = [
                    (x + 10, y - 30),
                    (x, y - 10),
                    (x + 20, y - 10)
                ]
                pygame.draw.polygon(screen, YELLOW, flame_points)
                pygame.draw.polygon(screen, ORANGE, flame_points, 2)
                
        if self.cutscene_page < len(self.intro_text):
            text = self.intro_text[self.cutscene_page]
            visible_chars = min(self.cutscene_timer // 2, len(text))
            display_text = text[:visible_chars]
            
            # Text background
            text_bg = pygame.Surface((800, 80))
            text_bg.set_alpha(150)
            text_bg.fill(BLACK)
            screen.blit(text_bg, (200, 500))
            
            text_surf = font_cutscene.render(display_text, True, WHITE)
            screen.blit(text_surf, (250, 520))
            
    def draw_victory_cutscene(self):
        # Warm glow
        for i in range(WINDOW_HEIGHT):
            color_value = min(255, 50 + i // 3)
            pygame.draw.line(screen, (color_value, color_value // 2, 0), 
                           (0, i), (WINDOW_WIDTH, i))
        
        # Ghostly figures
        for i in range(4):
            x = 300 + i * 200
            y = 300
            alpha = 100 + int(math.sin(pygame.time.get_ticks() * 0.001 + i) * 50)
            
            ghost_surf = pygame.Surface((40, 70), pygame.SRCALPHA)
            # Ghost body
            pygame.draw.ellipse(ghost_surf, (200, 200, 255, alpha), (0, 0, 40, 70))
            # Eyes
            pygame.draw.circle(ghost_surf, (255, 255, 255, alpha), (12, 20), 4)
            pygame.draw.circle(ghost_surf, (255, 255, 255, alpha), (28, 20), 4)
            pygame.draw.circle(ghost_surf, (0, 0, 0, alpha), (12, 20), 2)
            pygame.draw.circle(ghost_surf, (0, 0, 0, alpha), (28, 20), 2)
            screen.blit(ghost_surf, (x, y))
            
        # Player
        player_surf = pygame.Surface((40, 60), pygame.SRCALPHA)
        pygame.draw.rect(player_surf, BLUE, (10, 10, 20, 40))
        pygame.draw.circle(player_surf, WHITE, (20, 15), 8)
        screen.blit(player_surf, (500, 300))
        
        # Great hearth
        hearth_x, hearth_y = 450, 400
        pygame.draw.rect(screen, BROWN, (hearth_x, hearth_y, 100, 50))
        # Fire
        for f in range(3):
            flame_y = hearth_y - 20 - f * 15
            flame_size = 30 - f * 8
            color = [YELLOW, ORANGE, RED][f]
            pygame.draw.circle(screen, color, (hearth_x + 50, flame_y), flame_size)
            
        if self.cutscene_page < len(self.outro_text):
            text = self.outro_text[self.cutscene_page]
            visible_chars = min(self.cutscene_timer // 2, len(text))
            display_text = text[:visible_chars]
            
            text_bg = pygame.Surface((900, 60))
            text_bg.set_alpha(150)
            text_bg.fill(BLACK)
            screen.blit(text_bg, (150, 600))
            
            color = GOLD if "THE END" in text else WHITE
            text_surf = font_cutscene.render(display_text, True, color)
            screen.blit(text_surf, (200, 615))
            
    def draw_menu(self):
        # Title with glow
        title = font_large.render("THE LAST WICK", True, ORANGE)
        title_x = WINDOW_WIDTH//2 - title.get_width()//2
        
        # Glow effect
        for offset in range(5, 0, -1):
            glow = font_large.render("THE LAST WICK", True, (255, 200, 0))
            glow.set_alpha(50 // offset)
            screen.blit(glow, (title_x - offset, 150 - offset))
            
        screen.blit(title, (title_x, 150))
        
        subtitle = font_medium.render("A Vengeance for Peace", True, WHITE)
        screen.blit(subtitle, (WINDOW_WIDTH//2 - subtitle.get_width()//2, 220))
        
        # Menu options with icons
        controls = [
            ("WASD/Arrows", "Move"),
            ("Space", "Jump"),
            ("Shift", "Dodge"),
            ("Left Click", "Attack"),
            ("Right Click", "Parry"),
            ("F", "Toggle Fullscreen"),
        ]
        
        y = 300
        for key, action in controls:
            # Key background
            key_bg = pygame.Surface((120, 30))
            key_bg.fill(DARK_GRAY)
            screen.blit(key_bg, (350, y))
            
            key_text = font_small.render(key, True, YELLOW)
            screen.blit(key_text, (360, y + 2))
            
            action_text = font_small.render(action, True, WHITE)
            screen.blit(action_text, (500, y + 2))
            
            y += 40
            
        # Game mechanics
        mech_y = 550
        mech_texts = [
            "PERFECT PARRY = Oneshot enemies",
            "Watch for the YELLOW glow - PARRY THEN!",
            "3 Perfect parries stun bosses",
        ]
        for text in mech_texts:
            color = GOLD if "PERFECT" in text else YELLOW if "YELLOW" in text else WHITE
            mech_surf = font_small.render(text, True, color)
            screen.blit(mech_surf, (WINDOW_WIDTH//2 - mech_surf.get_width()//2, mech_y))
            mech_y += 35
            
        # Start prompt
        start_text = font_medium.render("Press SPACE to begin", True, GREEN)
        start_rect = start_text.get_rect(center=(WINDOW_WIDTH//2, 700))
        # Pulsing effect
        pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) * 0.5
        start_text.set_alpha(150 + int(105 * pulse))
        screen.blit(start_text, start_rect)
        
    def draw_game(self):
        # Draw ground with texture
        ground_rect = pygame.Rect(0 - self.camera_x, GROUND_Y, 2000, 200)
        pygame.draw.rect(screen, DARK_GRAY, ground_rect)
        # Ground texture
        for i in range(0, 2000, 20):
            x = i - self.camera_x
            pygame.draw.line(screen, GRAY, (x, GROUND_Y), (x + 10, GROUND_Y + 10), 1)
        
        # Draw castle background
        for i in range(0, 2000, 300):
            x = i - self.camera_x
            # Castle walls
            pygame.draw.rect(screen, DARK_GRAY, (x, 300, 200, 300))
            # Windows
            for w in range(3):
                window_y = 350 + w * 80
                pygame.draw.rect(screen, YELLOW, (x + 50, window_y, 30, 40))
                pygame.draw.rect(screen, BLACK, (x + 50, window_y, 30, 40), 2)
            # Battlements
            for b in range(5):
                battlement_x = x + b * 40
                pygame.draw.rect(screen, GRAY, (battlement_x, 280, 30, 20))
                
        # Draw particles
        for p in self.particles:
            p.draw(screen, self.camera_x)
            
        # Draw floating text
        for text in self.floating_texts:
            text.draw(screen, self.camera_x)
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(screen, self.camera_x)
            
        # Draw boss
        if self.boss:
            self.boss.draw(screen, self.camera_x)
            
        # Draw player
        if self.player:
            self.player.draw(screen, self.camera_x)
            
        # UI Panel
        ui_panel = pygame.Surface((300, 150))
        ui_panel.set_alpha(150)
        ui_panel.fill(DARK_GRAY)
        screen.blit(ui_panel, (10, 10))
        
        # Level info
        level_text = font_medium.render(f"Level {self.level}/3", True, GOLD)
        screen.blit(level_text, (20, 20))
        
        if self.state == "playing":
            wave_text = font_small.render(f"Wave {self.wave_count}/3", True, WHITE)
            screen.blit(wave_text, (20, 55))
            
        # Score
        score_text = font_small.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (20, 80))
        
        # Time
        elapsed = time.time() - self.start_time
        time_text = font_small.render(f"Time: {elapsed:.1f}s", True, CYAN)
        screen.blit(time_text, (20, 105))
        
        # Best time
        if self.best_time < 999999:
            best_text = font_small.render(f"Best: {self.best_time:.1f}s", True, GOLD)
            screen.blit(best_text, (20, 130))
            
        # Parry count
        if self.player:
            parry_text = font_small.render(f"Perfect: {self.player.perfect_parries}", True, GOLD)
            screen.blit(parry_text, (150, 80))
            
        # Cooldown indicators
        if self.player and self.player.parry_cooldown > 0:
            cd_text = font_small.render("Parry Cooldown", True, GRAY)
            screen.blit(cd_text, (150, 105))
            
        # Health candle (detailed)
        if self.player:
            x, y = 850, 30
            # Candle holder
            pygame.draw.rect(screen, BRONZE, (x-5, y+80, 30, 10))
            pygame.draw.rect(screen, BRONZE, (x, y+70, 20, 15))
            
            # Candle body
            health_percent = self.player.health / self.player.max_health
            candle_height = int(70 * health_percent)
            pygame.draw.rect(screen, CREAM, (x, y + 70 - candle_height, 20, candle_height))
            pygame.draw.rect(screen, WHITE, (x, y + 70 - candle_height, 20, candle_height), 2)
            
            # Flame
            if health_percent > 0:
                flame_size = 15 + int(health_percent * 10)
                flame_points = [
                    (x + 10, y + 65 - flame_size),
                    (x, y + 70 - candle_height),
                    (x + 20, y + 70 - candle_height)
                ]
                pygame.draw.polygon(screen, YELLOW, flame_points)
                pygame.draw.polygon(screen, ORANGE, flame_points, 2)
                
    def draw_game_over(self):
        # Dark overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(200)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))
        
        title = font_large.render("THE FLAME DIED...", True, RED)
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, 250))
        
        score_text = font_medium.render(f"Score: {self.score}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH//2 - score_text.get_width()//2, 350))
        
        restart_text = font_medium.render("Press R to Restart or Q to Quit", True, WHITE)
        screen.blit(restart_text, (WINDOW_WIDTH//2 - restart_text.get_width()//2, 450))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.toggle_fullscreen()
                    
                elif self.state == "intro_cutscene":
                    if event.key == pygame.K_SPACE:
                        if self.cutscene_page < len(self.intro_text) - 1:
                            self.cutscene_page += 1
                            self.cutscene_timer = 0
                        else:
                            self.state = "menu"
                            
                elif self.state == "victory_cutscene":
                    if event.key == pygame.K_SPACE:
                        if self.cutscene_page < len(self.outro_text) - 1:
                            self.cutscene_page += 1
                            self.cutscene_timer = 0
                        else:
                            self.state = "menu"
                            
                elif self.state == "menu" and event.key == pygame.K_SPACE:
                    self.new_game()
                    
                elif self.state == "game_over":
                    if event.key == pygame.K_r:
                        self.state = "menu"
                    elif event.key == pygame.K_q:
                        return False
                        
        return True
        
    def run(self):
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            clock.tick(FPS)
            
        pygame.quit()
        sys.exit()

# Run the game
if __name__ == "__main__":
    game = Game()
    game.run()