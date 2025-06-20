import subprocess

input_filename = "server/machotes/divorcio_incausado.docx"
# input_filename = "server/machotes/convenio_divorcio_incausado.docx"
# output_filename = "server/machotes/convenio_divorcio_incausado.html"
output_filename = "server/machotes/divorcio_incausado.html"

# Ejecuta el comando pandoc
result = subprocess.run(
    ["pandoc", input_filename, "-o", output_filename], capture_output=True, text=True
)

if result.returncode == 0:
    print(f"Archivo HTML generado: {output_filename}")
else:
    print("Error al convertir el archivo:")
    print(result.stderr)
