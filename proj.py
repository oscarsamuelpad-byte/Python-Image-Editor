# Imports and other necessary stuff

from pydoc import text
from PIL import ImageDraw
from PIL import Image, ImageTk, ImageFilter, ImageOps
import ttkbootstrap as ttk
import ttkbootstrap as tb
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import *
import os

history = []
draw_color = (0, 0, 0, 255)
last_x, last_y = None, None
DRAW_DELAY = 2

#app window tingz

app = ttk.Window(themename = "darkly")
app.title("Photo Editor 1.0")
app.geometry("800x600")
current_Image = None
display_Image = None

center_frame = ttk.Frame(app)
center_frame.pack(fill=tk.BOTH, expand=True)

#canvas = tk.Canvas(center_frame, bg="#333333")
#center_frame.pack(fill=tk.BOTH, expand=True)
canvas = tk.Canvas(center_frame, bg="#333333")
canvas.place(relx=0.5, rely=0.5, anchor="center", relwidth=1, relheight=1)
canvas.bind('<Configure>', lambda e: redraw_image())

app_icon = tk.PhotoImage(file="assets/icon.png") 
app.iconphoto(True, app_icon)

tool_var = tk.StringVar(value="None")

#functions

def refresh_state_image():
    global draw
    draw = ImageDraw.Draw(current_Image)
    update()

