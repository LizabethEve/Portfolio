import customtkinter as ctk
import time
import random
import math
import sys
#import tkinter as tk
from tkinter import *
from Character import Character
from Pause_Frame import MenuFrame
from Projectile import Projectile
from Enemy import Enemy
from Timer import Timer
from Weapons import Weapon
from Ammo_Drop import Ammo

# Enemies must spawn outside a 120 pixel radius of each other
SPAWN_MIN_DISTANCE = 120

# Checks all movements axis coordinates to keep enemies from spawning too close
def too_close(x1, y1, x2, y2):
    return math.dist((x1, y1), (x2, y2)) < SPAWN_MIN_DISTANCE


# The frame used for the game
class Frame:
    def __init__(self, root=None):
        # Initialize main frame
        if root is None:
            self.frame = ctk.CTk()
        else:
            self.frame = root

        # Customize frame
        self.frame.geometry("1920x1080")
        #self.frame.iconbitmap('Images/Winston.ico')
        self.frame.title("Compartmentalization Practice")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.frame.resizable(False, False)
        self.frame.configure(fg_color="#7AA257")

        # Create a Tk Canvas inside the CTk window
        #self.canvas = tk.Canvas(
            #self.frame,
            #width=1920,
            #height=1080,
            #highlightthickness=0,
            #bg="black"
        #)
        #self.canvas.place(x=0, y=0)


class Controls:
    def __init__(self, parent_app, frame, c, menu, p, weapon, t):
        # Connect to main frame and character
        self.parent = parent_app
        self.frame = frame
        self.c = c
        self.menu = menu
        self.p = p
        self.weapon = weapon
        self.t = t
        self.ammo = None

        # Initialize variables
        self.running = False
        self.after_id = None
        self.move_after_id = None  # ID returned by frame.after
        self.death_time = self.t.display_text
        self.player_dead = False
        self.enemies_spawned = []
        self.in_between_rounds_ammo = False
        self.ammo_spawned = []
        self.health_spawned = []
        self.redraw = True

        # Starting position
        self.player_y = 540.0
        self.player_x = 960.0

        self.ammo_pos_x = None
        self.ammo_pos_y = None

        # Mouse coordinates for targeting
        self.mouse_x = None
        self.mouse_y = None

        # Set of currently pressed keys
        self.pressed_keys = set()

        # Animation state
        self.animation_state = None
        self.reload_bar = ctk.CTkProgressBar(self.frame.frame,
            width=50,
            height=10,
            corner_radius=50,
            border_width=2,
            border_color="black",
            fg_color="#362C39",
            progress_color="#F1EC64"
            )
        self.reload_bar.set(0)
        self.reload_bar.place_forget()

        # Enemy Tracking
        self.enemies = []
        self.last_player_hit = 0
        self.player_hit_cooldown = 1.0

        self.timer_label = ctk.CTkLabel(self.frame.frame,
            text="00:00",
            text_color="#FFFBE1",
            fg_color="transparent",
            font=("Terminal", 24),
            )
        self.timer_label.place_forget()

        self.ammo_label = ctk.CTkLabel(self.frame.frame,
            text="Ammo: 0/0",
            font=("Terminal", 24),
            fg_color="transparent",
            text_color="#FFFBE1"
            )
        self.ammo_label.place_forget()

        self.wave_label = ctk.CTkLabel(self.frame.frame,
            text=f"Wave: {self.t.wave_number}",
            font=("Terminal", 24),
            fg_color="transparent",
            text_color="#FFFBE1"
            )
        self.wave_label.place_forget()

        # Projectile system
        self.projectiles = []  # List of Projectile instances
        self.proj_updater = None  # after() id for the projectile updater
        self.proj_tick_ms = 16  # Update interval
        # Start the projectile update loop
        self.start_projectile_updater()

        # Bind key events
        self.frame.frame.bind_all("<KeyPress>", self.key_press)
        self.frame.frame.bind_all("<KeyRelease>", self.key_release)
        self.frame.frame.bind_all("<Escape>", self.menu.pause_menu)
        self.frame.frame.bind_all("<Button-1>", self.attack)

        # Start the movement loop
        self.move_loop()
        print("Controls initialized: move_loop and projectile updates started.")

    # Animation position check and drawing functions
    def position_check(self):
        if self.animation_state == "Idle2":
            self.animation_state = "Idle1"
            self.draw1()
        elif self.animation_state == "Idle1":
            self.animation_state = "Idle2"
            self.draw2()
        else:
            self.animation_state = "Idle1"
            self.draw1()

    def draw1(self):
        if self.redraw == True:
            try:
                self.c.Character_Idle2.place_forget()
                self.c.Character_Idle1.place(x=self.player_x, y=self.player_y)
            except Exception:
                pass
        else:
            self.c.Character_Idle1.place_forget()
            self.c.Character_Idle2.place_forget()

    def draw2(self):
        if self.redraw == True:
            try:
                self.c.Character_Idle1.place_forget()
                self.c.Character_Idle2.place(x=self.player_x, y=self.player_y)
            except Exception:
                pass
        else:
            self.c.Character_Idle1.place_forget()
            self.c.Character_Idle2.place_forget()

