import customtkinter as ctk


class Ammo:
    def __init__(self, parent):
        self.parent = parent

        self.ammo_item = ctk.CTkButton(self.parent,
            height=17,
            width=17,
            text="",
            state="disabled",
            corner_radius=5,
            border_width=2,
            border_color=("black"),
            fg_color=("#F1EC64"),
            )
        self.ammo_item.place_forget()

        self.health_drop = ctk.CTkButton(self.parent,
            height=17,
            width=17,
            text="",
            state="disabled",
            corner_radius=5,
            border_width=2,
            border_color=("black"),
            fg_color=("#CF5555"),
            )
        self.health_drop.place_forget()