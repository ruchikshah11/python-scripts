"""
SYNOPSIS
    An interactive Tkinter viewer for every pattern in the Patterns folder -
    pick a pattern from the dropdown, drag the --rows/--size slider, and
    see it update live. Reuses each pattern's actual print_xxx() function
    directly (via stdout capture), rather than reimplementing any pattern's
    logic here.

DESCRIPTION
    CharacterPattern is handled specially since it takes a character plus a
    size, and its function returns lines directly instead of printing them.

EXAMPLE
    python pattern_visualizer.py

NOTES
    Created by  : Ruchik Shah
    Created on  : 2026-08-01
    Modified by :
    Modified on :
    Version     : 1.0.0
"""

import contextlib
import importlib
import io
import sys
import tkinter as tk
from pathlib import Path
from tkinter import ttk

PYTHON_ROOT = Path(__file__).resolve().parent.parent.parent
PATTERNS_ROOT = PYTHON_ROOT / "Patterns"

# (display name, folder name, module name, function name)
PATTERN_REGISTRY = [
    ("Square", "Square", "square", "print_square"),
    ("Left Triangle", "LeftTriangle", "left_triangle", "print_left_triangle"),
    ("Right-Aligned Triangle", "RightAlignedTriangle", "right_aligned_triangle", "print_right_aligned_triangle"),
    ("Inverted Triangle", "InvertedTriangle", "inverted_triangle", "print_inverted_triangle"),
    ("Hollow Triangle", "HollowTriangle", "hollow_triangle", "print_hollow_triangle"),
    ("Rhombus", "Rhombus", "rhombus", "print_rhombus"),
    ("Pyramid", "Pyramid", "pyramid", "print_pyramid"),
    ("Inverted Pyramid", "InvertedPyramid", "inverted_pyramid", "print_inverted_pyramid"),
    ("Hollow Pyramid", "HollowPyramid", "hollow_pyramid", "print_hollow_pyramid"),
    ("Diamond", "Diamond", "diamond", "print_diamond"),
    ("Hollow Diamond", "HollowDiamond", "hollow_diamond", "print_hollow_diamond"),
    ("Hourglass", "Hourglass", "hourglass", "print_hourglass"),
    ("Butterfly", "ButterflyPattern", "butterfly_pattern", "print_butterfly"),
    ("Hollow Square", "HollowSquare", "hollow_square", "print_hollow_square"),
    ("Checkerboard", "Checkerboard", "checkerboard", "print_checkerboard"),
    ("Plus (+)", "PlusPattern", "plus_pattern", "print_plus"),
    ("Cross (X)", "CrossPattern", "cross_pattern", "print_cross"),
    ("Alphabet Triangle", "AlphabetTriangle", "alphabet_triangle", "print_alphabet_triangle"),
    ("Number Triangle", "NumberTriangle", "number_triangle", "print_number_triangle"),
    ("Number Pyramid", "NumberPyramid", "number_pyramid", "print_number_pyramid"),
    ("Floyd's Triangle", "FloydsTriangle", "floyds_triangle", "print_floyds_triangle"),
    ("Pascal's Triangle", "PascalsTriangle", "pascals_triangle", "print_pascals_triangle"),
    ("Palindromic Pattern", "PalindromicPattern", "palindromic_pattern", "print_palindromic_pattern"),
    ("Spiral Matrix", "SpiralMatrix", "spiral_matrix", "print_spiral_matrix"),
    ("Heart", "HeartPattern", "heart_pattern", "print_heart"),
]

CHARACTER_PATTERN_LABEL = "Character (any letter/digit)"


