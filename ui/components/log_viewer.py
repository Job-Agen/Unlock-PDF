"""
Operation Log Viewer component for PDF Unlocker Desktop Windows (Section 12 of Master Prompt).
Displays timestamped real events with semantic colors (#9BB9E3, #23B5FF, #16D18C, #FF5368, #F6B94A),
smart auto-scroll, and a button to clear visual logs without touching persistent history.
"""

import customtkinter as ctk
from datetime import datetime
from ui.theme import (
    COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_TEXT_DIM, COLOR_INPUT_BG, COLOR_CYAN, COLOR_SUCCESS_TEXT,
    COLOR_ERROR_RED, COLOR_WARNING_AMBER, COLOR_SECONDARY_BTN, COLOR_SECONDARY_HOVER,
    FONT_FAMILY, FONT_MONO
)
from ui.icons import get_icon


class LogViewer(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            **kwargs
        )
        self._build_ui()

    def _build_ui(self):
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # 12.1 Header (Icône + "Journal des opérations" + Bouton Effacer)
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=(16, 10))
        header_frame.grid_columnconfigure(1, weight=1)

        self.list_icon = get_icon("log_list", 18, COLOR_CYAN)
        icon_lbl = ctk.CTkLabel(header_frame, image=self.list_icon, text="")
        icon_lbl.grid(row=0, column=0, padx=(0, 10))

        title_lbl = ctk.CTkLabel(
            header_frame,
            text="Journal des opérations",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE,
            anchor="w"
        )
        title_lbl.grid(row=0, column=1, sticky="w")

        self.clear_btn = ctk.CTkButton(
            header_frame,
            text="Effacer",
            font=(FONT_FAMILY, 11),
            fg_color=COLOR_SECONDARY_BTN,
            hover_color=COLOR_SECONDARY_HOVER,
            text_color=COLOR_TEXT_MUTED,
            height=26,
            width=68,
            corner_radius=6,
            command=self.clear
        )
        self.clear_btn.grid(row=0, column=2, sticky="e")

        # 12.2 Textbox for logs
        self.textbox = ctk.CTkTextbox(
            self,
            fg_color=COLOR_INPUT_BG,
            text_color=COLOR_TEXT_MUTED,
            font=(FONT_MONO, 12),
            corner_radius=9,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            wrap="word"
        )
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 18))

        # 12.3 Semantic colors
        tb = self.textbox._textbox
        tb.tag_config("time", foreground=COLOR_TEXT_DIM)
        tb.tag_config("info", foreground=COLOR_TEXT_MUTED)
        tb.tag_config("action", foreground=COLOR_CYAN)
        tb.tag_config("success", foreground=COLOR_SUCCESS_TEXT)
        tb.tag_config("error", foreground=COLOR_ERROR_RED)
        tb.tag_config("warning", foreground=COLOR_WARNING_AMBER)
        tb.tag_config("msg_white", foreground=COLOR_TEXT_WHITE)

        self.add_log("ℹ", "Application initialisée — En attente d'un fichier PDF.")

    def add_log(self, symbol: str, message: str, timestamp_str: str = None):
        """Adds a timestamped log line with smart auto-scroll (Section 12.4)."""
        if timestamp_str is None:
            timestamp_str = datetime.now().strftime("%H:%M:%S")

        tb = self.textbox._textbox
        # Check if scrollbar is currently near the bottom before inserting
        try:
            _, y_bottom = tb.yview()
            at_bottom = y_bottom >= 0.92
        except Exception:
            at_bottom = True

        tb.configure(state="normal")
        tb.insert("end", f"{timestamp_str}   ", "time")

        if symbol == "✓":
            tb.insert("end", "✓   ", "success")
            tb.insert("end", f"{message}\n", "success")
        elif symbol in ("✕", "✗"):
            tb.insert("end", "✕   ", "error")
            tb.insert("end", f"{message}\n", "error")
        elif symbol in ("⌛", "⚠"):
            tb.insert("end", f"{symbol}   ", "warning")
            tb.insert("end", f"{message}\n", "warning")
        elif symbol == "→":
            tb.insert("end", "→   ", "action")
            tb.insert("end", f"{message}\n", "msg_white")
        else:
            tb.insert("end", "ℹ   ", "info")
            tb.insert("end", f"{message}\n", "info")

        if at_bottom:
            self.textbox.see("end")
        tb.configure(state="disabled")

    def clear(self):
        tb = self.textbox._textbox
        tb.configure(state="normal")
        tb.delete("1.0", "end")
        tb.configure(state="disabled")