# Key normalization and event handling
    def norm_key(self, k: str) -> str:
        k = k.lower()
        if k in ("shift", "shift_l", "shift_r"):
            return "shift"
        return k

# Key press and release handlers
    def key_press(self, event=None):
        key = self.norm_key(event.keysym)
        if key in ["w", "a", "s", "d"]:
            self.pressed_keys.add(key)

    def key_release(self, event):
        self.pressed_keys.discard(self.norm_key(event.keysym))
        if not self.pressed_keys:
            self.start()

# Movement functions
    def move_up(self):
        # Cancel any ongoing animation and cleanup
        if self.after_id:
            self.frame.frame.after_cancel(self.after_id)
            # Reset to not running
            self.after_id = None
            self.running = False

        # Forget idle/current sprite
        self.c.Character_Idle1.place_forget()
        self.c.Character_Idle2.place_forget()

        # Check for multiple keys being pressed for diagonal movement
        if self.player_y > 0:
            if len(self.pressed_keys) >= 2:
                # Adjust player coordinates slower for diagonal movement
                self.player_y -= 2.0
            else:
                # Adjust player coordinates
                self.player_y -= 3.0
        else:
            self.player_y += 1.0
        # Redraw at new position
        self.c.Character_Idle1.place(x=self.player_x, y=self.player_y)

    def move_right(self):
        if self.after_id:
            self.frame.frame.after_cancel(self.after_id)
            self.after_id = None
            self.running = False

        self.c.Character_Idle1.place_forget()
        self.c.Character_Idle2.place_forget()

        if self.player_x < 1895:
            if len(self.pressed_keys) >= 2:
                self.player_x += 2.0
            else:
                self.player_x += 3.0
        else:
            self.player_x -= 1.0
        self.c.Character_Idle1.place(x=self.player_x, y=self.player_y)

    def move_down(self):
        if self.after_id:
            self.frame.frame.after_cancel(self.after_id)
            self.after_id = None
            self.running = False

        self.c.Character_Idle1.place_forget()
        self.c.Character_Idle2.place_forget()

        if self.player_y < 1055:
            if len(self.pressed_keys) >= 2:
                self.player_y += 2.0
            else:
                self.player_y += 3.0
        else:
            self.player_y -= 1.0
        self.c.Character_Idle1.place(x=self.player_x, y=self.player_y)

    def move_left(self):
        if self.after_id:
            self.frame.frame.after_cancel(self.after_id)
            self.after_id = None
            self.running = False

        self.c.Character_Idle1.place_forget()
        self.c.Character_Idle2.place_forget()

        if self.player_x > 0:
            if len(self.pressed_keys) >= 2:
                self.player_x -= 2.0
            else:
                self.player_x -= 3.0
        else:
            self.player_x += 1.0
        self.c.Character_Idle1.place(x=self.player_x, y=self.player_y)

# Start and stop animation functions
    def start(self):
        self.running = True
        self.progress()

    def stop(self):
        self.running = False
        # Cancel any scheduled after calls
        if self.after_id is not None:
            self.frame.frame.after_cancel(self.after_id)
            self.after_id = None

