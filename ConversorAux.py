import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from ttkthemes import ThemedStyle
import math
from PIL import Image, ImageTk  # Para agregar íconos

# Variables para almacenar la selección de archivos y carpeta
input_files = []
output_format_folder = ""

def select_files():
    global input_files
    new_files = filedialog.askopenfilenames(
        title="Seleccionar archivos de entrada", 
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    if new_files:
        input_files.extend(new_files)  # Acumular los archivos seleccionados
        success_label.config(text=f"{len(input_files)} archivos seleccionados", foreground="#4CAF50")

def select_folder():
    global output_format_folder
    output_format_folder = filedialog.askdirectory(title="Seleccionar carpeta para guardar los archivos en formato")
    if output_format_folder:
        success_label.config(text="Carpeta seleccionada correctamente", foreground="#4CAF50")

def process_files():
    if not input_files:
        messagebox.showwarning("Advertencia", "Por favor, seleccione los archivos primero.")
        return
    
    if not output_format_folder:
        messagebox.showwarning("Advertencia", "Por favor, seleccione una carpeta de guardado.")
        return
    
    # Procesar y agrupar los pedidos por sucursal
    sucursal_data, error_lines_combined = group_orders_by_sucursal(input_files)
    
    # Guardar los pedidos organizados por sucursal
    save_orders_by_sucursal(sucursal_data, output_format_folder)
    
    # Mostrar resumen gráfico
    success_label.config(text=f"Lotes procesados: {len(input_files)}\nTotal de sucursales: {len(sucursal_data)}", foreground="#4CAF50")

    # Guardar los errores si es necesario
    save_error_option = messagebox.askyesno("Guardar Errores", "¿Desea guardar los archivos de errores?")
    if save_error_option:
        output_error_folder = filedialog.askdirectory(title="Seleccionar carpeta para guardar los archivos de error")
        if output_error_folder:
            error_file_path = os.path.join(output_error_folder, "errores.txt")
            write_lines_to_file(error_lines_combined, error_file_path)
    
    messagebox.showinfo("Proceso finalizado", "El proceso ha finalizado con éxito.")

def extract_sucursal_from_filename(filename):
    # Usamos expresiones regulares para extraer el número de la sucursal en el formato "- SucXX -"
    match = re.search(r'- Suc(\d{1,2}) -', filename)
    if match:
        return match.group(1).zfill(2)  # Aseguramos que sea de dos dígitos
    return None

def group_orders_by_sucursal(input_files):
    sucursal_data = {}
    error_lines_combined = []
    
    for input_file_path in input_files:
        sucursal = extract_sucursal_from_filename(os.path.basename(input_file_path))
        if not sucursal:
            messagebox.showerror("Error", f"No se pudo extraer la sucursal del archivo: {input_file_path}")
            continue

        sucursal_data_in_file, error_lines = process_file(input_file_path)
        error_lines_combined.extend(error_lines)
        
        # Agrupar por sucursal
        if sucursal not in sucursal_data:
            sucursal_data[sucursal] = []
        sucursal_data[sucursal].extend(sucursal_data_in_file.get(sucursal, []))
    
    return sucursal_data, error_lines_combined

def process_file(input_file_path):
    sucursal_data = {}
    error_lines = []
    with open(input_file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            barcode = line[:13]
            if len(re.findall(r'\d', barcode)) >= 5 and barcode.count('0') <= 7:
                match = re.search(r'\d+(?=[^\d]*$)', line)
                if match:
                    quantity = match.group(0)
                    if ',' in line[len(barcode) + len(quantity):]:
                        quantity = 1
                    else:
                        quantity = int(math.ceil(float(quantity)))
                else:
                    quantity = "No se encontró cantidad"
                description = re.sub(r'\d', '', line[13:-len(str(quantity))]).strip()
                
                sucursal = extract_sucursal_from_filename(os.path.basename(input_file_path))
                
                if sucursal not in sucursal_data:
                    sucursal_data[sucursal] = []
                
                # Crear un pedido y agregarlo a la sucursal
                pedido = {
                    'barcode': barcode.strip(),
                    'description': description,
                    'quantity': quantity
                }
                sucursal_data[sucursal].append(pedido)
            else:
                error_lines.append(line)
    
    return sucursal_data, error_lines

def save_orders_by_sucursal(sucursal_data, output_folder):
    for sucursal, pedidos in sucursal_data.items():
        # Crear un archivo por cada sucursal
        output_file_path = os.path.join(output_folder, f"pedidos_sucursal_{sucursal}.txt")
        with open(output_file_path, 'w') as output_file:
            for pedido in pedidos:
                line = f"{pedido['barcode']};{pedido['description']};{pedido['quantity']}\n"
                output_file.write(line)

def write_lines_to_file(lines, file_path):
    with open(file_path, 'w') as output_file:
        for line in lines:
            output_file.write(line)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Conversor de archivos")
root.geometry("500x350")  # Tamaño de ventana inicial

root.resizable(True, True)
root.configure(bg="#F5F5F5")  # Fondo más suave

# Estilo
style = ThemedStyle(root)
style.set_theme("arc")
style.configure('TButton', font=('Arial', 12, 'bold'), foreground='#000000', background="#FFFFFF")
style.configure('TLabel', font=('Arial', 12), foreground='#000000', background="#F5F5F5")

# Añadir íconos a los botones en formato .ico y reducir tamaño
def load_image(path, size=(15, 15)):
    img = Image.open(path)
    img = img.resize(size, Image.LANCZOS)  # Corregido a LANCZOS
    return ImageTk.PhotoImage(img)

file_icon = load_image('file_icon.ico')
folder_icon = load_image('folder_icon.ico')
process_icon = load_image('process_icon.ico')

# Widgets
select_files_button = ttk.Button(root, text="Seleccionar Archivos", command=select_files, image=file_icon, compound=tk.LEFT)
select_files_button.pack(pady=10)

select_folder_button = ttk.Button(root, text="Seleccionar Carpeta", command=select_folder, image=folder_icon, compound=tk.LEFT)
select_folder_button.pack(pady=10)

process_button = ttk.Button(root, text="Procesar Archivos", command=process_files, image=process_icon, compound=tk.LEFT)
process_button.pack(pady=10)

progress_label = ttk.Label(root, text="Progreso de la conversión:", font=('Arial', 10, 'italic'))
progress_label.pack()

progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate')
progress_bar.pack(fill='x', padx=20, pady=10)

success_label = ttk.Label(root, text="", font=('Arial', 10, 'bold'))
success_label.pack(pady=10)

# Funciones para tooltips
def on_hover(event):
    tooltip_label.config(text="Selecciona los archivos en formato .TXT")

def on_leave(event):
    tooltip_label.config(text="")

# Tooltip label
tooltip_label = ttk.Label(root, text="", background="#F5F5F5")
tooltip_label.pack()

# Eventos de hover
select_files_button.bind("<Enter>", on_hover)
select_files_button.bind("<Leave>", on_leave)

root.mainloop()
