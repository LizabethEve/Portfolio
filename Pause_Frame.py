import customtkinter as ctk


class MenuFrame:
    def __init__(self, parent):
        self.parent = parent
        self.menu_frame = ctk.CTkFrame(self.parent.frame,
            width=500,
            height=400,
            fg_color="#E1C284",
            corner_radius=50,
            border_width=5,
            border_color="#5B3F09",
            )
        self.menu_frame.place_forget()

        self.health_offer = ctk.CTkButton(self.menu_frame,
            fg_color="#E1C284",
            corner_radius=50,
            border_width=5,
            border_color="#5B3F09",
            text="Health",
            text_color="#5B3F09",
            font=("Terminal", 24),
            hover_color="#5B3F09",
            )
        self.health_offer.place_forget()

        self.ammo_offer = ctk.CTkButton(self.menu_frame,
            fg_color="#E1C284",
            corner_radius=50,
            border_width=5,
            border_color="#5B3F09",
            text="Ammo",
            text_color="#5B3F09",
            font=("Terminal", 24),
            hover_color="#5B3F09",
            )
        self.ammo_offer.place_forget()

        self.dead_label = ctk.CTkLabel(self.menu_frame,
            text="Dead",
            text_color="#5B3F09",
            font=("Terminal", 24),
            fg_color="#E1C284",
            )
        self.dead_label.place_forget()

        self.advance_label = ctk.CTkLabel(self.menu_frame,
            text="Which would you \nlike to refill?",
            text_color="#5B3F09",
            font=("Terminal", 24),
            fg_color="#E1C284",
            )
        self.advance_label.place_forget()

        self.death_count_label = ctk.CTkLabel(self.menu_frame,
            text="You killed _ enemies.",
            text_color="#5B3F09",
            font=("Terminal", 24),
            fg_color="#E1C284",
            )
        self.death_count_label.place_forget()

        self.restart_button = ctk.CTkButton(
            self.menu_frame,
            command=lambda: self.parent.restart_game(),
            border_width=5,
            border_color="#5B3F09",
            text="Restart",
            font=("Terminal", 24),
            text_color="#5B3F09",
            hover_color="#5B3F09",
            fg_color="#E1C284",
            corner_radius=25,
        )
        self.restart_button.place_forget()

        self.quit_button = ctk.CTkButton(
            self.menu_frame,
            command=lambda: self.parent.quit_game(),
            text="Quit",
            border_width=5,
            border_color="#5B3F09",
            font=("Terminal", 24),
            text_color="#5B3F09",
            hover_color="#5B3F09",
            fg_color="#E1C284",
            corner_radius=25,
        )
        self.quit_button.place_forget()

