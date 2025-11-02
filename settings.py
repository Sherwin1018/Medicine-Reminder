from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.card import MDCard
from kivymd.uix.selectioncontrol import MDSwitch
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.scrollview import MDScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp

class SettingsScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        scroll = MDScrollView(size_hint=(1, 1), do_scroll_x=False)

        content = MDBoxLayout(
            orientation="vertical",
            padding=[dp(20), dp(20), dp(20), dp(20)],
            spacing=dp(25),
            size_hint_y=None
        )
        content.bind(minimum_height=content.setter("height"))

        # === Title ===
        content.add_widget(MDLabel(
            text="Settings",
            halign="center",
            font_style="H5",
            size_hint_y=None,
            height=dp(50)
        ))

        # === Toggle Row Helper ===
        def toggle_row(text, on_toggle=None):
            row = MDBoxLayout(
                orientation="horizontal",
                spacing=dp(10),
                size_hint_y=None,
                height=dp(40)
            )
            label = MDLabel(
                text=text,
                halign="left",
                valign="middle",
                font_style="Body1",
                size_hint_x=0.85
            )
            switch = MDSwitch(pos_hint={"center_y": 0.5})
            if on_toggle:
                switch.bind(active=on_toggle)
            row.add_widget(label)
            row.add_widget(switch)
            return row

        # === Reminder Notifications Card ===
        reminder_card = MDCard(
            orientation="vertical",
            padding=dp(20),
            spacing=dp(15),
            radius=[dp(15)],
            elevation=3,
            size_hint_y=None
        )
        reminder_card.add_widget(MDLabel(
            text="🕐 Reminder Notifications",
            font_style="H6",
            bold=True,
            theme_text_color="Custom",
            text_color=(0.2, 0.3, 0.4, 1)
        ))
        reminder_card.add_widget(toggle_row("Sound", self.toggle_sound))
        reminder_card.add_widget(toggle_row("Vibration", self.toggle_vibration))
        reminder_card.add_widget(MDLabel(
            text="Reminder Time: Select Time (Coming Soon)",
            theme_text_color="Secondary",
            font_style="Caption",
            size_hint_y=None,
            height=dp(20)
        ))

        content.add_widget(reminder_card)
        content.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # === Back Button ===
        back_btn = MDRaisedButton(
            text="Back",
            size_hint=(None, None),
            height=dp(50),
            width=dp(100),
            pos_hint={"center_x": 0.5},
            md_bg_color=(0.2, 0.6, 0.7, 1)
        )
        back_btn.bind(on_release=self.go_back)
        content.add_widget(back_btn)

        scroll.add_widget(content)
        self.add_widget(scroll)

    def toggle_sound(self, instance, value):
        print("🔊 Sound Enabled:", value)

    def toggle_vibration(self, instance, value):
        print("📳 Vibration Enabled:", value)

    def go_back(self, instance=None):
        if hasattr(self.manager.parent, "go_back"):
            self.manager.parent.go_back()
