"""
Progress Card component for PDF Unlocker Desktop Windows (Section 11 of Master Prompt).
Left: Circular progress indicator (108 px, #142A4A / #1687F8).
Right: Real status title, horizontal bar (height 11 px, #1A3155 / #1687F8),
and aligned real statistics (Essais effectués, Temps écoulé, Vitesse, Temps restant estimé).
"""

import customtkinter as ctk
from ui.theme import (
    COLOR_CARD_BG, COLOR_CARD_BORDER, COLOR_TEXT_WHITE, COLOR_TEXT_MUTED,
    COLOR_PRIMARY_BLUE, COLOR_PROGRESS_TRACK, FONT_FAMILY, FONT_MONO
)
from ui.components.circular_progress import CircularProgress


class ProgressCard(ctk.CTkFrame):
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
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Left: Circular progress (108 px diameter)
        self.circular_progress = CircularProgress(
            self,
            size=108,
            ring_width=9,
            bg_color=COLOR_CARD_BG
        )
        self.circular_progress.grid(row=0, column=0, padx=(22, 18), pady=18, sticky="w")

        # Right: Status, horizontal progress bar, and statistics grid
        self.right_box = ctk.CTkFrame(self, fg_color="transparent")
        self.right_box.grid(row=0, column=1, padx=(0, 22), pady=18, sticky="nsew")
        self.right_box.grid_columnconfigure(0, weight=1)

        # 11.5 Status text (default: "En attente d'une opération")
        self.status_title = ctk.CTkLabel(
            self.right_box,
            text="En attente d'une opération",
            font=(FONT_FAMILY, 14, "bold"),
            text_color=COLOR_TEXT_WHITE,
            anchor="w"
        )
        self.status_title.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # 11.3 Horizontal progress bar (height 11 px, track #1A3155, progress #1687F8, radius 6 px)
        self.progress_bar = ctk.CTkProgressBar(
            self.right_box,
            fg_color=COLOR_PROGRESS_TRACK,
            progress_color=COLOR_PRIMARY_BLUE,
            height=11,
            corner_radius=6
        )
        self.progress_bar.set(0.0)
        self.progress_bar.grid(row=1, column=0, sticky="ew", pady=(0, 14))

        # 11.4 Statistics Grid (4 aligned columns)
        self.metrics_grid = ctk.CTkFrame(self.right_box, fg_color="transparent")
        self.metrics_grid.grid(row=2, column=0, sticky="ew")
        for c in range(4):
            self.metrics_grid.grid_columnconfigure(c, weight=1)

        # Stat 1: Essais effectués
        self.attempts_lbl = self._create_stat_column(self.metrics_grid, 0, "Essais effectués", "0")
        # Stat 2: Temps écoulé
        self.elapsed_lbl = self._create_stat_column(self.metrics_grid, 1, "Temps écoulé", "00:00:00")
        # Stat 3: Vitesse
        self.speed_lbl = self._create_stat_column(self.metrics_grid, 2, "Vitesse", "0 essais/s")
        # Stat 4: Temps restant estimé
        self.eta_lbl = self._create_stat_column(self.metrics_grid, 3, "Temps restant", "--:--:--")

    def set_compact_vertical(self, compact: bool):
        py = 10 if compact else 18
        self.circular_progress.set_size(84 if compact else 108)
        self.circular_progress.grid_configure(pady=py, padx=(16, 14) if compact else (22, 18))
        self.right_box.grid_configure(pady=py)
        self.progress_bar.grid_configure(pady=(0, 8 if compact else 14))

    def _create_stat_column(self, parent, col: int, label_text: str, initial_value: str) -> ctk.CTkLabel:
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=0, column=col, sticky="w", padx=(0, 10))

        ctk.CTkLabel(
            box,
            text=label_text,
            font=(FONT_FAMILY, 11),
            text_color=COLOR_TEXT_MUTED,
            anchor="w"
        ).grid(row=0, column=0, sticky="w")

        val_lbl = ctk.CTkLabel(
            box,
            text=initial_value,
            font=(FONT_MONO, 13, "bold"),
            text_color=COLOR_TEXT_WHITE,
            anchor="w"
        )
        val_lbl.grid(row=1, column=0, sticky="w", pady=(2, 0))
        return val_lbl

    @staticmethod
    def _format_hms(sec: float) -> str:
        s = max(0, int(sec))
        hours = s // 3600
        minutes = (s % 3600) // 60
        seconds = s % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def update_metrics(self, current: int, total: int, elapsed_sec: float, speed_val: float):
        if total <= 0:
            self.circular_progress.set_progress(0.0, indeterminate=True)
            self.progress_bar.set(0.0)
        else:
            fraction = min(1.0, max(0.0, current / float(total)))
            self.circular_progress.set_progress(fraction * 100.0, indeterminate=False)
            self.progress_bar.set(fraction)

        self.attempts_lbl.configure(text=f"{current:,}".replace(",", " "))
        self.elapsed_lbl.configure(text=self._format_hms(elapsed_sec))
        self.speed_lbl.configure(text=f"{int(round(speed_val)):,} essais/s".replace(",", " "))

        if speed_val > 0.5 and total > current:
            rem_sec = (total - current) / speed_val
            self.eta_lbl.configure(text=self._format_hms(rem_sec))
        elif total > 0 and current >= total:
            self.eta_lbl.configure(text="00:00:00")
        else:
            self.eta_lbl.configure(text="--:--:--")

    def set_status_text(self, text: str):
        self.status_title.configure(text=text)

    def reset(self):
        self.circular_progress.set_progress(0.0, indeterminate=False)
        self.progress_bar.set(0.0)
        self.attempts_lbl.configure(text="0")
        self.elapsed_lbl.configure(text="00:00:00")
        self.speed_lbl.configure(text="0 essais/s")
        self.eta_lbl.configure(text="--:--:--")
        self.status_title.configure(text="En attente d'une opération")
