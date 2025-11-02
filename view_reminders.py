import json
import os
from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivy.uix.anchorlayout import AnchorLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.dialog import MDDialog
from kivy.app import App

DATA_FILE = "reminders.json"

class ViewRemindersScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.delete_dialog = None

    def on_pre_enter(self, *args):
        self.load_reminders()

    def load_reminders(self):
        self.clear_widgets()

        anchor_layout = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))

        main_card = MDCard(
            padding=20,
            orientation="vertical",
            radius=[15],
            size_hint=(0.9, None),
            height=500,
            spacing=15,
            elevation=5,
        )

        main_card.add_widget(MDLabel(text="Your Reminders", halign="center", font_style="H5"))

        scroll = MDScrollView(size_hint=(1, None), height=350)
        list_layout = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        list_layout.bind(minimum_height=list_layout.setter("height"))

        reminders = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                try:
                    reminders = json.load(f)
                except json.JSONDecodeError:
                    reminders = []

        def parse_datetime(reminder):
            try:
                return datetime.strptime(f"{reminder.get('date', '')} {reminder.get('time', '')}", "%Y-%m-%d %I:%M %p")
            except:
                return datetime.min

        reminders = sorted(reminders, key=parse_datetime)

        if reminders:
            for idx, reminder in enumerate(reminders):
                medicine = reminder.get("medicine", "Unknown")
                time = reminder.get("time", "Unknown")
                date = reminder.get("date", "Unknown")

                record_card = MDCard(
                    padding=10,
                    orientation="vertical",
                    radius=[10],
                    size_hint_y=None,
                    height=100,
                    md_bg_color=(0.9, 0.95, 0.97, 1),
                )
                record_card.add_widget(MDLabel(
                    text=f"{medicine} - {date} at {time}",
                    halign="center",
                    theme_text_color="Primary"
                ))

                btn_layout = MDBoxLayout(orientation="horizontal", spacing=20, size_hint_y=None, height=40)
                edit_btn = MDRaisedButton(text="Edit", on_release=lambda x, i=idx: self.edit_reminder(i))
                delete_btn = MDFlatButton(text="Delete", on_release=lambda x, i=idx: self.delete_reminder(i))
                btn_layout.add_widget(edit_btn)
                btn_layout.add_widget(delete_btn)
                record_card.add_widget(btn_layout)

                list_layout.add_widget(record_card)
        else:
            list_layout.add_widget(MDLabel(text="No reminders yet.", halign="center", theme_text_color="Hint"))

        scroll.add_widget(list_layout)
        main_card.add_widget(scroll)

        back_btn = MDRaisedButton(
            text="Back",
            size_hint=(1, None),
            height=50,
            on_release=self.go_back
        )
        main_card.add_widget(back_btn)

        anchor_layout.add_widget(main_card)
        self.add_widget(anchor_layout)

    def edit_reminder(self, index):
        App.get_running_app().root.edit_index = index
        App.get_running_app().root.switch("edit_reminder")

    def delete_reminder(self, index):
        if not os.path.exists(DATA_FILE):
            return

        with open(DATA_FILE, "r") as f:
            reminders = json.load(f)

        removed = reminders.pop(index)

        with open(DATA_FILE, "w") as f:
            json.dump(reminders, f, indent=4)

        self.show_delete_dialog(removed.get("medicine", "Reminder"))
        self.load_reminders()

    def show_delete_dialog(self, med_name):
        if self.delete_dialog:
            self.delete_dialog.dismiss()
        self.delete_dialog = MDDialog(
            title="Deleted",
            text=f"🗑️ {med_name} Reminder Deleted Successfully",
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: self.delete_dialog.dismiss())
            ]
        )
        self.delete_dialog.open()

    def go_back(self, instance=None):
        App.get_running_app().root.go_back()
