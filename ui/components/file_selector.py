"""
File selector component for PDF Unlocker Desktop Windows (Section 8 of Master Prompt).
Displays non-editable path field with smart middle truncation + full path tooltip,
native Windows PDF file dialog button, and real validation state.
"""

import customtkinter as ctk
from tkinter import filedialog
from pathlib import Path
from ui.theme import (
    COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_PRIMARY_BLUE, COLOR_PRIMARY_HOVER,
    COLOR_TEXT_WHITE, COLOR_TEXT_MUTED, COLOR_INPUT_BG, COLOR_SUCCESS_TEXT,
    COLOR_ERROR_RED, COLOR_WARNING_AMBER, FONT_FAMILY, RADIUS_INPUT
)
from ui.icons import get_icon
from core.engine import CrackerEngine


class FileSelector(ctk.CTkFrame):
    def __init__(self, master, on_file_changed=None, default_file="", **kwargs):
        super().__init__(
            master,
            fg_color=COLOR_CARD_BG,
            corner_radius=13,
            border_width=1,
            border_color=COLOR_CARD_BORDER,
            **kwargs
        )
        self.on_file_changed = on_file_changed
        self.selected_path = ""
        self.last_inspection = None
        self._tooltip_win = None
        self._build_ui()

        if default_file and Path(default_file).exists():
            self.set_file(str(Path(default_file).resolve()))

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)

        # 8.1 Header (Icône document + Titre "Fichier PDF")
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=22, pady=(18, 12))

        self.doc_icon = get_icon("file_doc", 18, "#23B5FF")
        icon_lbl = ctk.CTkLabel(self.header_frame, image=self.doc_icon, text="")
        icon_lbl.grid(row=0, column=0, padx=(0, 10))

        title_lbl = ctk.CTkLabel(
            self.header_frame,
            text="Fichier PDF",
            font=(FONT_FAMILY, 15, "bold"),
            text_color=COLOR_TEXT_WHITE
        )
        title_lbl.grid(row=0, column=1, sticky="w")

        # 8.2 & 8.3 Input Row (Read-only path field + "Choisir un fichier" button)
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.grid(row=1, column=0, sticky="ew", padx=22, pady=(0, 10))
        self.input_frame.grid_columnconfigure(0, weight=1)
        self.input_frame.grid_columnconfigure(1, weight=0)

        self.path_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="Sélectionnez un fichier PDF protégé sur votre ordinateur...",
            fg_color=COLOR_INPUT_BG,
            border_color=COLOR_CARD_BORDER,
            text_color=COLOR_TEXT_WHITE,
            font=(FONT_FAMILY, 13),
            height=45,
            corner_radius=RADIUS_INPUT
        )
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 12))
        self.path_entry.configure(state="readonly")
        self.path_entry.bind("<Enter>", self._show_full_path_tooltip)
        self.path_entry.bind("<Leave>", self._hide_full_path_tooltip)

        self.folder_icon = get_icon("folder", 17, "#FFFFFF")
        self.browse_btn = ctk.CTkButton(
            self.input_frame,
            text="  Choisir un fichier",
            image=self.folder_icon,
            compound="left",
            font=(FONT_FAMILY, 13, "bold"),
            fg_color=COLOR_PRIMARY_BLUE,
            hover_color=COLOR_PRIMARY_HOVER,
            text_color="#FFFFFF",
            height=45,
            width=175,
            corner_radius=9,
            command=self._browse_file
        )
        self.browse_btn.grid(row=0, column=1, sticky="e")

        # 8.4 File status row
        self.status_row = ctk.CTkFrame(self, fg_color="transparent")
        self.status_row.grid(row=2, column=0, sticky="ew", padx=22, pady=(0, 18))
        self.status_row.grid_columnconfigure(1, weight=1)

        self.icon_info = get_icon("info_circle", 16, COLOR_TEXT_MUTED)
        self.icon_ok = get_icon("check_circle", 16, COLOR_SUCCESS_TEXT)
        self.icon_err = get_icon("error_circle", 16, COLOR_ERROR_RED)
        self.icon_warn = get_icon("info_circle", 16, COLOR_WARNING_AMBER)

        self.status_icon_lbl = ctk.CTkLabel(self.status_row, image=self.icon_info, text="")
        self.status_icon_lbl.grid(row=0, column=0, padx=(0, 8), sticky="w")

        self.status_lbl = ctk.CTkLabel(
            self.status_row,
            text="Aucun fichier sélectionné — Cliquez sur « Choisir un fichier » pour charger un PDF.",
            font=(FONT_FAMILY, 12),
            text_color=COLOR_TEXT_MUTED,
            anchor="w",
            justify="left"
        )
        self.status_lbl.grid(row=0, column=1, sticky="ew")

    def _format_display_path(self, full_path: str, max_chars: int = 62) -> str:
        if len(full_path) <= max_chars:
            return full_path
        p = Path(full_path)
        name = p.name
        prefix_len = max(14, max_chars - len(name) - 5)
        return f"{full_path[:prefix_len]}...\\{name}"

    def _show_full_path_tooltip(self, event=None):
        if not self.selected_path or len(self.selected_path) <= 55:
            return
        self._hide_full_path_tooltip()
        try:
            self._tooltip_win = tw = ctk.CTkToplevel(self)
            tw.wm_overrideredirect(True)
            x = self.path_entry.winfo_rootx() + 10
            y = self.path_entry.winfo_rooty() + self.path_entry.winfo_height() + 4
            tw.wm_geometry(f"+{x}+{y}")
            lbl = ctk.CTkLabel(
                tw,
                text=self.selected_path,
                font=(FONT_FAMILY, 11),
                fg_color="#081427",
                text_color=COLOR_TEXT_WHITE,
                corner_radius=6,
                padx=10,
                pady=5
            )
            lbl.pack()
        except Exception:
            self._tooltip_win = None

    def _hide_full_path_tooltip(self, event=None):
        if self._tooltip_win is not None:
            try:
                self._tooltip_win.destroy()
            except Exception:
                pass
            self._tooltip_win = None

    def _browse_file(self):
        filename = filedialog.askopenfilename(
            title="Sélectionner un fichier PDF",
            filetypes=[("Fichiers PDF (*.pdf)", "*.pdf"), ("Tous les fichiers", "*.*")]
        )
        if filename:
            self.set_file(filename)

    def set_file(self, filepath: str, notify: bool = True):
        self.selected_path = filepath.strip() if filepath else ""

        self.path_entry.configure(state="normal")
        self.path_entry.delete(0, "end")
        if self.selected_path:
            self.path_entry.insert(0, self._format_display_path(self.selected_path))
        self.path_entry.configure(state="readonly")

        if not self.selected_path:
            self.last_inspection = None
            self.status_icon_lbl.configure(image=self.icon_info)
            self.status_lbl.configure(
                text="Aucun fichier sélectionné — Cliquez sur « Choisir un fichier » pour charger un PDF.",
                text_color=COLOR_TEXT_MUTED
            )
            return

        info = CrackerEngine.inspect_pdf_detailed(self.selected_path)
        self.last_inspection = info
        status = info.get("status")
        size_str = info.get("size_str", "").replace(".", ",")
        fname = Path(self.selected_path).name

        if status == "user_password_required":
            self.status_icon_lbl.configure(image=self.icon_ok)
            self.status_lbl.configure(
                text=f"Fichier sélectionné : {fname} ({size_str}) — Protégé par mot de passe",
                text_color=COLOR_SUCCESS_TEXT
            )
        elif status == "permissions_only":
            self.status_icon_lbl.configure(image=self.icon_warn)
            self.status_lbl.configure(
                text=f"Fichier sélectionné : {fname} ({size_str}) — Restrictions d'édition uniquement",
                text_color=COLOR_WARNING_AMBER
            )
        elif status == "unencrypted":
            self.status_icon_lbl.configure(image=self.icon_ok)
            self.status_lbl.configure(
                text=f"Fichier sélectionné : {fname} ({size_str}) — Aucun mot de passe requis",
                text_color=COLOR_SUCCESS_TEXT
            )
        else:
            self.status_icon_lbl.configure(image=self.icon_err)
            self.status_lbl.configure(
                text=info.get("message", "Fichier invalide ou inaccessible."),
                text_color=COLOR_ERROR_RED
            )

        if notify and self.on_file_changed:
            self.on_file_changed(self.selected_path)

    def get_file(self) -> str:
        return self.selected_path

    def set_compact_vertical(self, compact: bool):
        self.header_frame.grid_configure(pady=(10, 6) if compact else (18, 12))
        self.input_frame.grid_configure(pady=(0, 6) if compact else (0, 10))
        self.status_row.grid_configure(pady=(0, 10) if compact else (0, 18))
        h = 36 if compact else 45
        self.path_entry.configure(height=h)
        self.browse_btn.configure(height=h)
