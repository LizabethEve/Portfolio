import time


class Weapon:
    def __init__(self,
        name="Pistol",
        max_ammo=6,
        reload_time=1.0,
        projectile_speed=8.0,
        fire_rate=0.1,
        burst_count=1,
        spread=0,
        reload_amount=None):
        self.name = name

        # Ammo system
        self.max_ammo = max_ammo
        self.ammo = max_ammo
        self.ammo_stored = 60
        self.reload_time = reload_time
        self.reloading = False

        # Fire rate
        self.fire_rate = fire_rate
        self.last_shot = 0.0

        # Projectile settings
        self.projectile_speed = projectile_speed

        self.burst_count = burst_count
        self.spread = spread
        self.reload_amount = reload_amount or max_ammo

    # Change weapon
    def equip(self, weapon_name):
        self.name = weapon_name.lower()

        if self.name == "pistol":
            self.max_ammo = 6
            self.ammo = 6
            self.reload_time = 1.0
            self.fire_rate = 0.15
            self.projectile_speed = 8
            self.burst_count = 1
            self.spread = 0
            self.reload_amount = 6

        elif self.name == "shotgun":
            self.max_ammo = 2
            self.ammo = 2
            self.reload_time = 1.8
            self.fire_rate = 0.5
            self.projectile_speed = 7
            self.burst_count = 3  # three pellets
            self.spread = 15  # degrees
            self.reload_amount = 2

        elif self.name == "rifle":
            self.max_ammo = 30
            self.ammo = 30
            self.reload_time = 2.0
            self.fire_rate = 0.08  # fast
            self.projectile_speed = 10
            self.burst_count = 1
            self.spread = 0
            self.reload_amount = 30

    # Fire weapon unless no ammo
    def try_fire(self):
        now = time.time()

        if self.reloading:
            return False, "reloading"

        if self.ammo <= 0:
            self.start_reload()
            return False, "empty"

        if now - self.last_shot < self.fire_rate:
            return False, "cooldown"

        # Successful shot
        self.ammo -= 1
        self.last_shot = now

        if self.ammo <= 0:
            self.start_reload()

        return True, "fired"

    # Reload logic
    def start_reload(self):
        if self.reloading:
            return

        # Amount to reload
        amount = min(self.reload_amount, self.ammo_stored)

        if amount <= 0:
            return

        self.ammo_stored -= amount
        self.reload_amount_current = amount  # Keep track of how much to reload
        self.reloading = True
        self.reload_start = time.time()

    def update_reload(self):
        if not self.reloading:
            return None

        elapsed = time.time() - self.reload_start
        progress = elapsed / self.reload_time

        # Cap progress between 0 and 1
        if progress >= 1.0:
            self.reloading = False
            self.ammo = min(self.max_ammo, self.ammo + self.reload_amount_current)
            return 1.0

        return progress