# Timer based Idle animation function. .5 second intervals
    def progress(self):
        # Check to see if the animation is running, if not, exit
        if not self.running:
            return

        # On each .5 second, switch the character position
        self.position_check()

        # Call this function every .5 seconds
        self.after_id = self.frame.frame.after(500, self.progress)

# Movement loop to handle continuous movement, so holding down keys to move works
    def move_loop(self):
        self.weapon.update_reload()
        if self.redraw == True:
            if self.pressed_keys:
                if "w" in self.pressed_keys:
                    self.move_up()
                if "s" in self.pressed_keys:
                    self.move_down()
                if "a" in self.pressed_keys:
                    self.move_left()
                if "d" in self.pressed_keys:
                    self.move_right()

        # Enemy movement and collision
        now = time.time()
        for enemy in list(self.enemies):
            try:
                if not getattr(enemy, "active", True):
                    continue

                # If the enemy class doesn't provide last_hit_time / hit_cooldown, create them on the instance with safe defaults.
                if not hasattr(enemy, "last_hit_time"):
                    enemy.last_hit_time = 0.0
                if not hasattr(enemy, "hit_cooldown"):
                    enemy.hit_cooldown = 1.0

                # Prevents from crashes if something goes wrong with the enemy(ies)
                if hasattr(enemy, "update") and callable(getattr(enemy, "update")):
                    try:
                        chance = random.randint(1, 5)
                        if chance == 3:
                            side = random.randint(1, 2)
                            charge = random.randint(1, 2)
                            if side == 1:
                                if charge == 1:
                                    enemy.update(self.player_x + 5, self.player_y)
                                elif charge == 2:
                                    enemy.update(self.player_x - 5, self.player_y)
                            elif side == 2:
                                if charge == 1:
                                    enemy.update(self.player_x, self.player_y - 5)
                                elif charge == 2:
                                    enemy.update(self.player_x, self.player_y - 5)

                        else:
                            enemy.update(self.player_x, self.player_y)
                    except Exception as e:
                        # Keep going if a single enemy update fails
                        print("Enemy update error:", e)

                # Collision check if enemy provides check_player_collision
                if hasattr(enemy, "check_player_collision") and callable(getattr(enemy, "check_player_collision")):
                    try:
                        collided = enemy.check_player_collision(self.player_x, self.player_y)
                    except Exception as e:
                        print("Enemy collision check error:", e)
                        collided = False

                    if collided and (now - enemy.last_hit_time) >= enemy.hit_cooldown:
                        enemy.last_hit_time = now
                        self.player_hit()

            except Exception as outer_e:
                print("Unexpected error in move_loop for enemy:", outer_e)

        # Prevents enemies overlapping
        SEP_DIST = 20  # How far apart they should stay
        PUSH = 1.0     # How hard they push away per frame

        for i in range(len(self.enemies)):
            e1 = self.enemies[i]
            if not getattr(e1, "active", True):
                continue

            for j in range(i + 1, len(self.enemies)):
                e2 = self.enemies[j]
                if not getattr(e2, "active", True):
                    continue

                dx = e2.x - e1.x
                dy = e2.y - e1.y
                dist = math.hypot(dx, dy)

                if dist < SEP_DIST and dist > 0:
                    overlap = SEP_DIST - dist
                    nx = dx / dist
                    ny = dy / dist

                    move_amount = overlap * 0.5 * PUSH
                    e1.x -= nx * move_amount
                    e1.y -= ny * move_amount
                    e2.x += nx * move_amount
                    e2.y += ny * move_amount

                    e1.enemy.place(x=e1.x, y=e1.y)
                    e2.enemy.place(x=e2.x, y=e2.y)


        # Schedule the next frame
        try:
            self.move_after_id = self.frame.frame.after(16, self.move_loop)

        except Exception as e:
            print("Failed to schedule move_loop:", e)

        # Wave cleared check
        alive = [e for e in self.enemies if getattr(e, "active", True)]

        # If no enemies left AND not in a break
        if len(alive) == 0 and not self.parent.t.in_break:
            # Clear ammo
            try:
                for drop in list(self.ammo_spawned):
                    try:
                        drop["obj"].ammo_item.place_forget()
                    except Exception:
                        pass
                self.ammo_spawned.clear()
                self.ammo = None

                for drop in list(self.health_spawned):
                    try:
                        drop["obj"].health_drop.place_forget()
                    except Exception:
                        pass
                self.health_spawned.clear()
                self.health = None
            except Exception:
                pass
            if self.t.wave_number > 1:
                if self.c.player_health > 0:
                    #y_max = 1080
                    #y_min = 1
                    #x_max = 1920
                    #x_min = 1

                    #self.in_between_rounds_ammo = True

                    #self.ammo_pos_x = random.randint(x_min, x_max)
                    #self.ammo_pos_y = random.randint(y_min, y_max)

                    #self.spawn_ammo(self.ammo_pos_x, self.ammo_pos_y)
                    #self.ammo_spawned.append(self.spawn_ammo)
                    self.c.Character_Idle1.place_forget()
                    self.c.Character_Idle2.place_forget()
                    choice = random.choice(["pistol", "shotgun", "rifle"])
                    self.ammo_label.configure(text=f"{choice.upper()}: {self.weapon.ammo}/{self.weapon.max_ammo}\nAmmo: {self.weapon.ammo_stored}")
                    self.weapon.equip(choice)
                    self.menu.offer_pop_up()
                    self.redraw = False

            self.enemies_spawned.append(self.t.wave_number * 3)
            self.parent.t.notify_wave_cleared()

        # Pickup logic
        if self.ammo_spawned:
            for drop in list(self.ammo_spawned):
                dx = abs(self.player_x - drop["x"])
                dy = abs(self.player_y - drop["y"])
                if dx <= 17 and dy <= 17:
                    print("Picked up ammo at:", drop["x"], drop["y"], "player:", self.player_x, self.player_y)

                    # Change ammo
                    if self.t.in_break:
                        self.weapon.ammo_stored = 60
                    elif self.weapon.ammo_stored <= 54:
                        self.weapon.ammo_stored += 6
                    else:
                        self.weapon.ammo_stored = 60

                    self.weapon.ammo = self.weapon.max_ammo

                    # Remove ammo drop
                    try:
                        drop["obj"].ammo_item.place_forget()
                    except Exception:
                        pass

                    try:
                        self.ammo_spawned.remove(drop)
                    except ValueError:
                        pass

                    if getattr(self, "ammo", None) is drop["obj"]:
                        self.ammo = None
                    break

        if self.health_spawned:
            for drop in list(self.health_spawned):
                dx = abs(self.player_x - drop["x"])
                dy = abs(self.player_y - drop["y"])
                if dx <= 17 and dy <= 17:
                    # debug:
                    print("Picked up health at:", drop["x"], drop["y"], "player:", self.player_x, self.player_y)

                    if self.c.player_health < 20:
                        self.c.player_health += 1

                    # Remove health drop
                    try:
                        drop["obj"].health_drop.place_forget()
                    except Exception:
                        pass

                    try:
                        self.health_spawned.remove(drop)
                    except ValueError:
                        pass

                    if getattr(self, "health", None) is drop["obj"]:
                        self.health = None
                    break

        # HUD update
        if self.c.player_health > 0:
            self.c.character_health.set(self.c.player_health / 20)
        else:
            self.c.player_health = 0
            self.c.character_health.set(0)
        self.ammo_label.configure(text=f"{self.weapon.name.upper()}: {self.weapon.ammo}/{self.weapon.max_ammo}\nAmmo: {self.weapon.ammo_stored}")
        self.wave_label.configure(text=f"Wave: {self.t.wave_number}")

        progress = self.weapon.update_reload()

        if progress is not None and progress < 1.0:
            # Position reload bar above player
            self.reload_bar.place(x=self.player_x - 15, y=self.player_y - 20)
            self.reload_bar.set(progress)
        else:
            # On reload finished or not active → hide bar
            self.reload_bar.place_forget()

            #px = self.player_x
            #py = self.player_y - 20  # 20 px above player

    # Player hit flash
    def player_hit(self):
        if self.c.player_health <= 0:
            # Show death screen (menu handles logic to restart)

            not_dead = [e for e in self.enemies if getattr(e, "active", True)]
            spawned_this_wave = self.t.wave_number * 3
            spawned_previously = sum(self.enemies_spawned)
            spawned = spawned_this_wave + spawned_previously
            killed = spawned - len(not_dead)
            self.menu.eliminated = killed

            self.player_dead = True
            self.menu.death_screen()
            # Freeze player visuals and show death menu
            try:
                self.c.Character_Idle1.place_forget()
                self.c.Character_Idle2.place_forget()
                self.c.Character_Idle1.destroy()
                self.c.Character_Idle2.destroy()
            except Exception:
                pass
            # Clear lists but keep widgets destruction handled by App.restart later

            # Clear ammo
            try:
                for drop in list(self.ammo_spawned):
                    try:
                        drop["obj"].ammo_item.place_forget()
                    except Exception:
                        pass
                self.ammo_spawned.clear()
                self.ammo = None
            except Exception:
                pass

            try:
                for drop in list(self.health_spawned):
                    try:
                        drop["obj"].health_drop.place_forget()
                    except Exception:
                        pass
                self.health_spawned.clear()
                self.health = None
            except Exception:
                pass

            # Clear enemies
            try:
                for e in list(self.enemies):
                    try:
                        e.active = False
                        e.enemy.place_forget()
                        e.health_bar.place_forget()
                        e.enemy.destroy()
                    except Exception:
                        pass
                self.enemies.clear()
                self.projectiles.clear()
                self.pressed_keys.clear()
            except Exception:
                pass

            # Stop timer
            try:
                self.timer_label.configure(text=f"{self.death_time}")
                self.t.player_alive = False
            except Exception:
                pass
            return  # Exit early; avoid flashing multiple times

        try:
            # Flash both idle sprites if they exist
            if hasattr(self.c, "Character_Idle1"):
                try:
                    self.c.player_health -= 1
                    self.c.Character_Idle1.configure(fg_color="#CF5555")
                except Exception:
                    pass
            if hasattr(self.c, "Character_Idle2"):
                try:
                    self.c.player_health -= 1
                    self.c.Character_Idle2.configure(fg_color="#CF5555")
                except Exception:
                    pass

            # Restore after 480ms using a lambda
            def restore():
                try:
                    if hasattr(self.c, "Character_Idle1"):
                        self.c.Character_Idle1.configure(fg_color="#C979D6")
                except Exception:
                    pass
                try:
                    if hasattr(self.c, "Character_Idle2"):
                        self.c.Character_Idle2.configure(fg_color="#C979D6")
                except Exception:
                    pass

            if self.redraw == True:
                self.frame.frame.after(480, restore)
        except Exception as e:
            print("player_hit error:", e)

    # Hide projectile function
    def hide_projectile(self):
        self.present = False
        self.p.projectile.place_forget()

    # Handles all projectiles
    def start_projectile_updater(self):
        if self.proj_updater is None:
            # Schedule first call
            self.proj_updater = self.frame.frame.after(self.proj_tick_ms, self.update_projectiles)

