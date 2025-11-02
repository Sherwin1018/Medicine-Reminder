import json
import os
from datetime import datetime, timedelta
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivy.app import App

REMINDERS_FILE = "reminders.json"
TRACK_FILE = "tracker.json"

class TrackerScreen(MDScreen):
    def on_pre_enter(self):
        self.clear_widgets()
        self.build_ui()

    def build_ui(self):
        main = MDBoxLayout(orientation="vertical", padding=20, spacing=20)

        # === SUMMARY CARDS ===
        summary_box = MDBoxLayout(size_hint_y=None, height=120, spacing=20)

        self.taken_card = MDCard(orientation="vertical", padding=15, radius=[15], md_bg_color="#E8F5E9")
        self.taken_label = MDLabel(text="0", halign="center", font_style="H4")
        self.taken_card.add_widget(MDLabel(text="Taken", halign="center"))
        self.taken_card.add_widget(self.taken_label)

        self.missed_card = MDCard(orientation="vertical", padding=15, radius=[15], md_bg_color="#FFEBEE")
        self.missed_label = MDLabel(text="0", halign="center", font_style="H4")
        self.missed_card.add_widget(MDLabel(text="Missed", halign="center"))
        self.missed_card.add_widget(self.missed_label)

        summary_box.add_widget(self.taken_card)
        summary_box.add_widget(self.missed_card)

        # === DATE HEADER ===
        today_str = datetime.now().strftime("%Y-%m-%d")
        date_label = MDLabel(
            text=f"📅 {today_str}",
            halign="center",
            font_style="H6",
            bold=True,
            size_hint_y=None,
            height=40
        )

        # === SCROLLABLE MEDICINE LIST ===
        scroll = MDScrollView()
        self.list_box = MDBoxLayout(orientation="vertical", spacing=10, size_hint_y=None)
        self.list_box.bind(minimum_height=self.list_box.setter("height"))
        scroll.add_widget(self.list_box)

        main.add_widget(summary_box)
        main.add_widget(date_label)
        main.add_widget(scroll)

        # === BACK BUTTON ===
        back_btn = MDRaisedButton(
            text="Back",
            on_release=lambda x: self.go_back(),
            size_hint_y=None,
            height=50
        )
        main.add_widget(back_btn)

        self.add_widget(main)

        self.load_tracker_counts()
        self.load_reminders()

    def load_reminders(self):
        today = datetime.now().strftime("%Y-%m-%d")
        now = datetime.now()
        reminders = []

        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, "r") as f:
                try:
                    reminders = json.load(f)
                except json.JSONDecodeError:
                    reminders = []

        self.list_box.clear_widgets()

        for r in reminders:
            med_name = r.get("medicine", "Unknown")
            time_str = r.get("time", "00:00 AM")
            date_str = r.get("date", today)

            try:
                reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
            except:
                continue

            key = f"{med_name}_{date_str}"

            # === Past-day auto-mark missed ===
            if date_str < today:
                if not self.was_marked(med_name, date_str):
                    self.tracker_data[key] = "missed"
                continue

            # === Auto-miss if 2 hours passed and not taken ===
            if date_str == today and reminder_time + timedelta(hours=2) < now:
                if not self.was_marked(med_name, date_str):
                    self.tracker_data[key] = "missed"

            self.add_medicine_item(med_name, date_str, reminder_time)

        self.save_tracker_counts()
        self.update_summary_ui()

    def add_medicine_item(self, medicine_name, date_str, reminder_time):
        key = f"{medicine_name}_{date_str}"
        row = MDBoxLayout(orientation="horizontal", spacing=10, padding=10, size_hint_y=None, height=60)
        row.add_widget(MDLabel(text=medicine_name, halign="left"))

        if self.was_marked(medicine_name, date_str):
            status = self.tracker_data[key]
            status_label = MDLabel(
                text=f"Marked as {status.capitalize()}",
                halign="right",
                theme_text_color="Custom",
                text_color=("#4CAF50" if status == "taken" else "#E53935")
            )
            row.add_widget(status_label)
        else:
            now = datetime.now()
            if reminder_time + timedelta(hours=2) < now:
                self.tracker_data[key] = "missed"
                status_label = MDLabel(
                    text="Marked as Missed",
                    halign="right",
                    theme_text_color="Custom",
                    text_color="#E53935"
                )
                row.add_widget(status_label)
            else:
                taken_btn = MDRaisedButton(
                    text="Taken",
                    md_bg_color="#4CAF50",
                    on_release=lambda x: self.mark_and_replace(row, medicine_name, date_str, "taken")
                )
                missed_btn = MDRaisedButton(
                    text="Missed",
                    md_bg_color="#E53935",
                    on_release=lambda x: self.mark_and_replace(row, medicine_name, date_str, "missed")
                )
                row.add_widget(taken_btn)
                row.add_widget(missed_btn)

        self.list_box.add_widget(row)

    def mark_and_replace(self, row, medicine_name, date_str, status):
        key = f"{medicine_name}_{date_str}"
        if key in self.tracker_data:
            return

        self.tracker_data[key] = status
        if status == "taken":
            self.taken_count += 1
        else:
            self.missed_count += 1

        self.save_tracker_counts()
        self.update_summary_ui()

        row.clear_widgets()
        row.add_widget(MDLabel(text=medicine_name, halign="left"))
        status_label = MDLabel(
            text=f"Marked as {status.capitalize()}",
            halign="right",
            theme_text_color="Custom",
            text_color=("#4CAF50" if status == "taken" else "#E53935")
        )
        row.add_widget(status_label)

    def load_tracker_counts(self):
        self.taken_count = 0
        self.missed_count = 0
        self.tracker_data = {}

        if os.path.exists(TRACK_FILE):
            with open(TRACK_FILE, "r") as f:
                try:
                    self.tracker_data = json.load(f)
                except:
                    self.tracker_data = {}

        today = datetime.now().strftime("%Y-%m-%d")
        for key, status in self.tracker_data.items():
            if key.endswith(today):
                if status == "taken":
                    self.taken_count += 1
                elif status == "missed":
                    self.missed_count += 1

    def save_tracker_counts(self):
        self.tracker_data["taken"] = self.taken_count
        self.tracker_data["missed"] = self.missed_count
        with open(TRACK_FILE, "w") as f:
            json.dump(self.tracker_data, f, indent=4)

    def update_summary_ui(self):
        self.taken_label.text = str(self.taken_count)
        self.missed_label.text = str(self.missed_count)

    def was_marked(self, medicine_name, date_str):
        key = f"{medicine_name}_{date_str}"
        return key in self.tracker_data

    def go_back(self):
        App.get_running_app().root.go_back()
