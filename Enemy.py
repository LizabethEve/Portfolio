import customtkinter as ctk
#import os
import math
import time
#from tkinter import *
#from PIL import Image, ImageDraw

class Enemy:
    def __init__(self, parent, x=200, y=200):
        self.parent = parent
        self.x = float(x)
        self.y = float(y)

        #self.winston = ctk.CTkImage(Image.open('Images/Winston.png'),
            #size=(25, 25),
            #)
        #self.red_winston = ctk.CTkImage(Image.open('Images/Red_Winston.png'),
            #size=(25, 25)
            #)

        #self.health_bar = ctk.CTkProgressBar(self.parent.frame,
                                             #width=40,
                                             #height=6,
                                             #corner_radius=50,
                                             #border_width=3,
                                             #border_color="black",
                                             #fg_color="#362C39",
                                             #progress_color="#CF5555"
                                             #)
        #self.health_bar.set(0)
        #self.health_bar.place(x=self.x, y=self.y)

        # UI widget
        self.enemy = ctk.CTkButton(
            self.parent.frame,
            border_width=2,
            border_color="black",
            state="disabled",
            fg_color="#9263AF",
            bg_color="transparent",
            text="",
            height=25,
            width=25,
            #image=self.winston,
            corner_radius=50
        )
        self.enemy.place(x=self.x, y=self.y)

        # Enemy movement speed
        self.speed = 2.75

        # Collision radius
        self.player_collision_radius = 25
        self.projectile_hit_radius = 20

        # Combat stats
        self.hp = 3
        self.active = True
        self.enemies_dead = 0

        self.max_hp = self.hp
        self.health_visible_until = 0  # Timestamp until bar should remain visible

        self.health_bar = ctk.CTkProgressBar(
            self.parent.frame,
            width=40,
            height=6,
            corner_radius=5,
            fg_color="#3A2E39",
            progress_color="#CF5555"
        )
        self.health_bar.set(1)
        self.health_bar.place_forget()

        # Per enemy cooldown so they don't spam hits
        self.last_hit_time = 0.0
        self.hit_cooldown = 1.0

    # Move enemies toward the player
    def update(self, player_x, player_y):
        if not self.active:
            return

        dx = player_x - self.x
        dy = player_y - self.y
        dist = math.hypot(dx, dy)

        if dist == 0:
            return

        # Normalize direction
        nx = dx / dist
        ny = dy / dist

        # Move enemy
        self.x += nx * self.speed
        self.y += ny * self.speed

        # Update position on screen
        try:
            self.enemy.place(x=self.x, y=self.y)
            self.update_health_bar()
        except Exception:
            pass

    # Player collision/damage logic
    def check_player_collision(self, px, py):
        if not self.active:
            return False

        dx = self.x - px
        dy = self.y - py
        dist = math.hypot(dx, dy)
        return dist < self.player_collision_radius

    # Projectile collision logic
    def check_projectile_collision(self, proj):
        if not self.active:
            return False

        dx = (self.x + 12) - proj.x
        dy = (self.y + 12) - proj.y
        dist = math.hypot(dx, dy)

        return dist < self.projectile_hit_radius

# Display health bar above enemy when recently hit, similar to reload bar for player
    def update_health_bar(self):
        now = time.time()

        if now < self.health_visible_until and self.active:
            # Update percentage
            hp_ratio = max(self.hp / self.max_hp, 0)

            try:
                self.health_bar.set(hp_ratio)
                self.health_bar.place(x=self.x, y=self.y - 15)
            except:
                pass
        else:
            # Hide bar
            try:
                self.health_bar.place_forget()
            except:
                pass


    # Enemy take damage logic
    def take_damage(self, dmg):
        if not self.active:
            return

        self.hp -= dmg

        # Health bar visible for 2 seconds
        self.health_visible_until = time.time() + 2
        self.update_health_bar()

        # Flash on hit
        try:
            self.enemy.configure(fg_color="#CF5555")

            def reset_color_safe(enemy=self.enemy):
                try:
                    enemy.configure(fg_color="#9263AF")
                except:
                    # Widget was destroyed
                    pass

            self.parent.frame.after(120, reset_color_safe)

        except Exception:
            pass

        if self.hp <= 0:
            self.die()

# "Kill" the enemy
    def die(self):
        self.enemies_dead += 1
        self.active = False
        try:
            self.enemy.place_forget()
            self.health_bar.set(0)
            self.health_bar.place_forget()
            self.enemy.destroy()
        except Exception:
            pass
