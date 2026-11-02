"""
Main Application Window for PDF Unlocker Desktop Windows.
Implements the 4-zone layout (TopBar 84px, Sidebar 268px, Central Workspace, Footer 40px),
1536x1024 reference dimensions (min 1120x760), Section 19 responsive resize rules,
and offline cryptographic license state synchronization.
"""

import customtkinter as ctk
from ui.theme import (
    COLOR_BG_ROOT, WINDOW_INITIAL_WIDTH, WINDOW_INITIAL_HEIGHT,
    WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT, get_resource_path
)
from ui.components.topbar import TopBar
from ui.components.sidebar import Sidebar
from ui.components.footer import Footer
from ui.views.home_view import HomeView
from ui.views.search_view import SearchView
from ui.views.recovery_view import RecoveryView
from ui.views.batch_view import BatchView
from ui.views.history_view import HistoryView
from ui.views.settings_view import SettingsView
from ui.views.about_view import AboutView
from core.engine import CrackerEngine
from core.history_manager import HistoryManager
from core.settings_manager import SettingsManager
from core.license_manager import LicenseManager


class PDFUnlockerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PDF Unlocker Desktop")
        self.minsize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
        self._set_initial_geometry(WINDOW_INITIAL_WIDTH, WINDOW_INITIAL_HEIGHT)

        icon_path = get_resource_path("assets/app_icon.ico")
        if icon_path.exists():
            try:
                self.iconbitmap(str(icon_path))
            except Exception:
                pass

        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLOR_BG_ROOT)

        self.engine = CrackerEngine()
        self.history = HistoryManager()
        self.settings = SettingsManager()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._last_size = (0, 0)

        self._build_ui()
        self.refresh_license_state()
        self.bind("<Configure>", self._on_window_configure)

    def _set_initial_geometry(self, width: int, height: int):
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = max(0, (screen_w - width) // 2)
        y = max(0, (screen_h - height) // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=0)    # 1. Barre supérieure (84 px)
        self.grid_rowconfigure(1, weight=1)    # 2 & 3. Menu latéral + Zone de travail
        self.grid_rowconfigure(2, weight=0)    # 4. Barre inférieure (40 px)
        self.grid_columnconfigure(0, weight=0) # Menu latéral (268 px)
        self.grid_columnconfigure(1, weight=1) # Zone centrale de travail

        # Zone 1: Barre supérieure
        self.topbar = TopBar(
            self,
            on_open_settings=lambda: self.navigate_to("Paramètres")
        )
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Zone 2: Menu latéral
        self.sidebar = Sidebar(
            self,
            on_tab_selected=self.switch_tab,
            on_discover_premium=lambda: self.navigate_to("Paramètres")
        )
        self.sidebar.grid(row=1, column=0, sticky="nsew")

        # Zone 3: Zone centrale de travail
        self.content_container = ctk.CTkFrame(self, fg_color=COLOR_BG_ROOT, corner_radius=0)
        self.content_container.grid(row=1, column=1, sticky="nsew")
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Initialize all 7 views once
        self.home_view = HomeView(self.content_container, self.engine, self.history, self.settings)
        self.views = {
            "Accueil": self.home_view,
            "Déverrouiller": SearchView(self.content_container),
            "Récupération": RecoveryView(self.content_container, on_launch_method=self._on_launch_from_recovery),
            "Traitement par lots": BatchView(self.content_container, self.engine),
            "Historique": HistoryView(self.content_container, self.history),
            "Paramètres": SettingsView(
                self.content_container,
                self.settings,
                on_license_changed=self.refresh_license_state
            ),
            "Aide": AboutView(self.content_container),
        }

        self.current_view_name = "Accueil"
        self.views["Accueil"].grid(row=0, column=0, sticky="nsew")

        # Zone 4: Barre inférieure
        self.footer = Footer(self)
        self.footer.grid(row=2, column=0, columnspan=2, sticky="ew")

    def refresh_license_state(self):
        st = LicenseManager.get_license_status(self.settings)
        self.sidebar.update_license_badge(bool(st["is_pro"]), str(st["tier"]))

    def _on_launch_from_recovery(self, method_id: str, preset_val: str):
        self.home_view.configure_and_run_from_recovery_page(method_id, preset_val, auto_start=False)
        self.navigate_to("Accueil")

    def navigate_to(self, tab_name: str):
        self.sidebar.select_tab(tab_name, notify=True)

    def switch_tab(self, tab_name: str):
        if tab_name == self.current_view_name:
            return
        if self.current_view_name in self.views:
            self.views[self.current_view_name].grid_forget()
        if tab_name in self.views:
            target = self.views[tab_name]
            if tab_name == "Historique":
                target.refresh_list()
            target.grid(row=0, column=0, sticky="nsew")
            self.current_view_name = tab_name

    def _on_window_configure(self, event=None):
        if event and event.widget is self:
            w, h = event.width, event.height
            if abs(w - self._last_size[0]) >= 12 or abs(h - self._last_size[1]) >= 12:
                self._last_size = (w, h)
                self.topbar.set_compact_mode(w < 1180)
                self.sidebar.apply_responsive_dimensions(w, h)
                self.home_view.apply_responsive_layout(w, h)
                self.footer.set_compact_mode(w < 1200)

    def _on_close(self):
        if self.engine.is_running:
            self.engine.stop()
        self.destroy()
