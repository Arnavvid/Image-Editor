from tkinter import *
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import ttk, colorchooser, Scale, HORIZONTAL
import tkinter as tk
import os
from pathlib import Path
from PIL import Image, ImageTk, ImageGrab, ImageEnhance, ImageDraw

#root/ main window
root = tk.Tk()
root.title("Epic Photo Editor")

#root.attributes('-fullscreen', True)
root.state('zoomed')
root.resizable(False,False)
root.config(bg = '#050521')

#folder path
current_path = Path.cwd()

undo = []
redo = []

img_id, img = None, None
thickness_menu, multi_menu, shape_menu = None, None, None # Added shape_menu
selected_color = "black"
selected_thickness = 1
current_image = None
x_pressed, y_pressed, x_released, y_released = None, None, None, None
x_root, y_root, x1_root, y1_root = None, None, None, None
img = None
selected_brightness = 1
selected_saturation = 1
selected_sharpness = 1
bg_color = "white"
selected_shape = "rectangle" # Default shape
shape_size = 1  # Default size
hasfill = BooleanVar()
hasfill.set(True)
selected_fill_color = "black"
dynX = dynY = 0
shape_fill = None

#getimage size
def image_size():
    global x_root, y_root, x1_root, y1_root
    x, y, x1, y1 = main_canvas.bbox(img_id)
    x_root = main_canvas.winfo_rootx() + x
    y_root = main_canvas.winfo_rooty() + y
    x1_root = main_canvas.winfo_rootx() + x1
    y1_root = main_canvas.winfo_rooty() + y1

