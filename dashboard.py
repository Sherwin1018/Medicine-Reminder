import json
import os
from datetime import datetime
from kivy.clock import Clock
from plyer import notification

from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDIconButton, MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.dialog import MDDialog
from kivy.graphics import Color, Rectangle

REMINDERS_FILE = "reminders.json"
TRACK_FILE = "tracker.json"

def rgb(r, g, b, a=255):
    return (r / 255, g / 255, b / 255, a / 255)

class DashboardScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.notification_count = 0
        self.pending_notifications = []

        self.layout = MDBoxLayout(orientation="vertical")

        # === HEADER ===
        header = MDBoxLayout(orientation="horizontal", size_hint=(1, 0.13), padding=[10, 10, 10, 10], spacing=10)
        with header.canvas.before:
            Color(*rgb(25, 153, 178))
            self.header_bg = Rectangle()
        header.bind(pos=self._update_header_bg, size=self._update_header_bg)

        title = MDLabel(text="Smart Medicine Reminder", halign="left", valign="middle", theme_text_color="Custom", text_color=(1, 1, 1, 1), font_style="H6")
        self.notif_btn = MDIconButton(icon="bell-outline", theme_icon_color="Custom", icon_color=(1, 1, 1, 1), pos_hint={"center_y": 0.5}, on_press=self.on_notif_pressed)

        header.add_widget(title)
        header.add_widget(self.notif_btn)
        self.layout.add_widget(header)

        # === BODY ===
        self.scroll = MDScrollView(size_hint=(1, 0.87))
        self.inner_layout = MDBoxLayout(orientation="vertical", spacing=15, size_hint_y=None, padding=15)
        self.inner_layout.bind(minimum_height=self.inner_layout.setter("height"))

        self.top_row = MDGridLayout(cols=2, spacing=10, size_hint_y=None, height=120)
        self.active_card = self.create_card("✅ Active\nReminders", "None")
        self.today_card = self.create_card("📅 Today’s\nMedicines", "0", on_press=self.show_today_meds)

        self.top_row.add_widget(self.active_card)
        self.top_row.add_widget(self.today_card)
        self.inner_layout.add_widget(self.top_row)

        self.next_card = self.create_card("⏰ Next Reminder", "None")
        self.inner_layout.add_widget(self.next_card)

        self.scroll.add_widget(self.inner_layout)
        self.layout.add_widget(self.scroll)
        self.add_widget(self.layout)

        Clock.schedule_interval(self.check_reminder_times, 60)

    def on_pre_enter(self, *args):
        self.update_dashboard()

    def _update_header_bg(self, instance, value):
        self.header_bg.pos = instance.pos
        self.header_bg.size = instance.size

    def create_card(self, title, subtitle, on_press=None):
        card = MDCard(orientation="vertical", radius=[15], size_hint_y=None, height="100dp", md_bg_color=rgb(204, 240, 245), padding=10, elevation=3)
        label = MDLabel(text=f"{title}\n{subtitle}", halign="center", theme_text_color="Custom", text_color=rgb(37, 50, 55), font_style="Body1")
        card.add_widget(label)
        if on_press:
            card.on_touch_down = lambda touch: on_press() if card.collide_point(*touch.pos) else False
        return card

    def update_dashboard(self):
        now = datetime.now()
        active_count = 0
        today_meds = []
        next_reminder = None

        tracker_data = {}
        if os.path.exists(TRACK_FILE):
            with open(TRACK_FILE, "r") as f:
                try:
                    tracker_data = json.load(f)
                except:
                    tracker_data = {}

        reminders = []
        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, "r") as f:
                try:
                    reminders = json.load(f)
                except:
                    reminders = []

        for r in reminders:
            med = r.get("medicine")
            time_str = r.get("time")
            date_str = r.get("date")
            key = f"{med}_{date_str}"

            try:
                reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
            except:
                continue

            if date_str == now.strftime("%Y-%m-%d"):
                today_meds.append(f"{med} at {time_str}")

                if key in tracker_data:
                    status = tracker_data[key]
                    if status == "missed" and reminder_time < now:
                        active_count += 1
                else:
                    if reminder_time < now:
                        active_count += 1

            if reminder_time > now:
                if not next_reminder or reminder_time < next_reminder["time"]:
                    next_reminder = {"medicine": med, "time": reminder_time}

        self.active_card.children[0].text = f"✅ Active\nReminders\n{active_count}" if active_count else "✅ Active\nReminders\nNone"
        self.today_card.children[0].text = f"📅 Today’s\nMedicines\n{len(today_meds)}" if today_meds else "📅 Today’s\nMedicines\n0"
        if next_reminder:
            t = next_reminder["time"].strftime("%I:%M %p")
            self.next_card.children[0].text = f"⏰ Next Reminder\n{next_reminder['medicine']} - {t}"
        else:
            self.next_card.children[0].text = "⏰ Next Reminder\nNone"

        self.today_meds_list = today_meds

    def check_reminder_times(self, dt):
        now = datetime.now().replace(second=0, microsecond=0)

        if os.path.exists(REMINDERS_FILE):
            with open(REMINDERS_FILE, "r") as f:
                try:
                    reminders = json.load(f)
                except:
                    reminders = []

            for r in reminders:
                med = r.get("medicine")
                time_str = r.get("time")
                date_str = r.get("date")
                key = f"{med}_{date_str}_{time_str}"

                if date_str == now.strftime("%Y-%m-%d"):
                    try:
                        reminder_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %I:%M %p")
                        if reminder_time == now and key not in self.pending_notifications:
                            self.pending_notifications.append(key)
                            self.notification_count += 1
                            self.update_notif_icon()
                            self.play_notification_sound()
                    except:
                        continue

    def update_notif_icon(self):
        self.notif_btn.icon = "bell-ring" if self.notification_count > 0 else "bell-outline"

    def on_notif_pressed(self, instance):
        if not self.pending_notifications:
            self.dialog = MDDialog(
                title="Notifications",
                text="🔕 No new medicine reminders.",
                buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())]
            )
            self.dialog.open()
            return

        messages = []
        for key in self.pending_notifications:
            med_name = key.split("_")[0]
            messages.append(f"🕒 Please take your {med_name} medicine")

        self.dialog = MDDialog(
            title="Medicine Reminder",
            text="\n".join(messages),
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.clear_notifications())]
        )
        self.dialog.open()

    def clear_notifications(self):
        self.pending_notifications.clear()
        self.notification_count = 0
        self.update_notif_icon()
        if self.dialog:
            self.dialog.dismiss()

    def play_notification_sound(self):
        notification.notify(
            title="Medicine Reminder",
            message="You have a medicine to take!",
            timeout=5
        )

    def show_today_meds(self):
        if not self.today_meds_list:
            text = "All medicines taken or no reminders today."
        else:
            text = "\n".join(self.today_meds_list)

        self.dialog = MDDialog(
            title="Today's Medicines",
            text=text,
            size_hint=(0.8, None),
            height=300
        )
        self.dialog.open()

    def go_to_home(self, *args):
        if self.manager:
            self.manager.current = "dashboard"

    def go_to_add(self, *args):
        if self.manager:
            self.manager.current = "add_reminder"

    def go_to_view(self, *args):
        if self.manager:
            self.manager.current = "view_reminders"

    def go_to_tracker(self, *args):
        if self.manager:
            self.manager.current = "tracker"

    def go_to_settings(self, *args):
        if self.manager:
            self.manager.current = "settings"