import os
import tkinter as tk
from tkinter import filedialog, messagebox, Text
from PIL import Image, ImageTk
import map_handler
from minimap_scanner import MinimapScanner
import threading

class DarkAndDarkerTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Dark and Darker Utility Tool")
        self.root.geometry("300x400")
        self.map_handler = map_handler.MapHandler()
        self.setup_ui()
        self.monitor = {"top": 880, "left": 2800, "width": 400, "height": 600}
        self.best_map_path = None
        self.scanner = None
        self.map_window = None
        self.canvas = None
        self.rect = None
        self.player_rect = None
        self.scanning_active = None

    def setup_ui(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=20)

        button_start = tk.Button(frame, text="Start Scanning", command=self.start_scanning, width=20, height=2)
        button_select = tk.Button(frame, text="Select Maps", command=self.select_maps, width=20, height=2)
        button_help = tk.Button(frame, text="Help", command=self.help_function, width=20, height=2)
        button_select_minimap = tk.Button(frame, text="Select Minimap Region", command=self.select_minimap_region, width=20, height=2)

        button_start.pack(pady=10)
        button_select_minimap.pack(pady=10)
        button_select.pack(pady=10)
        button_help.pack(pady=10)

    def start_scanning(self):
        if self.scanning_active is False or self.scanning_active is None:
            self.maps = self.map_handler.get_maps()
            if not self.maps:
                messagebox.showerror("Error", "No maps selected. Please select maps first.")
                return

            self.map_image_paths = [map_obj.get_image_path() for map_obj in self.maps]
            self.scanner = MinimapScanner(self.map_image_paths, self.monitor, self)

            # Capture the initial minimap to find the best match
            query_img = self.scanner.capture_minimap()
            self.best_map_path = self.scanner.find_best_match(query_img)

            if self.best_map_path:
                self.scanning_active = True
                self.update_rectangle_continuously()

    def on_close(self):
        self.scanning_active = False
        if self.map_window is not None:
            self.map_window.destroy()

    def update_rectangle_continuously(self):
        def update():
            self.scanner.start_continuous_scanning(self.best_map_path, self.update_rectangle)

        thread = threading.Thread(target=update)
        thread.daemon = True
        thread.start()

    def update_rectangle(self, x, y, w, h):
        if x is not None and y is not None and w is not None and h is not None:
            self.show_matching_region(self.best_map_path, x, y, w, h)

    def show_matching_region(self, map_image_path, x, y, w, h):
        if self.map_window is None or not self.map_window.winfo_exists():
            map_image = Image.open(map_image_path)
            map_image = ImageTk.PhotoImage(map_image)

            self.map_window = tk.Toplevel(self.root)
            self.map_window.title("Matching Region")
            self.map_window.geometry(f"{map_image.width()}x{map_image.height()}")
            self.map_window.protocol("WM_DELETE_WINDOW", self.on_close)

            self.canvas = tk.Canvas(self.map_window, width=map_image.width(), height=map_image.height())
            self.canvas.pack()

            self.canvas.create_image(0, 0, anchor=tk.NW, image=map_image)
            self.map_image = map_image  # Keep a reference to prevent garbage collection

        if self.rect is not None:
            self.canvas.delete(self.rect)
            self.canvas.delete(self.player_rect)
        player_x = (2*x+w)/2
        player_y = (2*y+h)/2
        self.rect = self.canvas.create_rectangle(x, y, x + w, y + h, outline='red', width=2)
        self.player_rect = self.canvas.create_rectangle(player_x, player_y , player_x+16, player_y + 16, fill='red', width=2)

    def select_maps(self):
        self.new_window = tk.Toplevel(self.root)
        self.new_window.title("Select Maps")
        self.new_window.geometry("500x300")
        self.select_maps_text = tk.StringVar()
        self.update_text_select_maps()

        self.label = tk.Label(self.new_window, textvariable=self.select_maps_text)
        self.label.pack()

        button_frame = tk.Frame(self.new_window)
        button_frame.pack(side='bottom', pady=10)

        button_load = tk.Button(button_frame, text="Load Maps", command=self.load_maps)
        button_load.pack(side='left', padx=10)

        button_close = tk.Button(button_frame, text="Clear Maps", command=self.clear_maps)
        button_close.pack(side='right', padx=10)

    def update_text_select_maps(self):
        self.map_handler.load_maps()
        self.select_maps_text.set("Loaded maps: \n " + self.map_handler.get_maps_as_lb_string())

    def help_function(self):
        messagebox.showinfo("Help", "Help functionality will be implemented here.")

    def select_minimap_region(self):
        overlay = tk.Toplevel(self.root)
        overlay.attributes("-fullscreen", True)
        overlay.attributes("-topmost", True)
        overlay.attributes("-alpha", 0.8)
        overlay.configure(bg='gray')

        region_selector = DraggableRectangle(overlay, self.monitor)
        region_selector.make_draggable()
        overlay.mainloop()

    def load_maps(self):
        file_path = filedialog.askopenfilenames()
        self.map_handler.clear_maps()
        if file_path:
            lst = list(file_path)
            for map_path in lst:
                head, tail = os.path.split(map_path)
                self.map_handler.add_map(map_path, tail)
        self.map_handler.save_maps()
        self.update_text_select_maps()

    def clear_maps(self):
        self.map_handler.clear_maps()
        self.map_handler.save_maps()
        self.update_text_select_maps()

class DraggableRectangle:
    def __init__(self, overlay, monitor):
        self.overlay = overlay
        self.canvas = tk.Canvas(self.overlay, bg='gray', highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=tk.YES)
        self.rect = None
        self.start_x = None
        self.start_y = None
        self.end_x = None
        self.end_y = None
        self.rect_id = None
        self.monitor = monitor

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        if not self.rect:
            self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_move_press(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        self.end_x, self.end_y = (event.x, event.y)
        self.parse_rectangle_position()
        print(self.monitor)
        self.overlay.destroy()

    def make_draggable(self):
        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_move_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def parse_rectangle_position(self):
        width = abs(self.start_x - self.end_x)
        height = abs(self.start_y - self.end_y)

        leftmost_x = min(self.start_x, self.end_x)
        upmost_y = min(self.start_y, self.end_y)

        self.monitor.update({"top": upmost_y})
        self.monitor.update({"left": leftmost_x})
        self.monitor.update({"width": width})
        self.monitor.update({"height": height})

if __name__ == "__main__":
    root = tk.Tk()
    app = DarkAndDarkerTool(root)
    root.mainloop()