def load_pattern_modules():
    """Imports every pattern module (each folder added to sys.path), and
    returns {display_name: function} plus the CharacterPattern renderer."""
    functions = {}
    for display_name, folder_name, module_name, function_name in PATTERN_REGISTRY:
        sys.path.insert(0, str(PATTERNS_ROOT / folder_name))
        module = importlib.import_module(module_name)
        functions[display_name] = getattr(module, function_name)

    sys.path.insert(0, str(PATTERNS_ROOT / "CharacterPattern"))
    character_module = importlib.import_module("character_pattern")
    return functions, character_module.render_character_grid


class PatternVisualizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pattern Visualizer")
        self.root.geometry("700x650")

        self.pattern_functions, self.render_character_grid = load_pattern_modules()
        pattern_names = [name for name, *_ in PATTERN_REGISTRY] + [CHARACTER_PATTERN_LABEL]

        # --- Controls ---
        controls = ttk.Frame(root)
        controls.pack(fill="x", padx=10, pady=10)

        ttk.Label(controls, text="Pattern:").grid(row=0, column=0, sticky="w")
        self.pattern_combo = ttk.Combobox(controls, values=pattern_names, state="readonly", width=30)
        self.pattern_combo.set("Square")
        self.pattern_combo.grid(row=0, column=1, padx=8, sticky="w")
        self.pattern_combo.bind("<<ComboboxSelected>>", self._on_pattern_or_size_change)

        ttk.Label(controls, text="Rows / Size:").grid(row=1, column=0, sticky="w", pady=(8, 0))
        self.size_value = tk.IntVar(value=5)
        self.size_slider = ttk.Scale(controls, from_=1, to=20, orient="horizontal",
                                      variable=self.size_value, command=self._on_slider_move)
        self.size_slider.grid(row=1, column=1, sticky="ew", padx=8, pady=(8, 0))
        self.size_label = ttk.Label(controls, text="5")
        self.size_label.grid(row=1, column=2, padx=4, pady=(8, 0))

        self.char_row_label = ttk.Label(controls, text="Character:")
        self.char_entry = ttk.Entry(controls, width=5)
        self.char_entry.insert(0, "R")
        self.char_entry.bind("<KeyRelease>", self._on_pattern_or_size_change)
        # gridded/ungridded dynamically depending on whether CharacterPattern is selected

        controls.columnconfigure(1, weight=1)

        # --- Preview ---
        preview_frame = ttk.LabelFrame(root, text="Preview")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.preview_text = tk.Text(preview_frame, font=("Consolas", 11), wrap="none")
        self.preview_text.pack(fill="both", expand=True, padx=8, pady=8)

        self._update_char_field_visibility()
        self._render_current_pattern()

    def _on_pattern_or_size_change(self, _event=None):
        self._update_char_field_visibility()
        self._render_current_pattern()

    def _on_slider_move(self, _value):
        self.size_label.configure(text=str(self.size_value.get()))
        self._render_current_pattern()

    def _update_char_field_visibility(self):
        if self.pattern_combo.get() == CHARACTER_PATTERN_LABEL:
            self.char_row_label.grid(row=2, column=0, sticky="w", pady=(8, 0))
            self.char_entry.grid(row=2, column=1, sticky="w", padx=8, pady=(8, 0))
        else:
            self.char_row_label.grid_forget()
            self.char_entry.grid_forget()

    def _render_current_pattern(self):
        pattern_name = self.pattern_combo.get()
        size = self.size_value.get()

        try:
            if pattern_name == CHARACTER_PATTERN_LABEL:
                char = self.char_entry.get()
                if len(char) != 1:
                    output = "(enter exactly one character)"
                else:
                    lines = self.render_character_grid(char, size)
                    output = "\n".join(lines)
            else:
                function = self.pattern_functions[pattern_name]
                buffer = io.StringIO()
                with contextlib.redirect_stdout(buffer):
                    function(size)
                output = buffer.getvalue()
        except Exception as ex:
            output = f"Error: {ex}"

        self.preview_text.delete("1.0", "end")
        self.preview_text.insert("1.0", output)


def main():
    root = tk.Tk()
    PatternVisualizerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
