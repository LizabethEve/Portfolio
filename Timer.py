import time

class Timer:
    def __init__(self, parent):
        self.parent = parent

        # Game clock
        self.start_time = time.time()
        self.last_update = self.start_time

        # Wave system
        self.wave_length = 60       # Max duration of a wave
        self.break_length = 10
        self.in_break = False
        self.wave_number = 0
        self.last_wave_number = 0
        self.player_alive = True

        # Timer for the next event
        self.next_event_time = self.start_time + self.wave_length

        # Visible timer text
        self.display_text = "00:00"

    def get_time_string(self, seconds):
        m = int(seconds // 60)
        s = int(seconds % 60)
        return f"{m:02d}:{s:02d}"

    def start_break(self):
        self.last_wave_number += 1
        self.in_break = True
        self.next_event_time = time.time() + self.break_length
        print("Break started")

    def start_wave(self):
        self.in_break = False
        self.wave_number += 1
        print(f"Wave {self.wave_number} starting")
        self.parent.spawn_enemy_wave()
        self.next_event_time = time.time() + self.wave_length

    def notify_wave_cleared(self):
        if not self.in_break:
            self.start_break()

    def update(self):
        if self.player_alive == True:
            now = time.time()
            elapsed = now - self.start_time
            self.display_text = self.get_time_string(elapsed)

            if self.wave_number < 1:
               self.start_wave()
            # Normal time based events
            elif now >= self.next_event_time:

                if not self.in_break:
                    # Stop wave if it's been too long
                    self.start_break()
                else:
                    # Stop break and start next wave
                    self.start_wave()

            return self.display_text, self.in_break
