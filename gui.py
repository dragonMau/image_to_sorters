import sys
import tkinter
from os import getcwd, getlogin, mkdir, path
from math import ceil
from tkinter import filedialog

from PIL import Image, ImageTk

import custom
import tool

class keysim:
    keycode: int
    def __init__(self, k):
        self.keycode = k

root = tkinter.Tk()
custom.master = root

image_raw = Image.new("RGB", (250, 250), color="#53565c")
tool.reform_photo(image_raw, 250, 250)
image_tk = ImageTk.PhotoImage(tool.converted)
def kWH(): t = image_raw.width / image_raw.height; return t #width height
def kSF(): t = 250/max(tool.converted.size); return t # size field

source_frame = tkinter.Frame(root)
source_label = tkinter.Label(source_frame, text="Source image:")
source_field = custom.Entry(source_frame, width=100, placeholder=f"{getcwd()}")
source_button = tkinter.Button(source_frame, text="Browse")

panel_image = tkinter.Label(root, image=image_tk,
    borderwidth=2, relief="solid",width=250, height=250, background="#53565c")
piece_frame = tkinter.Frame(root)

piece_x_label = tkinter.Label(piece_frame, text="piece width: ")
piece_x_entry = custom.Entry(piece_frame, placeholder="32")
piece_y_label = tkinter.Label(piece_frame, text="piece height: ")
piece_y_entry = custom.Entry(piece_frame, placeholder="32")

schematic_frame = tkinter.Frame(root)
total_x_label = tkinter.Label(schematic_frame, text="schematic width: ")
total_x_entry = custom.Entry(schematic_frame, placeholder="32")
total_y_label = tkinter.Label(schematic_frame, text="schematic height: ")
total_y_entry = custom.Entry(schematic_frame, placeholder="32")

filename_frame = tkinter.Frame(root)
filename_label = tkinter.Label(filename_frame, text="schematic name: ")
filename_entry = custom.Entry(filename_frame, placeholder="schematic")
file_export = tkinter.Button(filename_frame, text="Export")
abs_path = path.abspath('./out').replace(':\\', '://').replace('\\', '/')

dest_frame = tkinter.Frame(root)
dest_label = tkinter.Label(dest_frame, foreground="gray", text=f"{abs_path}/")

console_frame = tkinter.Frame(root)
console_box = tkinter.Text(console_frame, wrap='char', height=10, width=58, state="disabled")
console_scrole = tkinter.Scrollbar(console_frame, orient="vertical")

def normpath(p: str) -> str:
    return path.normpath(p.strip('"\''))

def load_image(e, skip=False):
    if e.keycode != 13:
        return
    global image_tk, image_raw
    np = normpath(source_field.get())
    if path.isfile(np):
        if not skip:
            image_raw = Image.open(np) if not skip else image_raw
            total_x_entry.put(image_raw.width, True)
            total_y_entry.put(image_raw.height, True)
        tool.total_x, tool.total_y = int(total_x_entry.get()), int(total_y_entry.get())
        tool.reform_photo(image_raw, tool.total_x, tool.total_y)
        image_tk = ImageTk.PhotoImage(tool.converted.resize((ceil(tool.total_x*kSF()),
                                                             ceil(tool.total_y*kSF()))))
        panel_image.configure(image=image_tk)
        panel_image.image = image_tk
        if not skip:
            filename_entry.put(path.basename(np)[:path.basename(np).find(".")], True)

def show_full(*_):
    tool.converted.show()

def focus_out(entry: custom.Entry):
    cleared = ""
    for c in entry.get():
        cleared += c if c in "0123456789" else ""
    entry.delete(0, "end")
    if cleared.replace("0", "") == "":
        entry.put_placeholder()
    else:
        entry.insert(0, cleared)
def focus_out_px(e: tkinter.Event): 
    if e.type == "2":
        if e.keycode != 13: return
        root.focus()
    focus_out(piece_x_entry)
    tool.split_x = int(piece_x_entry.get())
def focus_out_py(e: tkinter.Event):
    if e.type == "2":
        if e.keycode != 13: return
        root.focus()
    focus_out(piece_y_entry)
    tool.split_y = int(piece_y_entry.get())
