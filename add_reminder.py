import json
import os
from datetime import datetime
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivy.uix.anchorlayout import AnchorLayout

DATA_FILE = "reminders.json"

class AddReminderScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.success_dialog = None

        anchor_layout = AnchorLayout(anchor_x="center", anchor_y="center", size_hint=(1, 1))

        form_card = MDCard(
            padding=20,
            orientation="vertical",
            radius=[15],
            size_hint=(0.9, None),
            height=420,
            elevation=5,
            spacing=20,
        )

        form_card.add_widget(MDLabel(text="Add Reminder", halign="center", font_style="H5"))

        self.medicine_input = MDTextField(hint_text="Medicine Name", mode="rectangle")
        self.time_input = MDTextField(hint_text="Time (e.g., 8:00 AM)", mode="rectangle")

        today = datetime.now().strftime("%Y-%m-%d")
        self.date_input = MDTextField(
            hint_text="Date (YYYY-MM-DD)",
            text=today,
            mode="rectangle"
        )

        form_card.add_widget(self.medicine_input)
        form_card.add_widget(self.time_input)
        form_card.add_widget(self.date_input)

        button_layout = MDBoxLayout(orientation="horizontal", spacing=20, size_hint_y=None, height=60)
        save_btn = MDRaisedButton(text="Save Reminder", on_release=self.save_reminder)
        back_btn = MDRaisedButton(text="Back", on_release=self.go_back)
        button_layout.add_widget(save_btn)
        button_layout.add_widget(back_btn)
        form_card.add_widget(button_layout)

        anchor_layout.add_widget(form_card)
        self.add_widget(anchor_layout)

    def show_success_dialog(self):
        if self.success_dialog:
            self.success_dialog.dismiss()
        self.success_dialog = MDDialog(
            title="Success",
            text="✅ Reminder Added Successfully",
            buttons=[
                MDFlatButton(text="OK", on_release=lambda x: self.success_dialog.dismiss())
            ]
        )
        self.success_dialog.open()

    def save_reminder(self, instance):
        med = self.medicine_input.text.strip()
        time = self.time_input.text.strip()
        date_text = self.date_input.text.strip()

        if not med or not time or not date_text:
            Snackbar(text="⚠️ Please fill in all fields", duration=2).open()
            return

        try:
            datetime.strptime(date_text, "%Y-%m-%d")
        except ValueError:
            Snackbar(text="⚠️ Invalid date format. Use YYYY-MM-DD", duration=2).open()
            return

        reminder = {
            "medicine": med,
            "time": time,
            "date": date_text
        }

        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    data = []
        else:
            data = []

        data.append(reminder)
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=4)

        self.medicine_input.text = ""
        self.time_input.text = ""
        self.date_input.text = datetime.now().strftime("%Y-%m-%d")

        self.show_success_dialog()

    def go_back(self, instance=None):
        from kivy.app import App
        App.get_running_app().root.go_back()
