import customtkinter as ctk

class Character:
    def __init__(self, parent):
        self.parent = parent
        # Initialize both idle states for character
        self.Idle1()
        self.Idle2()
        self.Character_Idle1.place_forget()
        self.Character_Idle2.place_forget()

        self.player_health = 20

        self.character_health = ctk.CTkProgressBar(
            self.parent.frame,
            width=100,
            height=25,
            corner_radius=25,
            fg_color="#3A2E39",
            progress_color="#CF5555",
            border_width=3,
            border_color="black"
        )
        self.character_health.set(1)
        self.character_health.place_forget()

# Character Idle States
    def Idle1(self):
        self.Character_Idle1 = ctk.CTkButton(self.parent.frame,
            fg_color="#C979D6",
            bg_color="transparent",
            state="disabled",
            width=25,
            height=25,
            border_color="black",
            border_width=2,
            corner_radius=50,
            text=""
            )

    def Idle2(self):
        self.Character_Idle2 = ctk.CTkButton(self.parent.frame,
            fg_color="#C979D6",
            bg_color="transparent",
            state="disabled",
            width=25,
            height=23,
            border_color="black",
            border_width=2,
            corner_radius=50,
            text=""
            )