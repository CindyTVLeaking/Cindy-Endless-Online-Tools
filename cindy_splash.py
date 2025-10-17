#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Project Cindy - Splash Screen
Shows Cindy's image for 5 seconds before launching the bot
"""

import tkinter as tk
from tkinter import messagebox
import os
import pathlib
import threading
import time

class CindySplashScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Project Cindy")
        self.root.configure(bg='#1e1e1e')
        self.root.overrideredirect(True)  # Remove window decorations
        
        # Track if we're still animating
        self.is_animating = True
        self.animation_id = None
        self.is_destroyed = False  # NEW: Track if window is destroyed
        
        # Get screen dimensions
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Set window size
        window_width = 600
        window_height = 700
        
        # Center the window
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.root.geometry(f'{window_width}x{window_height}+{x}+{y}')
        
        # Try to load Cindy's image
        try:
            from PIL import Image, ImageTk
            
            script_dir = pathlib.Path(__file__).parent.absolute()
            cindy_image_path = os.path.join(script_dir, 'projectcindy.gla')
            
            if os.path.exists(cindy_image_path):
                # Load image
                cindy_img = Image.open(cindy_image_path)
                
                # Resize to fit splash screen
                cindy_img.thumbnail((500, 500), Image.Resampling.LANCZOS)
                self.cindy_photo = ImageTk.PhotoImage(cindy_img)
                
                # Display image
                image_label = tk.Label(
                    self.root,
                    image=self.cindy_photo,
                    bg='#1e1e1e',
                    borderwidth=0
                )
                image_label.pack(pady=20)
                
            else:
                # No image - show text instead
                tk.Label(
                    self.root,
                    text="Project Cindy",
                    font=('Arial', 48, 'bold'),
                    bg='#1e1e1e',
                    fg='#00ff00'
                ).pack(pady=100)
                
        except ImportError:
            # Pillow not installed - show text instead
            tk.Label(
                self.root,
                text="Project Cindy",
                font=('Arial', 48, 'bold'),
                bg='#1e1e1e',
                fg='#00ff00'
            ).pack(pady=100)
        
        # Project name
        tk.Label(
            self.root,
            text="Project Cindy",
            font=('Arial', 32, 'bold'),
            bg='#1e1e1e',
            fg='#00ff00'
        ).pack(pady=10)
        
        # Subtitle
        tk.Label(
            self.root,
            text="Endless Online Bot",
            font=('Arial', 16),
            bg='#1e1e1e',
            fg='#00aaff'
        ).pack()
        
        # Loading message
        self.loading_label = tk.Label(
            self.root,
            text="Loading...",
            font=('Arial', 14),
            bg='#1e1e1e',
            fg='#ffaa00'
        )
        self.loading_label.pack(pady=20)
        
        # Progress bar
        self.progress_canvas = tk.Canvas(
            self.root,
            width=400,
            height=20,
            bg='#0a0a0a',
            highlightthickness=0
        )
        self.progress_canvas.pack(pady=10)
        
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 20,
            fill='#00ff00',
            outline=''
        )
        
        # Start progress animation
        self.progress = 0
        self.animate_progress()
        
        # Close after 5 seconds and launch main bot
        self.root.after(5000, self.launch_bot)
        
    def animate_progress(self):
        """Animate the progress bar"""
        # Multiple safety checks
        if not self.is_animating:
            return
        
        if self.is_destroyed:
            return
            
        if self.progress < 400:
            self.progress += 8  # 400/50 = 8 per update
            try:
                # Check if widgets still exist before accessing
                if not self.is_destroyed and self.progress_canvas.winfo_exists():
                    self.progress_canvas.coords(self.progress_bar, 0, 0, self.progress, 20)
                    self.animation_id = self.root.after(100, self.animate_progress)
                else:
                    self.is_animating = False
            except (tk.TclError, AttributeError):
                # Window was destroyed, stop animating
                self.is_animating = False
                self.is_destroyed = True
    
    def launch_bot(self):
        """Close splash and launch main bot"""
        # Stop animation first
        self.is_animating = False
        self.is_destroyed = True
        
        # Cancel any pending animation callbacks
        if self.animation_id:
            try:
                self.root.after_cancel(self.animation_id)
            except:
                pass
        
        # Give a moment for callbacks to stop
        try:
            self.root.update()
        except:
            pass
        
        # Destroy splash screen
        try:
            self.root.quit()  # Stop mainloop first
            self.root.destroy()
        except:
            pass
        
        # Small delay to ensure cleanup
        time.sleep(0.1)
        
        # Import and launch main bot
        try:
            import tkinter as tk
            import cindy_ui
            
            # Create new root window for bot UI
            root = tk.Tk()
            app = cindy_ui.BotUI(root)
            root.mainloop()
        except Exception as e:
            # Create a new root for error dialog since splash was destroyed
            try:
                error_root = tk.Tk()
                error_root.withdraw()
                messagebox.showerror("Launch Error", f"Failed to launch Cindy Bot:\n\n{e}")
                error_root.destroy()
            except:
                # If even error dialog fails, just print
                print(f"ERROR: Failed to launch Cindy Bot: {e}")
    
    def run(self):
        """Run the splash screen"""
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.is_animating = False
            self.is_destroyed = True

def main():
    splash = CindySplashScreen()
    splash.run()

if __name__ == "__main__":
    main()
