# Import things
from PIL import Image, ImageTk
import ttkbootstrap as ttk
import tkinter as tk
from tkinter import filedialog, messagebox
from ttkbootstrap.constants import *
import os


#app window tingz
app = ttk.Window(themename = "darkly")
app.title("Photo Editor 1.0")
app.geometry("1280x720")
current_Image = None
display_Image = None

center_frame = ttk.Frame(app)
center_frame.pack(fill=tk.BOTH, expand=True)

canvas = tk.Canvas(center_frame, bg="#333333")
canvas.pack(fill=tk.BOTH, expand=True)
canvas.bind('<Configure>', lambda e: redraw_image())

#functions

def redraw_image():
        canvas.delete('all')
        if display_Image is None:
           
            canvas.create_text(500, 250, text='Open an image to begin', fill='white', font=(None, 16))
            return
        
        canvas_w = canvas.winfo_width()
        canvas_h = canvas.winfo_height()
        img_w = display_Image.width()
        img_h = display_Image.height()
        x = max(0, (canvas_w - img_w) // 2)
        y = max(0, (canvas_h - img_h) // 2)
        canvas.create_image(x, y, anchor='nw', image=display_Image)

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
        img = Image.open(path)
        print("Opened:", img)  
    except Exception as e:
        messagebox.showerror('Open Image', f'Failed to open image:\n{e}')

    

    current_Image = img

    #Now, we need to rescale the image

    canvas.update()
    canvas_w = canvas.winfo_width()
    canvas_h = canvas.winfo_height()

    img_w, img_h = img.size
    scale = min(canvas_w / img_w, canvas_h / img_h)

    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    resized =  img.resize((new_w, new_h), Image.LANCZOS)

    display_Image = ImageTk.PhotoImage(resized) #added tkinter compatibility
    redraw_image() #no recall, nothing was redrawn and no display

#button components

button_frame = ttk.Frame(app)
button_frame.pack(pady=10)
button_frame.pack(anchor="center")

OpenImage = ttk.Button(
    app,
    text="Import Image",
    bootstyle="warning",
    command=open_image,
    width=20
)


OpenImage.pack(side =tk.LEFT, pady=20, ipadx=10, ipady=10)


save_icon = Image.open("test.png")
save_icon = save_icon.resize((40, 40))
save_icon = ImageTk.PhotoImage(save_icon)

SaveImage = ttk.Button(

     app,
     image = save_icon,
     bootstyle="warning",
     command = save_image,
     width=20
    
)
SaveImage.image = save_icon
SaveImage.pack(side =tk.LEFT, pady=20, padx=10, ipadx=10, ipady=10)



app.mainloop()