def focus_out_tx(e: tkinter.Event): 
    if e.type == "2":
        if e.keycode != 13: return
        root.focus()
    focus_out(total_x_entry)
    tool.total_x = int(total_x_entry.get())
    total_y_entry.placeholder = ceil(tool.total_x / kWH())
    total_y_entry.put_placeholder()
    load_image(keysim(13), skip=True)
def focus_out_ty(e: tkinter.Event): 
    if e.type == "2":
        if e.keycode != 13: return
        root.focus()
    focus_out(total_y_entry)
    tool.total_y = int(total_y_entry.get())
    total_x_entry.placeholder = ceil(tool.total_y * kWH())
    total_x_entry.put_placeholder()
    load_image(keysim(13), skip=True)

def browse(*_):
    file = filedialog.askopenfilename(
        initialdir = normpath(source_field.get()),
		title = "Select a File",
		filetypes = (
            ("images", ".png .jfif .jpg .jpeg"),
		    ("all files", ".*")
     ))
    source_field.put(file if file else source_field.get(), True)
    load_image(keysim(13))

def export(*_):
    name = filename_entry.get()
    if not path.isdir("./out"):
        mkdir("./out")
    if path.isdir(f"./out/{name}"):
        i = 1
        while path.isdir(f"./out/{name} ({i})"):
            i += 1
        mkdir(f"./out/{name} ({i})")
        result = tool.generate(f"{name} ({i})")
        dest_label.configure(text=f"{abs_path}/{name} ({i})/")
    else:
        mkdir(f"./out/{name}")
        result = tool.generate(name)
        dest_label.configure(text=f"{abs_path}/{name}/")
    print("Errors: \n  "+"\n  ".join(result[1]))
    print(f"\n{result[0]}")

def start():
    root.title("sorterizer")
    source_field.bind("<KeyPress>", load_image)
    panel_image.bind("<Double-1>", show_full)
    source_button.configure(command=browse)
    root.bind("<Button-1>", custom.Entry.rbb)
    piece_x_entry.bind("<FocusOut>", focus_out_px)
    piece_y_entry.bind("<FocusOut>", focus_out_py)
    total_x_entry.bind("<FocusOut>", focus_out_tx)
    total_y_entry.bind("<FocusOut>", focus_out_ty)
    piece_x_entry.bind("<KeyPress>", focus_out_px)
    piece_y_entry.bind("<KeyPress>", focus_out_py)
    total_x_entry.bind("<KeyPress>", focus_out_tx)
    total_y_entry.bind("<KeyPress>", focus_out_ty)
    file_export.configure(command=export)
    console_box.config(yscrollcommand=console_scrole.set)
    console_scrole.config(command=console_box.yview)
    
    source_frame.pack(anchor="nw", fill="x", expand=False, side="top")   
    panel_image.pack(anchor="nw", fill="x", expand=False, side="left")
    piece_frame.pack(anchor="nw", fill="x", expand=False, side="top")
    schematic_frame.pack(anchor="nw", fill="x", expand=False, side="top")
    filename_frame.pack(anchor="nw", fill="x", expand=False, side="top")
    dest_frame.pack(anchor="nw", fill="x", expand=False, side="top")
    console_frame.pack(anchor="nw", fill="x", expand=False, side="top")
    
    source_label.pack(anchor="nw", side="left")
    source_field.pack(anchor="nw", side="left")
    source_button.pack(anchor="nw", side="left")
    
    
    piece_x_label.pack(anchor="nw", side="left")
    piece_x_entry.pack(anchor="nw", side="left")
    piece_y_label.pack(anchor="nw", side="left")
    piece_y_entry.pack(anchor="nw", side="left")
    
    total_x_label.pack(anchor="nw", side="left")
    total_x_entry.pack(anchor="nw", side="left")
    total_y_label.pack(anchor="nw", side="left")
    total_y_entry.pack(anchor="nw", side="left")
    
    filename_label.pack(anchor="nw", side="left")
    filename_entry.pack(anchor="nw", side="left")
    file_export.pack(anchor="nw", side="left")
    
    dest_label.pack(anchor="nw", fill="x", expand=False, side="left")
    
    console_box.pack(anchor="nw", fill="both", expand=False, side="left")
    console_scrole.pack(anchor="nw", fill="both", expand=False, side="left")
    
    sys.stdout = custom.StdoutRedirector(console_box)
    
    root.mainloop()




if __name__ == "__main__":
    start()
