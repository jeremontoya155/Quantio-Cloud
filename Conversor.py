import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
from ttkthemes import ThemedStyle
import math

def convert_and_save_files():
    input_files = filedialog.askopenfilenames(
        title="Seleccionar archivos de entrada", 
        filetypes=(("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*"))
    )
    if input_files:
        output_format_folder = filedialog.askdirectory(title="Seleccionar carpeta para guardar los archivos en formato")
        if output_format_folder:
            num_files = len(input_files)
            progress_bar['maximum'] = num_files
            for idx, input_file_path in enumerate(input_files, start=1):
                output_file_path_format = add_format_to_filename(input_file_path, output_format_folder)
                converted_lines, error_lines = convert_file(input_file_path)
                write_lines_to_file(converted_lines, output_file_path_format)
                progress_bar['value'] = idx
                root.update_idletasks()

            success_label.config(text="¡Archivos en formato guardados con éxito!", foreground="white")

            save_error_option = messagebox.askyesno("Guardar Errores", "¿Desea guardar los archivos de errores?")
            if save_error_option:
                output_error_folder = filedialog.askdirectory(title="Seleccionar carpeta para guardar los archivos de error")
                if output_error_folder:
                    save_errors_to_folder(input_files, output_error_folder)

            messagebox.showinfo("Proceso finalizado", "El proceso ha finalizado con éxito.")

def add_format_to_filename(input_file_path, output_folder):
    filename = os.path.basename(input_file_path)
    filename_no_extension, file_extension = os.path.splitext(filename)
    return os.path.join(output_folder, filename_no_extension + "_formato" + file_extension)

def add_error_to_filename(input_file_path, output_folder):
    filename = os.path.basename(input_file_path)
    filename_no_extension, file_extension = os.path.splitext(filename)
    return os.path.join(output_folder, filename_no_extension + "_error" + file_extension)

def convert_file(input_file_path):
    converted_lines = []
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
                converted_lines.append(f"{barcode.strip()};{description};{quantity}\n")
            else:
                error_lines.append(line)
    return converted_lines, error_lines

def write_lines_to_file(lines, file_path):
    with open(file_path, 'w') as output_file:
        for line in lines:
            output_file.write(line)

def save_errors_to_folder(input_files, output_folder):
    for input_file_path in input_files:
        output_file_path_error = add_error_to_filename(input_file_path, output_folder)
        converted_lines, error_lines = convert_file(input_file_path)
        write_lines_to_file(error_lines, output_file_path_error)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Conversor de archivos")
root.geometry("500x160")
root.resizable(False, False)
root.configure(bg="white")

# Estilo
style = ThemedStyle(root)
style.set_theme("arc")
style.configure('TButton', font=('Arial', 12, 'bold'), foreground='black', background="white")
style.configure('TLabel', font=('Arial', 12, 'bold'), foreground='black', background="white")

def convert():
    convert_button['state'] = 'disabled'
    convert_and_save_files()
    convert_button['state'] = 'normal'

# Widgets
convert_button = ttk.Button(root, text="Subir Archivos", command=convert)
convert_button.pack(pady=5)

progress_label = ttk.Label(root, text="Progreso de la conversión:")
progress_label.pack()

progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate')
progress_bar.pack(fill='x', padx=20)

success_label = ttk.Label(root, text="")
success_label.pack()

# Funciones para tooltips
def on_hover(event):
    tooltip_label.config(text="Selecciona los archivos de integra en formato .TXT")

def on_leave(event):
    tooltip_label.config(text="")

# Tooltip label
tooltip_label = ttk.Label(root, text="")
tooltip_label.pack()

# Eventos de hover
convert_button.bind("<Enter>", on_hover)
convert_button.bind("<Leave>", on_leave)

root.mainloop()
