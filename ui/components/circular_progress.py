"""
Circular Progress indicator widget (Section 11.2 of Master Prompt).
Diameter: 108 px, Track: #142A4A, Progress: #1687F8, Center text: 22 px bold #F3F7FF.
"""

import tkinter as tk
from ui.theme import (
    COLOR_CARD_BG, COLOR_PROGRESS_CIRCLE_BG, COLOR_PRIMARY_BLUE,
    COLOR_TEXT_WHITE, FONT_FAMILY
)


class CircularProgress(tk.Canvas):
    def __init__(
        self,
        master,
        size=108,
        ring_width=9,
        bg_color=COLOR_CARD_BG,
        ring_color=COLOR_PROGRESS_CIRCLE_BG,
        progress_color=COLOR_PRIMARY_BLUE,
        **kwargs
    ):
        super().__init__(master, width=size, height=size, bg=bg_color, highlightthickness=0, **kwargs)
        self.size = size
        self.ring_width = ring_width
        self.bg_color = bg_color
        self.ring_color = ring_color
        self.progress_color = progress_color
        self.percentage = 0.0
        self.indeterminate = False
        self.draw()

    def set_progress(self, percent: float, indeterminate: bool = False):
        self.indeterminate = indeterminate
        self.percentage = max(0.0, min(100.0, percent))
        self.draw()

    def set_size(self, new_size: int):
        if self.size != new_size:
            self.size = new_size
            self.configure(width=new_size, height=new_size)
            self.draw()

    def draw(self):
        self.delete("all")
        pad = self.ring_width + 4
        x0, y0 = pad, pad
        x1, y1 = self.size - pad, self.size - pad

        # Track circle (#142A4A)
        self.create_oval(
            x0, y0, x1, y1,
            outline=self.ring_color,
            width=self.ring_width
        )

        # Progress arc (#1687F8)
        if self.indeterminate:
            self.create_arc(
                x0, y0, x1, y1,
                start=45,
                extent=-90,
                style="arc",
                outline=self.progress_color,
                width=self.ring_width
            )
            display_text = "..."
        else:
            if self.percentage > 0.1:
                extent = -(self.percentage / 100.0) * 360.0
                self.create_arc(
                    x0, y0, x1, y1,
                    start=90,
                    extent=extent,
                    style="arc",
                    outline=self.progress_color,
                    width=self.ring_width
                )
            display_text = f"{int(round(self.percentage))}%"

        self.create_text(
            self.size / 2,
            self.size / 2,
            text=display_text,
            fill=COLOR_TEXT_WHITE,
            font=(FONT_FAMILY, 22, "bold")
        )
