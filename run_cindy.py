#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Project Cindy - Direct Launcher
Quick launcher without splash screen
"""

import tkinter as tk
import cindy_ui

def main():
    """Launch Project Cindy bot directly"""
    root = tk.Tk()
    app = cindy_ui.BotUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