def text_popup(in_text, time: int):
    popup = Toplevel(root)
    popup.resizable(False,False)
    popup.overrideredirect(True)

    popup_label = tk.Label(popup, text = str(in_text), font = 'Calibri 15 bold', fg = 'white', bg = '#050521')
    popup_label.pack(expand = True)

    popup.update_idletasks()

    x = (root.winfo_screenwidth() // 2) - (popup.winfo_reqwidth() // 2)
    y = (root.winfo_screenheight() // 2)-20
    popup.geometry(f"+{x}+{y}")
    popup.after(time, popup.destroy)

def update_mem():
    global undo, redo
    x = root.winfo_rootx() + main_canvas.winfo_x() + 40
    y = root.winfo_rooty() + main_canvas.winfo_y()
    x1 = x + main_canvas.winfo_width()
    y1 = y + main_canvas.winfo_height()

    temp_img = ImageGrab.grab((x, y, x1, y1))
    temp_img = ImageTk.PhotoImage(temp_img)
    if (len(undo)-1 > 5000):
        undo = undo[1:]
    undo.append(temp_img)

def undo_mem():
    global undo, redo, img_id
    if not undo:
        return
    x = len(undo)-1
    mem_img = undo[x]

    canvas_width = main_canvas.winfo_width()
    canvas_height = main_canvas.winfo_height()

    main_canvas.delete("all")

    x_center = canvas_width // 2
    y_center = canvas_height // 2

    if(mem_img is not None):
        img_id = main_canvas.create_image(x_center,y_center,image = mem_img, anchor=tk.CENTER)
        redo.append(undo[x])
        if x != 0:
            undo.pop(-1)

def redo_mem():
    global undo, redo, img_id
    if not redo:
        return

    mem_img = redo[-1]

    canvas_width = main_canvas.winfo_width()
    canvas_height = main_canvas.winfo_height()

    main_canvas.delete("all")

    x_center = canvas_width // 2
    y_center = canvas_height // 2

    img_id = main_canvas.create_image(x_center, y_center, image=mem_img, anchor=tk.CENTER)
    undo.append(redo[-1])
    redo.pop(-1)


#file commands
def f_open():
    global current_image, img_id, img
    file_path = askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    if not file_path:
        return
    img = Image.open(file_path)

    canvas_width = main_canvas.winfo_width()
    canvas_height = main_canvas.winfo_height()
    img.thumbnail((canvas_width, canvas_height))
    current_image = ImageTk.PhotoImage(img)

    main_canvas.delete("all")

    x_center = canvas_width // 2
    y_center = canvas_height // 2
    img_id = main_canvas.create_image(x_center, y_center, image=current_image, anchor=tk.CENTER)
    update_mem()


def save(x = None, y = None, x1 = None, y1 = None):
    file_path = asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPG files", "*.jpg"), ("All Files", "*.*")])
    if file_path:
        global img_id
        if x is None or y is None or x1 is None or y1 is None:
            x = main_canvas.winfo_rootx()
            y = main_canvas.winfo_rooty()
            x1 = main_canvas.winfo_width() + x
            y1 = main_canvas.winfo_height() + y

            image = ImageGrab.grab((x, y, x1, y1))
            image.save(file_path)
            text_popup('Saved the entire canvas!', 2000)
        else:
            image = ImageGrab.grab((x, y, x1, y1))
            image.save(file_path)
            text_popup('Saved selected area', 2000)

def partial_save():
    text_popup("Select area to save", 1000)



#sidebar commands
selected_tool = None
def set_tool(tool_name, cursor_type):
    update_mem()
    global selected_tool
    selected_tool = tool_name
    if selected_tool != "thickness" and selected_tool != "color" and selected_tool != "imgset" and selected_tool != "shape": # Added shape
        root.config(cursor=cursor_type)
    task()

def mouse_initial(event):
    global x_pressed, y_pressed
    x_pressed, y_pressed = event.x, event.y

def mouse_final(event):
    global x_released, y_released
    x_released, y_released = event.x, event.y
    main_canvas.delete("temp_shape")
    main_canvas.update_idletasks()
    if selected_tool == "crop":
        crop()
    elif selected_tool == 'shape':
        global dynX, dynY
        dynX = None
        dynY = None
        draw_shape()

def draw(event):
    global x_pressed, y_pressed, shape_fill
    main_canvas.delete("temp_shape")

    if selected_tool == "crop":
        main_canvas.delete("rect1")
        root.update_idletasks()
        main_canvas.create_rectangle(x_pressed - 1, y_pressed - 1, event.x + 1, event.y + 1, fill=None, outline="black", width=2, tags='rect1')

    elif selected_tool == "paint":
        main_canvas.create_line(x_pressed, y_pressed, event.x, event.y, fill = selected_color, width = selected_thickness, capstyle= "round", smooth = True)
        x_pressed, y_pressed = event.x, event.y
        update_mem()

    elif selected_tool == "shape":
        if selected_shape == "rectangle":
            main_canvas.create_rectangle(x_pressed, y_pressed, event.x, event.y, fill=shape_fill, outline=selected_color, width=selected_thickness, tags = "temp_shape")
        elif selected_shape == "oval":
            main_canvas.create_oval(x_pressed, y_pressed, event.x, event.y, fill=shape_fill, outline=selected_color, width=selected_thickness, tags = "temp_shape")
        elif selected_shape == "line":
             main_canvas.create_line(x_pressed, y_pressed, event.x, event.y, fill=shape_fill, width=selected_thickness, capstyle= "round", smooth = True, tags = "temp_shape")





def erase(event):
    global x_pressed, y_pressed
    main_canvas.create_line(x_pressed, y_pressed, event.x, event.y, fill = bg_color, width = selected_thickness, capstyle= "round", smooth = True)
    x_pressed, y_pressed = event.x, event.y
    update_mem()

def fill_canvas_with_color():
    global main_canvas, bg_color
    bg_color = colorchooser.askcolor(title="Choose Fill Color")[1]
    if bg_color:
        main_canvas.delete("all")
        main_canvas.config(bg = bg_color)
        update_mem()



def crop(issave = False):
    global x_center, y_center
    if len(main_canvas.find_withtag("rect")) < 1 and len(main_canvas.find_withtag("rect1")) < 1:
        main_canvas.create_rectangle(x_pressed-1, y_pressed-1, x_released+1, y_released+1, fill = None, outline = "black", width = 1, tags = 'rect')

    canvas_width = main_canvas.winfo_width()
    canvas_height = main_canvas.winfo_height()

    x_center = canvas_width // 2
    y_center = canvas_height // 2

    confirm_window = Toplevel(root, height = 50, width = 100)
    confirm_window.geometry(f"100x50+{x_center}+{y_center}")
    
    def set_cropped():
        confirm_window.destroy()

        def crp():
            global cropped_image
            cropped_temp = ImageGrab.grab((int(x_pressed)+40, int(y_pressed)+44, int(x_released)+40, int(y_released)+44))
            cropped_image = ImageTk.PhotoImage(cropped_temp)
            main_canvas.delete("all")
            main_canvas.create_image(x_center, y_center , image = cropped_image)

        root.after(250,crp)

    def destroy_confirm():
        confirm_window.destroy()
        main_canvas.delete("rect")
        main_canvas.delete("rect1")

    save_button = tk.Button(confirm_window, text = "Save", command = set_cropped)
    save_button.pack(side = "left", padx = 5)

    cancel_button = tk.Button(confirm_window, text = "Cancel", command=destroy_confirm)
    cancel_button.pack(side = "right", padx = 5)

def clear_canvas():
    main_canvas.delete("all")

def task():
    if selected_tool == "thickness":
        global thickness_menu, selected_thickness, img
        def update_thickness(value):
            global selected_thickness
            selected_thickness = int(value)

        if thickness_menu:
            thickness_menu.destroy()
        thickness_menu = Toplevel(root)
        thickness_menu.resizable(False, False)
        thickness_menu.title("Thickness")
        op = tk.Scale(thickness_menu, from_=1, to=100, orient=HORIZONTAL, label="Select Thickness", command=update_thickness)
        op.set(selected_thickness)
        op.pack()
        if op.get():
            selected_thickness = int(op.get())

    elif selected_tool == "color":
        global selected_color
        color = colorchooser.askcolor(title="Pick a Color")[1]
        if color:
            selected_color = color

    elif selected_tool == "paint":
        main_canvas.bind("<Button-1>", mouse_initial)
        main_canvas.bind("<B1-Motion>", draw)
        update_mem()

    elif selected_tool == "erase":
        main_canvas.bind("<Button-1>", mouse_initial)
        main_canvas.bind("<B1-Motion>", erase)
        update_mem()

    elif selected_tool == "crop":
        main_canvas.bind("<Button-1>", mouse_initial)
        main_canvas.bind("<B1-Motion>", draw)
        main_canvas.bind("<ButtonRelease-1>", mouse_final)
        update_mem()

    elif selected_tool == "imgset":
        global multi_menu
        if multi_menu:
            multi_menu.destroy()
        update_mem()

        def apply_adjustments():
            global current_image
            if img:
                adjusted_img = img.copy()

                enhancer = ImageEnhance.Brightness(adjusted_img)
                adjusted_img = enhancer.enhance(selected_brightness)

                enhancer = ImageEnhance.Color(adjusted_img)
                adjusted_img = enhancer.enhance(selected_saturation)

                enhancer = ImageEnhance.Sharpness(adjusted_img)
                adjusted_img = enhancer.enhance(selected_sharpness)

                current_image = ImageTk.PhotoImage(adjusted_img)
                main_canvas.itemconfig(img_id, image=current_image)

                update_mem()

        def update_brightness(value):
            global current_image, selected_brightness
            selected_brightness = float(value) / 100
            apply_adjustments()

        def update_saturation(value):
            global current_image, selected_saturation
            selected_saturation = float(value) / 100
            apply_adjustments()

        def update_sharpness(value):
            global selected_sharpness
            selected_sharpness = float(value) / 100
            apply_adjustments()


        multi_menu = Toplevel(root, bg = "#0a001a")
        multi_menu.resizable(False, False)
        multi_menu.title("Image Settings")

        brightness = tk.Scale(multi_menu,  from_= 0, to = 600, orient=HORIZONTAL, label="Brightness", command = update_brightness, bg = "#0a001a", fg = "white", font = "ArialBlack 9")
        brightness.set(selected_brightness*100)
        brightness.pack()

        saturation = tk.Scale(multi_menu, from_= -300 , to = 300, orient= HORIZONTAL, label = "Saturation", command = update_saturation, bg = "#0a001a", fg = "white", font = "ArialBlack 9")
        saturation.set(selected_saturation*100)
        saturation.pack()

        sharpness = tk.Scale(multi_menu, from_= -100 , to = 500, orient= HORIZONTAL, label = "Sharpness", command = update_sharpness, bg = "#0a001a", fg = "white", font = "ArialBlack 9")
        sharpness.set(selected_sharpness*100)
        sharpness.pack()

    elif selected_tool == 'shape':
        global shape_menu, selected_shape, shape_size
        def update_shape(shape):
            global selected_shape
            selected_shape = shape
        def update_size(value):
            global shape_size
            shape_size = int(value)
        if shape_menu:
            shape_menu.destroy()

        def s_f_c():
            global selected_fill_color
            selected_fill_color = colorchooser.askcolor(title="Pick a Color")[1]

        shape_menu = Toplevel(root)
        shape_menu.title("Select Shape")
        shape_menu.resizable(False, False)

        # Shape selection buttons
        global square_image, oval_image, line_image, hasfill


        tk.Button(shape_menu, image = square_image, command=lambda: update_shape("rectangle")).grid(row = 0, column = 0, columnspan = 1, padx = 10)
        tk.Button(shape_menu, image = oval_image, command=lambda: update_shape("oval")).grid(row = 0, column = 1, columnspan = 1, padx = 10)
        tk.Button(shape_menu, image = line_image, command=lambda: update_shape("line")).grid(row = 0, column = 2, columnspan = 1, padx = 10)

        tk.Checkbutton(shape_menu, text = "Fill", variable= hasfill).grid(row = 1, column = 0, pady = 10)
        tk.Button(shape_menu, image = color_image, command = s_f_c).grid(row = 1, column = 1, pady = 10)

        main_canvas.bind("<Button-1>", mouse_initial)
        main_canvas.bind("<B1-Motion>", draw)
        main_canvas.bind("<ButtonRelease-1>", mouse_final)
        update_mem()

def draw_shape():
    global x_pressed, y_pressed, x_released, y_released, selected_shape, selected_color, selected_thickness, shape_size, hasfill, selected_fill_color, shape_fill
    if hasfill.get():
        shape_fill = selected_fill_color
    else:
        shape_fill = None
    if x_pressed is not None and y_pressed is not None and x_released is not None and y_released is not None:
        if selected_shape == "rectangle":
            main_canvas.create_rectangle(x_pressed, y_pressed, x_released, y_released, fill=shape_fill, outline=selected_color, width=selected_thickness)
        elif selected_shape == "oval":
            main_canvas.create_oval(x_pressed, y_pressed, x_released, y_released, fill=shape_fill, outline=selected_color, width=selected_thickness)
        elif selected_shape == "line":
             main_canvas.create_line(x_pressed, y_pressed, x_released, y_released, fill=shape_fill, width=selected_thickness, capstyle= "round", smooth = True)
        update_mem()
        x_pressed, y_pressed, x_released, y_released = None, None, None, None



top_frame = tk.Frame(root, bg = "#0c0c6b")
top_frame.pack(side = "top" )

#initializing the menu bar
root.option_add("*Menu*Font", "Calibri 10 bold")
menu_bar = Menu(top_frame)
root.config(menu=menu_bar)
file_menu = Menu(menu_bar, tearoff=0)

#'file" menu
menu_bar.add_cascade(label="File", menu=file_menu)

file_menu.add_command(label="Open", command=f_open)
file_menu.add_command(label="Save", command=save)
file_menu.add_command(label = "Partial save", command = partial_save)

#'Canvas' menu
canvas_menu = Menu(menu_bar, tearoff=0)
canvas_menu.add_command(label="Clear", command=clear_canvas)
canvas_menu.add_command(label = "Background", command = fill_canvas_with_color)
menu_bar.add_cascade(label="Canvas", menu=canvas_menu)

#sidebar for tools
side_bar = tk.Frame(root, bg = "#282830")
side_bar.pack(side = 'left', fill = "y")


#sidebar thickness button
t_temp = str(current_path) + "\\pypics\\pythickness.png"
thickness_temp = Image.open(t_temp)
thickness_temp = thickness_temp.resize((20, 20))
thickness_image = ImageTk.PhotoImage(thickness_temp)

thickness_button = tk.Button(side_bar, image = str(thickness_image), command = lambda: set_tool("thickness","arrow"))
thickness_button.grid(row = 0, column = 0, pady = 10, padx = 7)

#sidebar color button
c_temp = str(current_path) + "\\pypics\\pycolor.png"
color_temp = Image.open(c_temp)
color_temp = color_temp.resize((20, 20))
color_image = ImageTk.PhotoImage(color_temp)

color_button = tk.Button(side_bar, image = str(color_image), command = lambda: set_tool("color","arrow"))
color_button.grid(row = 1, column = 0, pady = 10, padx = 7)

#sidebar paint button
p_temp = str(current_path) + "\\pypics\\pypaint.png"
paint_temp = Image.open(p_temp)
paint_temp = paint_temp.resize((20, 20))
paint_image = ImageTk.PhotoImage(paint_temp)

paint_button = tk.Button(side_bar, image = str(paint_image), command = lambda: set_tool("paint","circle"))
paint_button.grid(row = 2, column = 0, pady = 10, padx = 7)

#sidebar erase button
e_temp = str(current_path) + "\\pypics\\pyerase.png"
erase_temp = Image.open(e_temp)
erase_temp = erase_temp.resize((20, 20))
erase_image = ImageTk.PhotoImage(erase_temp)

erase_button = tk.Button(side_bar, image = str(erase_image), command = lambda: set_tool("erase","dotbox"))
erase_button.grid(row = 3, column = 0, pady = 10, padx = 7)

#sidebar image settings button
set_temp = str(current_path) + "\\pypics\\pyoptions.png"
imgset_temp = Image.open(set_temp)
imgset_temp = imgset_temp.resize((20, 20))
imgset_image = ImageTk.PhotoImage(imgset_temp)

imgset_button = tk.Button(side_bar, image = str(imgset_image), command = lambda: set_tool("imgset","arrow"))
imgset_button.grid(row = 4, column = 0, pady = 10, padx = 7)

#sidebar crop button
cr_temp = str(current_path) + "\\pypics\\pycrop.png"
crop_temp = Image.open(cr_temp)
crop_temp = crop_temp.resize((20,20))
crop_image = ImageTk.PhotoImage(crop_temp)

crop_button = tk.Button(side_bar, image = str(crop_image), command = lambda: set_tool("crop","cross"))
crop_button.grid(row = 5, column = 0, pady = 10, padx = 7)

#sidebar insert shape
sh_temp = str(current_path) + "\\pypics\\pyshapes.png"
shape_temp = Image.open(sh_temp)
shape_temp = shape_temp.resize((20,20))
shape_image = ImageTk.PhotoImage(shape_temp)

shape_button = tk.Button(side_bar, image = str(shape_image), command = lambda: set_tool("shape","cross"))
shape_button.grid(row = 6, column = 0, pady = 10, padx = 7)

square_image = ImageTk.PhotoImage((Image.open(str(current_path) + "\\pypics\\pysquare.png")).resize((20, 20)))
oval_image = ImageTk.PhotoImage((Image.open(str(current_path) + "\\pypics\\pyoval.png")).resize((20, 20)))
line_image = ImageTk.PhotoImage((Image.open(str(current_path) + "\\pypics\\pyline.png")).resize((20, 20)))

#sidebar undo button
un_temp = str(current_path) + "\\pypics\\pyundo.png"
undo_temp = Image.open(un_temp)
undo_temp = undo_temp.resize((20, 20))
undo_image = ImageTk.PhotoImage(undo_temp)

undo_button = tk.Button(side_bar, image = str(undo_image), command = undo_mem)
undo_button.grid(row = 7, column = 0, pady = 10, padx = 7)

#sidbar redo button
re_temp = str(current_path) + "\\pypics\\pyredo.png"
redo_temp = Image.open(re_temp)
redo_temp = redo_temp.resize((20, 20))
redo_image = ImageTk.PhotoImage(redo_temp)

redo_button = tk.Button(side_bar, image = str(redo_image), command = redo_mem)
redo_button.grid(row = 8, column = 0, pady = 10, padx = 7)

#--------MAIN FRAME----------
main_frame = tk.Frame(root, bg = "white")
main_frame.pack(fill = "both", expand = True)

main_canvas = tk.Canvas(main_frame)
main_canvas.pack(fill = "both", expand = True)
main_canvas.config(background='#ffffff')


root.mainloop()
