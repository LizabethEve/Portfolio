import customtkinter as ctk
import math
import time


class Projectile:
    def __init__(self, parent):
        self.parent = parent
        self.projectile = ctk.CTkLabel(self.parent.frame,
            fg_color="#5C76FD",
            width=10,
            height=10,
            corner_radius=50,
            text=""
            )
        self.projectile.place_forget()

        # Projectile state/physics
        self.x = 0.0
        self.y = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.tx = None
        self.ty = None
        self.active = False
        self.speed = 8.0  # Projectile speed
        self.lifetime = 5000  # Projectile life span (5 seconds)
        self.spawn_time = None

    def fire(self, start_x, start_y, target_x, target_y, speed=None, angle_offset=0, spawn_time_ms=None):
        self.x = float(start_x - 10)
        self.y = float(start_y - 10)

        dx = float(target_x) - self.x
        dy = float(target_y) - self.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            self.active = False
            return

        if speed is not None:
            self.speed = float(speed)

        # Get firing angle
        angle = math.atan2(dy, dx)

        # Apply angle adjustment for shotgun
        angle += math.radians(angle_offset)

        # Get velocity based on adjusted angle
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed

        self.active = True
        self.spawn_time = time.time()
        self.projectile.place(x=self.x, y=self.y)

    # Move each projectile every tick
    def update(self):
        # Kill projectile after 6 seconds
        if self.spawn_time is not None and (time.time() - self.spawn_time) >= 6:
            self.hide()
            return False

        if not self.active:
            return False

        self.x += self.vx
        self.y += self.vy
        self.projectile.place(x=self.x, y=self.y)

        return True

    def hide(self):
        try:
            self.projectile.place_forget()
        except Exception:
            pass
        self.active = False

    def destroy(self):
        try:
            self.projectile.destroy()
        except Exception:
            pass
        self.active = False