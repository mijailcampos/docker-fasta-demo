import argparse
from pathlib import Path

parser = argparse.ArgumentParser(description="Resume un archivo FASTA")
parser.add_argument("entrada", type=Path, help="Ruta del archivo FASTA")
args = parser.parse_args()

archivo = args.entrada

texto = archivo.read_text()

if not texto.strip():
    parser.error("El archivo de entrada está vacío")

numero_secuencias = 0
bases = ""

for linea in texto.splitlines():
    linea = linea.strip()

    if linea.startswith(">"):
        numero_secuencias += 1
    else:
        bases += linea.upper()

if numero_secuencias == 0:
    parser.error("El archivo no contiene encabezados FASTA")

print(f"Secuencias: {numero_secuencias}")
print(f"Bases: {bases}")
print(f"Longitud total: {len(bases)}")
cantidad_gc = bases.count("G") + bases.count("C")

cantidad_acgt = (
    bases.count("A")
    + bases.count("C")
    + bases.count("G")
    + bases.count("T")
)

if cantidad_acgt > 0:
    porcentaje_gc = cantidad_gc / cantidad_acgt * 100
    print(f"GC: {porcentaje_gc:.2f}%")
else:
    print("GC: no calculable (sin bases A, C, G o T)")