# Called each tick to update all projectiles once
    def update_projectiles(self):
        try:
            to_remove = []
            for proj in list(self.projectiles):
                try:
                    still_active = proj.update()
                except Exception as e:
                    print("Projectile update error:", e)
                    still_active = False

                # Projectile–enemy collisions
                if still_active:
                    for enemy in list(self.enemies):
                        try:
                            if hasattr(enemy, "check_projectile_collision") and callable(
                                    getattr(enemy, "check_projectile_collision")):
                                hit = enemy.check_projectile_collision(proj)
                            else:
                                # Fallback simple distance check if enemy has x/y attributes
                                if hasattr(enemy, "x") and hasattr(enemy, "y") and hasattr(proj, "x") and hasattr(proj, "y"):
                                    dx = proj.x - enemy.x
                                    dy = proj.y - enemy.y
                                    hit = (dx * dx + dy * dy) <= (20 * 20)  # 20px radius
                                else:
                                    hit = False
                        except Exception as e:
                            print("Projectile->Enemy collision error:", e)
                            hit = False

                        if hit:
                            try:
                                enemy.take_damage(1)
                                # If enemy's hp is now 0 or less, perform death sequence + spawn ammo
                                if getattr(enemy, "hp", 0) <= 0:
                                    print("Enemy died at:", enemy.x, enemy.y)
                                    # Save enemy dead/inactive
                                    try:
                                        enemy.active = False
                                        if hasattr(enemy, "die") and callable(enemy.die):
                                            enemy.die()
                                        # "Kill" enemy
                                        if hasattr(enemy, "enemy"):
                                            try:
                                                choice = random.randint(1, 3)
                                                if choice == 2:
                                                    self.spawn_ammo(enemy.x, enemy.y)
                                                elif choice == 3:
                                                    self.spawn_health(enemy.x, enemy.y)
                                                enemy.enemy.place_forget()
                                                enemy.enemy.destroy()
                                            except Exception:
                                                pass
                                            if hasattr(enemy, "health_bar"):
                                                try:
                                                    enemy.health_bar.place_forget()
                                                    enemy.health_bar.destroy()
                                                except Exception:
                                                    pass
                                    except Exception as e:
                                        print("Error during enemy death cleanup:", e)
                                else:
                                    # Enemy still alive
                                    pass

                            except Exception as e:
                                print("Error applying damage to enemy:", e)

                            try:
                                proj.active = False
                                proj.projectile.place_forget()
                            except Exception:
                                pass

                            # Save projectile for removal
                            to_remove.append(proj)
                            break  # This projectile already hit an enemy

                if not still_active:
                    to_remove.append(proj)

            for r in to_remove:
                try:
                    if r in self.projectiles:
                        self.projectiles.remove(r)
                except Exception:
                    pass

        except Exception as outer:
            print("Unexpected error in update_projectiles:", outer)

        # Schedule next tick
        try:
            self.proj_updater = self.frame.frame.after(self.proj_tick_ms, self.update_projectiles)
        except Exception as e:
            print("Failed to schedule projectile updater:", e)

    def attack(self, event=None):
        if event is None:
            return

        # Update reload if ongoing
        self.weapon.update_reload()

        # Attempt to fire
        fired, reason = self.weapon.try_fire()

        if not fired:
            return

        # Get player center
        px = self.player_x + 15
        py = self.player_y + 15

        # Convert mouse position to coordinates inside the game frame
        win_x = self.frame.frame.winfo_rootx()
        win_y = self.frame.frame.winfo_rooty()
        tx = event.x_root - win_x
        ty = event.y_root - win_y

        # Fire different guns logic
        count = self.weapon.burst_count  # 1 for pistol/rifle, 3 for shotgun
        spread = self.weapon.spread
        speed = self.weapon.projectile_speed

        if count == 1:
            # Pistol and rifle
            proj = Projectile(self.frame)
            proj.fire(px, py, tx, ty, speed=speed)
            self.projectiles.append(proj)

        else:
            # Shotgun (3 rounds)
            start_angle = -(spread // 2)
            angle_step = spread // (count - 1)

            for i in range(count):
                ang = start_angle + i * angle_step
                proj = Projectile(self.frame)
                proj.fire(px, py, tx, ty, speed=speed, angle_offset=ang)
                self.projectiles.append(proj)

    def spawn_enemy(self, x=None, y=None):
        e = Enemy(self.frame, x=x, y=y)
        self.enemies.append(e)

    def spawn_ammo(self, x, y):
        ammo_x = int(round(x))
        ammo_y = int(round(y))

        ammo_obj = Ammo(self.frame.frame)
        ammo_obj.ammo_item.place(x=ammo_x, y=ammo_y)

        drop = {"obj": ammo_obj, "x": ammo_x, "y": ammo_y}
        self.ammo_spawned.append(drop)

        self.ammo = ammo_obj

    def spawn_health(self, x, y):
        health_x = int(round(x))
        health_y = int(round(y))

        health_obj = Ammo(self.frame.frame)
        health_obj.health_drop.place(x=health_x, y=health_y)

        drop = {"obj": health_obj, "x": health_x, "y": health_y}
        self.health_spawned.append(drop)

        self.health = health_obj


class Menu:
    def __init__(self, app, mf, t):
        # Stores app and frame wrapper for convenience
        self.app = app
        self.frame = app.frame
        self.mf = mf
        self.t = t

        self.eliminated = 0

    def quit_game(self):
        sys.exit(0)

    def restart_game(self):
        try:
            self.app.restart()
        except Exception as e:
            print("Menu.restart_game → app.restart() failed:", e)

    def death_screen(self, event=None):
        # Show the menu frame
        try:
            self.app.clear_offer_pop_up()
        except Exception as e:
            print(f"Offer window not valid\n{e}")
        self.mf.death_count_label.configure(text=f"Enemies killed: {self.eliminated}")
        self.mf.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.mf.dead_label.place(relx=0.5, rely=0.3, anchor="center")
        self.mf.quit_button.place(relx=0.7, rely=0.7, anchor="center")
        self.mf.restart_button.place(relx=0.3, rely=0.7, anchor="center")
        self.mf.death_count_label.place(relx=0.5, rely=0.5, anchor="center")
        self.mf.dead_label.configure(text=f"You died on wave {self.t.wave_number}")
        self.mf.quit_button.configure(command=lambda:self.quit_game())
        self.mf.restart_button.configure(command=lambda:self.restart_game())
        # Disable main frame interactions
        #self.frame.frame.attributes("-disabled", True)
        # Unbind the Escape key
        self.frame.frame.unbind_all("<Escape>")
        self.frame.frame.unbind_all("<KeyPress>")
        self.frame.frame.unbind_all("<Button-1>")
        #self.mf.menu_frame.attributes("-enabled", True)

    # Offer pop up for health or ammo between rounds
    def offer_pop_up(self):
        self.mf.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.mf.health_offer.place(relx=0.3, rely=0.6, anchor="center")
        self.mf.ammo_offer.place(relx=0.7, rely=0.6, anchor="center")
        self.mf.advance_label.place(relx=0.5, rely=0.3, anchor="center")
        self.mf.ammo_offer.configure(command=lambda:self.app.choose_ammo())
        self.mf.health_offer.configure(command=lambda:self.app.choose_health())

        self.frame.frame.unbind_all("<Escape>")
        self.frame.frame.unbind_all("<KeyPress>")
        self.frame.frame.unbind_all("<Button-1>")

    def pause_menu(self, event=None):
        self.mf.menu_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.frame.frame.attributes("-disabled", True)
        self.frame.frame.unbind_all("<Escape>")
        self.frame.frame.bind_all("<Escape>", self.resume_game)

    def resume_game(self, event=None):
        self.mf.menu_frame.place_forget()
        self.frame.frame.attributes("-disabled", False)
        self.frame.frame.unbind_all("<Escape>")
        self.frame.frame.bind_all("<Escape>", self.pause_menu)


# Main app class to initialize everything
class App:
    def __init__(self, root_override=None):
        if root_override is None:
            self.frame = ctk.CTk()
        else:
            self.frame = root_override


        # Initialize app frame
        self.frame = Frame(self.frame)
        # Initialize pause window connected to frame
        self.mf = MenuFrame(self.frame)
        # Initialize character connected to frame
        self.c = Character(self.frame)
        # Initialize projectile connected to frame
        self.p = Projectile(self.frame)
        # Initialize timer
        self.t = Timer(self)
        # Initialize pistol weapon
        self.weapon = Weapon(name="Pistol", max_ammo=6, reload_time=1, projectile_speed=8.0)

        # Initialize pause menu connected to frame and menu frame
        self.menu = Menu(self, self.mf, self.t)
        # Initialize controls connected to frame, character, menu, projectile, weapon, and timer
        self.controls = Controls(self, self.frame, self.c, self.menu, self.p, self.weapon, self.t)

        # Start the idle animation
        self.controls.wave_label.place(relx=0.99, rely=0.99, anchor="se")
        self.controls.timer_label.place(relx=0.5, rely=0.01, anchor="n")
        self.controls.ammo_label.place(relx=0.01, rely=0.99, anchor="sw")
        self.c.character_health.place(relx=0.01, rely=0.01, anchor="nw")
        self.controls.start()
        self.game_tick()


    def choose_health(self):
        self.c.character_health.set(1)
        self.c.player_health = 20
        self.clear_offer_pop_up()

    def choose_ammo(self):
        self.weapon.ammo_stored = 60
        self.controls.ammo_label.configure(text=f"Pistol: {self.weapon.ammo}/{self.weapon.max_ammo}\nAmmo: {self.weapon.ammo_stored}")
        self.clear_offer_pop_up()

    def clear_offer_pop_up(self):
        # Bind key events
        self.controls.redraw = True
        self.c.Character_Idle1.place(x=self.controls.player_x, y=self.controls.player_y)
        self.mf.advance_label.place_forget()
        self.mf.menu_frame.place_forget()
        self.mf.ammo_offer.place_forget()
        self.mf.health_offer.place_forget()
        self.frame.frame.bind_all("<KeyPress>", self.controls.key_press)
        self.frame.frame.bind_all("<KeyRelease>", self.controls.key_release)
        self.frame.frame.bind_all("<Escape>", self.menu.pause_menu)
        self.frame.frame.bind_all("<Button-1>", self.controls.attack)

    def spawn_enemy_wave(self):
        try:
            y_max = 1080
            y_min = 0
            x_max = 1920
            x_min = 0

            enemy_count = self.t.wave_number * 3

            for _ in range(enemy_count):
                # Picks spawn coordinates for enemies
                for attempt in range(30):

                    wall_choice = random.randint(1, 4)

                    if wall_choice == 1:
                        x = random.randint(x_min, x_max)
                        y = y_max
                    elif wall_choice == 2:
                        x = random.randint(x_min, x_max)
                        y = y_min
                    elif wall_choice == 3:
                        x = x_max
                        y = random.randint(y_min, y_max)
                    else:
                        x = x_min
                        y = random.randint(y_min, y_max)

                    # Checks if too close to existing enemies
                    too_close_to_any = False
                    for e in self.controls.enemies:
                        if too_close(x, y, e.x, e.y):
                            too_close_to_any = True
                            break

                    if not too_close_to_any:
                        break  # Valid position found

                self.controls.spawn_enemy(x, y)
        except Exception as e:
            print(f"Something went wrong spawning all  enemies.\n{e}")


    def game_tick(self):
        try:
            time_text, in_break = self.t.update()
        except Exception as e:
            #print("Timer update error:", e)
            time_text, in_break = f"{self.t.display_text}", False

        if in_break == True:
            self.controls.timer_label.configure(text=f"{time_text}   (Break)")
        else:
            self.controls.timer_label.configure(text=time_text)

        # Schedule next tick
        self.frame.frame.after(200, self.game_tick)

# Fully restart and reset game
    def restart(self):
        print("App.restart(): performing a full reset...")

        root = self.frame.frame

        # Cancel Controls timers/loops if present
        try:
            if hasattr(self.controls, "_move_after_id") and self.controls._move_after_id:
                root.after_cancel(self.controls._move_after_id)
        except Exception:
            pass
        try:
            if hasattr(self.controls, "_after_id") and self.controls._after_id:
                root.after_cancel(self.controls._after_id)
        except Exception:
            pass
        try:
            if hasattr(self.controls, "_proj_updater") and self.controls._proj_updater:
                root.after_cancel(self.controls._proj_updater)
        except Exception:
            pass

        # Unbind global events so new bindings won't conflict
        try:
            root.unbind_all("<KeyPress>")
            root.unbind_all("<KeyRelease>")
            root.unbind_all("<Escape>")
            root.unbind_all("<Button-1>")
        except Exception:
            pass

        # Clear game lists / save entities inactive
        try:
            if hasattr(self.controls, "enemies"):
                for e in list(self.controls.enemies):
                    try:
                        e.active = False
                        e.enemy.place_forget()
                        e.health_bar.place_forget()
                        e.enemy.destroy()
                    except Exception:
                        pass
                self.controls.enemies.clear()
        except Exception:
            pass

        try:
            if hasattr(self.controls, "projectiles"):
                for p in list(self.controls.projectiles):
                    try:
                        p.hide()
                        p.destroy()
                    except Exception:
                        pass
                self.controls.projectiles.clear()
        except Exception:
            pass

        # Destroy all widgets
        try:
            for w in root.winfo_children():
                try:
                    w.destroy()
                except Exception:
                    pass
        except Exception:
            pass

        # Reinitialize the entire App on the same root window with root_override to rebuild in-place.
        try:
            self.__init__(root_override=root)
        except Exception as e:
            print("App.restart(): re-init failed:", e)


if __name__ == "__main__":
    app = App()
    app.frame.frame.mainloop()