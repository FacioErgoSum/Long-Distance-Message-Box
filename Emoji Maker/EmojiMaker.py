import tkinter as tk
from tkinter import colorchooser, messagebox, simpledialog, filedialog
from tkinter import ttk
import json
import re

class PixelArtEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("16x16 Pixel Art Editor")
        
        # Current color
        self.current_color = "#000000"
        self.pixel_size = 30
        self.canvas_size = 16
        self.pixels = [[None for _ in range(self.canvas_size)] for _ in range(self.canvas_size)]
        self.pixel_colors = [["#FFFFFF" for _ in range(self.canvas_size)] for _ in range(self.canvas_size)]
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.pixel_size * self.canvas_size,
            height=self.pixel_size * self.canvas_size,
            bg="white"
        )
        self.canvas.grid(row=0, column=0, columnspan=4, pady=5)
        
        # Buttons frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        # Color picker button
        self.color_button = ttk.Button(
            self.buttons_frame,
            text="Choose Color",
            command=self.choose_color
        )
        self.color_button.grid(row=0, column=0, padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(
            self.buttons_frame,
            text="Clear Canvas",
            command=self.clear_canvas
        )
        self.clear_button.grid(row=0, column=1, padx=5)
        
        # Load button
        self.load_button = ttk.Button(
            self.buttons_frame,
            text="Load Emoji",
            command=self.load_art
        )
        self.load_button.grid(row=0, column=2, padx=5)
        
        # Export button
        self.export_button = ttk.Button(
            self.buttons_frame,
            text="Export Emoji",
            command=self.export_art
        )
        self.export_button.grid(row=0, column=3, padx=5)
        
        # Current color display
        self.color_display = tk.Label(
            self.main_frame,
            text="Current Color:",
            bg=self.current_color,
            width=20,
            height=2
        )
        self.color_display.grid(row=2, column=0, columnspan=4, pady=5)
        
        # Initialize canvas
        self.init_canvas()
        
        # Bind mouse events
        self.canvas.bind("<Button-1>", self.paint)
        self.canvas.bind("<B1-Motion>", self.paint)
        self.canvas.bind("<Button-3>", self.erase)  # Right click to erase
        self.canvas.bind("<B3-Motion>", self.erase)
        
    def init_canvas(self):
        """Initialize the canvas with white pixels"""
        for i in range(self.canvas_size):
            for j in range(self.canvas_size):
                x1 = j * self.pixel_size
                y1 = i * self.pixel_size
                x2 = x1 + self.pixel_size
                y2 = y1 + self.pixel_size
                self.pixels[i][j] = self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="white",
                    outline="gray"
                )
    
    def choose_color(self):
        """Open color picker and set current color"""
        color = colorchooser.askcolor(title="Choose Color")[1]
        if color:
            self.current_color = color
            self.color_display.config(bg=color)
    
    def clear_canvas(self):
        """Clear the entire canvas to white"""
        for i in range(self.canvas_size):
            for j in range(self.canvas_size):
                self.canvas.itemconfig(self.pixels[i][j], fill="white")
                self.pixel_colors[i][j] = "#FFFFFF"
    
    def paint(self, event):
        """Paint a pixel when clicked"""
        x = event.x // self.pixel_size
        y = event.y // self.pixel_size
        if 0 <= x < self.canvas_size and 0 <= y < self.canvas_size:
            self.canvas.itemconfig(self.pixels[y][x], fill=self.current_color)
            self.pixel_colors[y][x] = self.current_color
    
    def erase(self, event):
        """Erase a pixel (set to white) when right-clicked"""
        x = event.x // self.pixel_size
        y = event.y // self.pixel_size
        if 0 <= x < self.canvas_size and 0 <= y < self.canvas_size:
            self.canvas.itemconfig(self.pixels[y][x], fill="white")
            self.pixel_colors[y][x] = "#FFFFFF"
    
    def hex_to_uint16(self, hex_color):
        """Convert hex color to uint16 format (RGB565)"""
        if hex_color == "#FFFFFF" or hex_color.upper() == "#FFFFFF":
            return 0x0000  # Use 0x0000 for transparent/white pixels
            
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16) >> 3  # 5 bits
        g = int(hex_color[2:4], 16) >> 2  # 6 bits  
        b = int(hex_color[4:6], 16) >> 3  # 5 bits
        return (r << 11) | (g << 5) | b
    
    def uint16_to_hex(self, uint16_value):
        """Convert uint16 format (RGB565) back to hex color"""
        if uint16_value == 0x0000:
            return "#FFFFFF"  # Treat 0x0000 as white/transparent
            
        # Extract RGB components from RGB565
        r = (uint16_value >> 11) & 0x1F  # 5 bits
        g = (uint16_value >> 5) & 0x3F   # 6 bits
        b = uint16_value & 0x1F          # 5 bits
        
        # Scale back to 8-bit values
        r = (r << 3) | (r >> 2)  # Scale 5-bit to 8-bit
        g = (g << 2) | (g >> 4)  # Scale 6-bit to 8-bit
        b = (b << 3) | (b >> 2)  # Scale 5-bit to 8-bit
        
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def load_art(self):
        """Load a previously exported emoji from file"""
        file_path = filedialog.askopenfilename(
            title="Select Emoji File",
            filetypes=[("Text files", "*.txt"), ("Header files", "*.h"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse the uint16 array from the file
            # Look for pattern like: const uint16_t EMOJI_NAME[] = { ... };
            pattern = r'const\s+uint16_t\s+\w+\[\]\s*=\s*\{([^}]+)\}'
            match = re.search(pattern, content, re.DOTALL)
            
            if not match:
                messagebox.showerror("Error", "Could not find valid emoji data in file")
                return
            
            # Extract the array values
            array_content = match.group(1)
            # Find all hex values (0x followed by hex digits)
            hex_values = re.findall(r'0x[0-9A-Fa-f]+', array_content)
            
            if len(hex_values) != 256:  # 16x16 = 256 pixels
                messagebox.showerror("Error", f"Expected 256 values, found {len(hex_values)}")
                return
            
            # Clear the canvas first
            self.clear_canvas()
            
            # Load the values into the canvas
            for i in range(self.canvas_size):
                for j in range(self.canvas_size):
                    index = i * self.canvas_size + j
                    uint16_value = int(hex_values[index], 16)
                    hex_color = self.uint16_to_hex(uint16_value)
                    
                    # Update the pixel
                    self.canvas.itemconfig(self.pixels[i][j], fill=hex_color)
                    self.pixel_colors[i][j] = hex_color
            
            messagebox.showinfo("Success", "Emoji loaded successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load emoji: {str(e)}")
    
    def export_art(self):
        """Export the pixel art to a text file"""
        name = tk.simpledialog.askstring("Export", "Enter name for your pixel art:")
        if not name:
            return
        
        # Clean the name (remove spaces, special characters)
        clean_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
            
        # Generate the export string
        export_lines = [f"// {name} (16x16 pixels)"]
        export_lines.append(f"const uint16_t EMOJI_{clean_name.upper()}[] = {{")
        
        # Convert colors to uint16 format
        for i in range(self.canvas_size):
            line = "    "
            for j in range(self.canvas_size):
                color = self.pixel_colors[i][j]
                uint16_value = self.hex_to_uint16(color)
                line += f"0x{uint16_value:04X}"
                if j < self.canvas_size - 1:
                    line += ", "
            if i < self.canvas_size - 1:
                line += ","
            export_lines.append(line)
        
        export_lines.append("};")
        
        # Save to file
        filename = f"{clean_name}_emoji.txt"
        with open(filename, "w") as f:
            f.write("\n".join(export_lines))
        
        messagebox.showinfo("Success", f"Emoji saved as {filename}")
        
        # Also show instructions for adding to the header file
        instructions = f"""
To use this emoji in your message box:

1. Add this code to your emoji_definitions.h file
2. Add to EMOJI_MAP array:
   "{clean_name[:2].upper()}", "EMOJI_{clean_name.upper()}",
3. Add to getEmojiFromText() function:
   if(strcmp(EMOJI_MAP[i + 1], "EMOJI_{clean_name.upper()}") == 0) return EMOJI_{clean_name.upper()};
4. Use "{clean_name[:2].upper()}" in your messages to display this emoji
        """
        
        messagebox.showinfo("Integration Instructions", instructions)

if __name__ == "__main__":
    root = tk.Tk()
    app = PixelArtEditor(root)
    root.mainloop()