def redraw_image():
        canvas.delete('all')
        if display_Image is None:
            canvas_w = canvas.winfo_width()
            canvas_h = canvas.winfo_height()

            canvas.create_image(canvas_w // 2, canvas_h // 2, image=app_icon)
            return
        
        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()
        img_w = display_Image.width()
        img_h = display_Image.height()
        x = max(0, (canvas_w - img_w) // 2)
        y = max(0, (canvas_h - img_h) // 2)
        canvas.create_image(x, y, anchor='nw', image=display_Image)

def update():
        if current_Image is None:
            return
        
        global display_Image

        canvas.update()
        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()

        img_w, img_h = current_Image.size
        scale = min(canvas_w / img_w, canvas_h / img_h)

        new_w = int(img_w * scale)
        new_h = int(img_h * scale)

        resized = current_Image.resize((new_w, new_h), Image.LANCZOS)
        display_Image = ImageTk.PhotoImage(resized)

        redraw_image()

def save_image():
     if current_Image is None:
        messagebox.showinfo('Missing Image', 'No image to save')
        return
     path = filedialog.asksaveasfilename(defaultextension='.png', filetypes=[('PNG', '*.png'), ('JPEG', '*.jpg;*.jpeg'), ('BMP', '*.bmp')])

     if path:
         current_Image.save(path)

def open_image():
    global current_Image, display_Image # Use global variables to store the current and display images, so variable update outside function
    path = filedialog.askopenfilename(
        filetypes=[('Image files', '*.png;*.jpg;*.jpeg;*.bmp')]
    )
    
    if not path:
        return

    try:
        img = Image.open(path).convert("RGBA")
        print("Opened:", img)  
    except Exception as e:
        messagebox.showerror('Open Image', f'Failed to open image:\n{e}')

    
    current_Image = img
    
    refresh_state_image()

    
def filter_image():
    global current_Image, display_Image
    
    if current_Image is None:
        messagebox.showinfo('Missing Image', 'Image required to apply filter')
        return
    
    selected = FilterImage.get()

    if selected == 'Contour':
        filtered = current_Image.filter(ImageFilter.CONTOUR)
    elif selected == 'B&W':
        filtered = current_Image.convert(mode ='L')
    elif selected == 'Sepia':
        BnW = current_Image.convert(mode = 'L')
        filtered = ImageOps.colorize(BnW, "#4F2E0D", "#CAA886")
    elif selected == 'Blur':
        filtered = current_Image.filter(ImageFilter.BLUR)
    elif selected == 'Emboss':
        filtered = current_Image.filter(ImageFilter.EMBOSS)
    elif selected == 'Detail':
        filtered = current_Image.filter(ImageFilter.DETAIL)
    elif selected == 'Edge Enhance':
        filtered = current_Image.filter(ImageFilter.EDGE_ENHANCE)
    elif selected == 'Sharpen':
        filtered = current_Image.filter(ImageFilter.SHARPEN)
    elif selected == 'Smooth':
        filtered = current_Image.filter(ImageFilter.SMOOTH)
    elif selected == 'Select Filter':
        messagebox.showinfo('Missing Input', 'Please select a filter before applying')

    history.append(current_Image.copy())

    current_Image = filtered

    refresh_state_image()

def rotate_image():
    global current_Image, display_Image

    if current_Image is None:
        messagebox.showinfo('Missing Image', 'Image is required before rotating')
        return
    
    history.append(current_Image.copy())

    current_Image = current_Image.rotate(-90, expand=True)

    refresh_state_image()
    
def flip_image():
    global current_Image, display_Image

    if current_Image is None:
        messagebox.showinfo('Missing Image', 'Image is required before flipping')
        return
    
    history.append(current_Image.copy())

    current_Image = ImageOps.mirror(current_Image)

    refresh_state_image()

def undo_image():
    global current_Image, display_Image
        
    if not history: 
        messagebox.showinfo('Missing Input', 'No actions to undo')
        return

    
    current_Image = history.pop()

    refresh_state_image()

#How values are updated
def pen_size(val):
    size = int(float(val))   
    pen_size_label.config(text=f"Pen size: {size}")

def eraser_size(val):
    size = int(float(val))   
    eraser_size_label.config(text=f"Eraser size: {size}")

def update_tool():
    tool = tool_var.get()
    if tool == 'Pen':
        EraserScale.config(state=DISABLED)
        PenColor.config(state=READONLY)
        PenScale.config(state=NORMAL)
    elif tool == 'Eraser':
        PenScale.config(state=DISABLED)
        PenColor.config(state=DISABLED)
        EraserScale.config(state=NORMAL)

def set_color(event=None):
    global draw_color

    colors = {
        "Red": (255, 0, 0, 255),
        "Green": (0, 255, 0, 255),
        "Blue": (0, 0, 255, 255),
        "Yellow": (255, 255, 0, 255),
        "Black": (0, 0, 0, 255),
        "White": (255, 255, 255, 255)
    }

    draw_color = colors.get(PenColor.get(), (0, 0, 0, 255))

def start_draw(event):
    global last_x, last_y
    if current_Image is not None:
        history.append(current_Image.copy())

    last_x, last_y = event.x, event.y

def draw_image(event):
    global last_x, last_y, current_Image, draw

    if current_Image is None:
        return

    if last_x == None or last_y == None:
        last_x, last_y = event.x, event.y
        return

    tool = tool_var.get()

    canvas_w = canvas.winfo_width()
    canvas_h = canvas.winfo_height()
    img_w, img_h = current_Image.size

    scale = min(canvas_w / img_w, canvas_h / img_h)
    offset_x = (canvas_w - img_w * scale) / 2
    offset_y = (canvas_h - img_h * scale) / 2

    x1 = int((last_x - offset_x) / scale)
    y1 = int((last_y - offset_y) / scale)
    x2 = int((event.x - offset_x) / scale)
    y2 = int((event.y - offset_y) / scale)

    dx = x2 - x1
    dy = y2 - y1
    steps = int(max(abs(dx), abs(dy)))

    if steps == 0:
        steps = 1

    if tool == 'Pen':
        size = int(float(PenScale.get()))
        color = draw_color

    elif tool == 'Eraser':
        size = int(float(EraserScale.get()))
        color = (0, 0, 0, 0)  

    else:
        return

    for i in range(steps):
        x = int(x1 + dx * i / steps)
        y = int(y1 + dy * i / steps)

        draw.ellipse(
            [x - size//2, y - size//2, x + size//2, y + size//2],
            fill=color
        )

    last_x, last_y = event.x, event.y

    canvas.after(DRAW_DELAY, update)

def stop_draw(event):
    global last_x, last_y
    last_x, last_y = None, None

canvas.bind("<Button-1>", start_draw)
canvas.bind("<B1-Motion>", draw_image)
canvas.bind("<ButtonRelease-1>", stop_draw)

#button components

button_frame = ttk.Frame(app)
button_frame.pack(pady=10)
button_frame.pack(anchor="center")

Open_icon = Image.open("assets/Open.png")
Open_icon = Open_icon.resize((40, 40))
Open_icon = ImageTk.PhotoImage(Open_icon)

OpenImage = ttk.Button(
    button_frame,
    image=Open_icon,
    bootstyle="warning",
    command=open_image,
    width=20
)
Open_icon.image = Open_icon
OpenImage.pack(side =tk.LEFT, pady=20, ipadx=10, ipady=10)


save_icon = Image.open("assets/save.png")
save_icon = save_icon.resize((40, 40))
save_icon = ImageTk.PhotoImage(save_icon)

SaveImage = ttk.Button(
    button_frame,
     image = save_icon,
     bootstyle="warning",
     command = save_image,
     width=20
    
)
SaveImage.image = save_icon
SaveImage.pack(side =tk.LEFT, pady=20, padx=10, ipadx=10, ipady=10)

FilterImage = ttk.Combobox(
    button_frame, 
    values=['Contour', 'B&W', 'Sepia', 'Blur', 'Emboss', 'Detail', 'Edge Enhance', 'Sharpen', 'Smooth'],
    width = 20,
    state = READONLY
    )

FilterImage.pack(side = tk.LEFT, pady=20, padx=10,)  
FilterImage.set('Select Filter') 

ttk.Button(
    button_frame, 
    text="Apply", 
    bootstyle = 'warning', 
    command = filter_image).pack(side=tk.LEFT, pady=20, padx = 10
    )


rotate_icon = Image.open("assets/rotate.png")
rotate_icon = rotate_icon.resize((40, 40))
rotate_icon = ImageTk.PhotoImage(rotate_icon)

RotateImage = ttk.Button(
        button_frame,
        image = rotate_icon,
        bootstyle = 'Warning',
        command = rotate_image,
        width = 20
)

rotate_icon.image = rotate_icon
RotateImage.pack(side = tk.LEFT, pady=20, padx=10, ipadx= 10, ipady=10)

flip_icon = Image.open("assets/flip.png")
flip_icon = flip_icon.resize((40, 40))
flip_Icon = ImageTk.PhotoImage(flip_icon)

FlipImage = ttk.Button(
    button_frame,
    image = flip_Icon,
    bootstyle = 'Warning',
    command = flip_image,
    width = 20
)

flip_icon.image = flip_icon
FlipImage.pack(side = tk.LEFT, pady=20, padx=10, ipadx=10, ipady=10)       

undo_icon = Image.open("assets/undo.png")
undo_icon = undo_icon.resize((40, 40))
undo_icon = ImageTk.PhotoImage(undo_icon)

UndoAction = ttk.Button(
    button_frame,
    image = undo_icon,
    bootstyle = 'Warning',
    command = undo_image,
    width = 20
)

undo_icon.image = undo_icon
UndoAction.pack(side = tk.LEFT, pady=20, padx=10, ipadx=10, ipady=10)

#scale for pen and eraser size
PenScale = tb.Scale(
    button_frame,
    orient = VERTICAL,
    style = 'warning',
    length = 50,
    from_= 10 , 
    to_ = 0,
    command = pen_size
    )

EraserScale = tb.Scale(
    button_frame,
    orient = VERTICAL,
    style = 'danger',
    length = 50,
    from_= 10 , 
    to_ = 0,
    state = NORMAL,
    command = eraser_size
)

eraser_size_label = ttk.Label(button_frame)
pen_size_label = ttk.Label(button_frame)
#Initial values of scales and labels
PenScale.set(0)
EraserScale.set(0)
#Properties of scales and labels
PenScale.pack(side=tk.LEFT, pady=20, padx=10, ipadx=10, ipady=10)
EraserScale.pack(side=tk.LEFT, pady=20, padx=10, ipadx=10, ipady=10)

pen_size_label.pack(side=tk.LEFT)
eraser_size_label.pack(side=tk.LEFT)


PenColor = ttk.Combobox(
    button_frame, values=['Red', 'Green', 'Blue', 'Yellow', 'Black', 'White'],
    width = 20,
    state = READONLY
    
    )

PenColor.bind("<<ComboboxSelected>>", set_color)
PenColor.pack(side = tk.LEFT, pady=20, padx=10)
PenColor.set('Select Color of choice')

Pen_icon = Image.open("assets/Brush.png")
Pen_icon = Pen_icon.resize((40, 40))
Pen_icon = ImageTk.PhotoImage(Pen_icon)

PenChoice = ttk.Radiobutton(
    button_frame,
    image = Pen_icon, 
    value = 'Pen', 
    bootstyle = 'warning',
    variable = tool_var,
    command = update_tool,


)
PenChoice.pack(side=tk.LEFT, pady=20, padx=10)

Eraser_icon = Image.open("assets/Eraser.png")
Eraser_icon = Eraser_icon.resize((40, 40))
Eraser_icon = ImageTk.PhotoImage(Eraser_icon)

EraserChoice = ttk.Radiobutton(
    button_frame,
    image = Eraser_icon,
    value = 'Eraser',
    variable = tool_var,
    command = update_tool,
 
    bootstyle = 'warning'

)
EraserChoice.pack(side=tk.LEFT, pady=20, padx=10)


app.mainloop()

