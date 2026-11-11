# Analizador FASTA con Docker y Compose

Proyecto de aprendizaje de José Mijail Campos Compean: un analizador Python resume un FASTA de ejemplo y Nginx sirve el reporte por HTTP. Práctica complementaria al curso **Learning Docker** de LinkedIn Learning.

## Qué demuestra

- Construir una imagen propia con un Dockerfile.
- Ejecutar un análisis como tarea temporal con `docker compose run --rm`.
- Leer datos con un bind mount de solo lectura y conservar la salida en el equipo.
- Escribir reportes con el UID/GID del usuario del equipo.
- Compartir la carpeta de reportes entre servicios y servirla mediante Nginx.
- Publicar un puerto solo en localhost y diagnosticar con `ps`, `logs` y `curl`.

## Flujo

```text
datos/ejemplo.fasta → analizador Python → reportes/resumen-compose.txt
                                                  ↓
                                                Nginx
                                                  ↓
                       http://localhost:8084/resumen-compose.txt
```

Los servicios comparten archivos mediante la carpeta `reportes/` del equipo. Ejecutar el analizador y comprobar su éxito precede al arranque de Nginx; no hay ejecución automática del análisis al levantar `web`.

## Requisitos

- Docker Engine en funcionamiento y el complemento Docker Compose (`docker compose`).
- Linux; práctica original realizada en Fedora 45 con SELinux.
- Puerto local 8084 disponible.
- `curl` para comprobar el servicio; Python 3 solo si se desea ejecutar sin Docker.

## Ejecutar

Clona el repositorio y entra en él:

```bash
git clone https://github.com/mijailcampos/docker-fasta-demo.git
cd docker-fasta-demo
mkdir -p reportes
id -u
id -g
```

El analizador usa `user: "1000:1000"` en `compose.yaml`. Si los dos comandos anteriores muestran otros valores, ajusta esa línea a `"TU_UID:TU_GID"` antes de ejecutar, para poder escribir en tu carpeta de reportes.

En Fedora, si el motor está detenido:

```bash
sudo systemctl start docker
```

Genera el reporte. Continúa únicamente si el comando termina correctamente:

```bash
sudo docker compose run --rm --build analizador
cat reportes/resumen-compose.txt
```

Salida esperada:

```text
Secuencias: 2
Bases: ACGTGGNN
Longitud total: 8
GC: 66.67%
```

Inicia Nginx y consulta el reporte:

```bash
sudo docker compose up -d web
curl --fail --retry 5 --retry-connrefused --retry-delay 1 http://localhost:8084/resumen-compose.txt
```

Abre también esa URL en el navegador del mismo equipo. El puerto 8084 del equipo se conecta al puerto 80 del contenedor; está publicado únicamente en `127.0.0.1`.

Los comandos usan `sudo`, como en la práctica original. En equipos donde tu sesión ya tiene acceso al motor, puedes omitirlo.

## Actualizar los resultados y detener

Al editar `datos/ejemplo.fasta`, vuelve a ejecutar el analizador para regenerar el reporte:

```bash
sudo docker compose run --rm analizador
```

Nginx puede seguir activo y servir el archivo actualizado. Si modificas `analizador.py`, reconstruye la imagen añadiendo `--build` al comando anterior: el Dockerfile copia ese código durante el build.

Para detener la práctica:

```bash
sudo docker compose down
```

Los archivos en `datos/` y `reportes/` permanecen en el equipo. El contenedor del analizador se elimina tras cada ejecución con `--rm`. No se necesita limpiar otros contenedores o imágenes.

## Analizador y ejemplos

El script cuenta encabezados FASTA, concatena las secuencias y calcula la longitud global. Calcula GC como `(G + C) / (A + C + G + T) × 100`: las bases `N` no entran en el denominador.

También puedes ejecutarlo directamente:

```bash
python3 analizador.py datos/ejemplo.fasta
```

| Entrada | Resultado esperado |
| --- | --- |
| `ejemplo.fasta` | 2 secuencias, 8 bases, GC 66.67%; salida 0 |
| `solo_n.fasta` | 1 secuencia, 4 bases, GC no calculable; salida 0 |
| `vacio.fasta` | Error: archivo vacío; salida 2 |
| `sin_encabezado.fasta` | Error: sin encabezados FASTA; salida 2 |

## Diagnóstico

```bash
sudo docker compose config -q
sudo docker compose ps
sudo docker compose logs --tail=20 web
```

| Síntoma | Qué revisar |
| --- | --- |
| No se puede conectar al motor Docker | Estado del servicio y acceso de la sesión al socket |
| No se puede escribir en `/salida` | UID/GID configurados y permisos de `reportes/` |
| HTTP 404 | Existencia de `reportes/resumen-compose.txt` y nombre exacto de la URL |
| Conexión rechazada | Estado de `web`, puerto 8084 y tiempo de arranque |
| Puerto ocupado | Otro proceso utiliza 8084; elige otro puerto local en Compose |

En sistemas con SELinux, `:Z` etiqueta la entrada para uso privado y `:z` permite compartir los reportes entre ambos contenedores. El montaje de Nginx es de solo lectura (`ro`); el del analizador permite escribir la salida.

## Alcance y límites

Es un ejercicio educativo con datos sintéticos diminutos, no un validador FASTA completo ni una herramienta de producción. El script carga la entrada completa en memoria, imprime las bases y solo detecta archivo vacío o ausencia total de encabezados; no valida todas las reglas FASTA ni el alfabeto biológico. Los errores de lectura del sistema de archivos no tienen manejo personalizado.

Las etiquetas base `python:3.13-slim` y `nginx:stable` pueden cambiar. El flujo se puede repetir, pero no garantiza imágenes idénticas bit a bit. No se incluyen datos privados, reportes generados, credenciales ni el PDF del certificado.
