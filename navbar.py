# # navbar.py
# from kivymd.uix.bottomnavigation import MDBottomNavigation, MDBottomNavigationItem
# from kivy.clock import Clock


# class BottomNavBar(MDBottomNavigation):
#     def __init__(self, screen_manager_callback, active_screen="dashboard", **kwargs):
#         """
#         screen_manager_callback: dict of navigation functions
#         active_screen: str - which tab is currently active
#         """
#         super().__init__(**kwargs)
#         self.panel_color = "#FFFFFF"
#         self.text_color_active = "#00796B"   # Teal active
#         self.text_color_normal = "#757575"   # Gray normal
#         self.selected_color_background = "#E0F2F1"
#         self.active_screen = active_screen
#         self.callbacks = screen_manager_callback

#         # === Create Tabs ===
#         self.home_tab = MDBottomNavigationItem(
#             name="dashboard",
#             text="Home",
#             icon="home-outline",
#             on_tab_press=lambda *a: self._switch("dashboard", "dashboard"),
#         )
#         self.add_widget(self.home_tab)

#         self.view_tab = MDBottomNavigationItem(
#             name="view_reminders",
#             text="View",
#             icon="view-list-outline",
#             on_tab_press=lambda *a: self._switch("view_reminders", "view_reminders"),
#         )
#         self.add_widget(self.view_tab)

#         self.add_tab = MDBottomNavigationItem(
#             name="add_reminder",
#             text="Add",
#             icon="plus-circle-outline",
#             on_tab_press=lambda *a: self._switch("add_reminder", "add_reminder"),
#         )
#         self.add_widget(self.add_tab)

#         self.tracker_tab = MDBottomNavigationItem(
#             name="tracker",
#             text="Tracker",
#             icon="chart-line",
#             on_tab_press=lambda *a: self._switch("tracker", "tracker"),
#         )
#         self.add_widget(self.tracker_tab)

#         self.settings_tab = MDBottomNavigationItem(
#             name="settings",
#             text="Settings",
#             icon="cog-outline",
#             on_tab_press=lambda *a: self._switch("settings", "settings"),
#         )
#         self.add_widget(self.settings_tab)

#         # ✅ Set the initial active tab
#         self.current = active_screen

#     # === Custom Switch Handler (fixed highlight bug) ===
#     def _switch(self, screen_name, callback_key):
#         """
#         Safely switch screens and keep navbar highlight correct.
#         We delay the callback slightly so the visual update happens first.
#         """
#         if self.current != screen_name:
#             self.current = screen_name  # visually update tab highlight

#         callback = self.callbacks.get(callback_key)
#         if callback:
#             # Delay screen switch for smoother highlight sync
#             Clock.schedule_once(lambda dt: callback(), 0.05)
