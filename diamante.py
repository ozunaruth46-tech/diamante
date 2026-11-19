#!/usr/bin/env python3
"""
Diamante 💎 — un lenguaje de programación en español, simple como hablar.
Creado por Ruth Abigail Ozuna (Plottier, Neuquén, Argentina).

Cómo funciona por dentro:
  1. Lee tu programa .dia línea por línea.
  2. Traduce cada línea de Diamante a Python (esto se llama "transpilar").
  3. Ejecuta el resultado y, si algo falla, te avisa en español y en qué línea.

Uso:
  python diamante.py programa.dia      -> ejecuta un programa
  python diamante.py                   -> abre la consola interactiva
  python diamante.py --ver programa.dia -> muestra la traducción a Python
"""

import os
import random
import re
import smtplib
import sys
sys.modules.setdefault("diamante", sys.modules[__name__])
from email.message import EmailMessage

VERSION = "0.3"

# ---------------------------------------------------------------------------
# 1. Funciones que vienen incluidas en Diamante
# ---------------------------------------------------------------------------

def _mostrar(*cosas):
    print(*[_a_texto(c) for c in cosas])


def _a_texto(valor):
    if valor is True:
        return "verdadero"
    if valor is False:
        return "falso"
    if valor is None:
        return "nada"
    if isinstance(valor, float) and valor.is_integer():
        return str(int(valor))
    if isinstance(valor, list):
        return "[" + ", ".join(_a_texto(v) for v in valor) + "]"
    return str(valor)


def _preguntar(texto=""):
    respuesta = input(_a_texto(texto) + " ")
    try:
        return int(respuesta)
    except ValueError:
        try:
            return float(respuesta.replace(",", "."))
        except ValueError:
            return respuesta


def _enviar_correo(para, asunto, mensaje):
    """Envía un correo de verdad si hay cuenta configurada; si no, lo simula."""
    usuario = os.environ.get("DIAMANTE_CORREO")
    clave = os.environ.get("DIAMANTE_CLAVE")
    if not usuario or not clave:
        print(f"📧 [simulado] Para: {para} | Asunto: {asunto}")
        print(f"   {mensaje}")
        return False
    correo = EmailMessage()
    correo["From"] = usuario
    correo["To"] = para
    correo["Subject"] = asunto
    correo.set_content(mensaje)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(usuario, clave)
        servidor.send_message(correo)
    print(f"📧 Correo enviado a {para}")
    return True


# ---------------------------------------------------------------------------
# 1b. Superpoderes: archivos, imágenes, videos, QR, PDF, internet, clima
#     Todo con herramientas gratuitas y legales.
# ---------------------------------------------------------------------------

import csv
import datetime
import json
import subprocess
import tempfile
import time
import urllib.parse
import urllib.request

COLORES = {
    "plateado": "#C0C0C0", "plata": "#C0C0C0", "dorado": "#D4AF37", "blanco": "#FFFFFF",
    "negro": "#111111", "gris": "#808080", "rojo": "#E53935", "azul": "#1E5BD8",
    "celeste": "#6EC6FF", "verde": "#2E9E5B", "amarillo": "#FDD835", "naranja": "#FB8C00",
    "violeta": "#8E44AD", "rosa": "#F06292", "marron": "#795548", "marrón": "#795548",
}


class FaltaHerramienta(Exception):
    pass


def _necesito(modulo, paquete):
    try:
        return __import__(modulo)
    except ImportError:
        raise FaltaHerramienta(
            f"Para esto Diamante necesita una herramienta gratuita. Instalala con:  pip install {paquete}"
        )


def _color(c):
    return COLORES.get(str(c).lower().strip(), c)


def _fuente(tamano):
    _necesito("PIL", "pillow")
    from PIL import ImageFont
    for nombre in ("arialbd.ttf", "arial.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(nombre, tamano)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=tamano)
    except TypeError:
        return ImageFont.load_default()


def _crear_imagen(archivo, ancho=1080, alto=1080, fondo="plateado", texto="", color_texto="negro"):
    _necesito("PIL", "pillow")
    from PIL import Image, ImageDraw
    img = Image.new("RGB", (int(ancho), int(alto)), _color(fondo))
    if texto:
        dibujo = ImageDraw.Draw(img)
        tamano = max(20, int(min(ancho, alto) / 12))
        fuente = _fuente(tamano)
        # Partir el texto en renglones que entren en la imagen
        palabras, renglones, actual = str(texto).split(), [], ""
        for p in palabras:
            prueba = (actual + " " + p).strip()
            if dibujo.textlength(prueba, font=fuente) > ancho * 0.85 and actual:
                renglones.append(actual)
                actual = p
            else:
                actual = prueba
        renglones.append(actual)
        alto_renglon = int(tamano * 1.3)
        y = (alto - alto_renglon * len(renglones)) / 2
        for r in renglones:
            x = (ancho - dibujo.textlength(r, font=fuente)) / 2
            dibujo.text((x, y), r, fill=_color(color_texto), font=fuente)
            y += alto_renglon
    img.save(archivo)
    print(f"🖼️  Imagen creada: {archivo}")
    return archivo


def _crear_video(archivo, imagenes, segundos=2):
    """Arma un video tipo presentación con una lista de imágenes."""
    try:
        import imageio_ffmpeg
        ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        import shutil
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise FaltaHerramienta("Para videos instalá la herramienta gratuita:  pip install imageio-ffmpeg")
    if isinstance(imagenes, str):
        imagenes = [imagenes]
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as lista:
        for img in imagenes:
            ruta = os.path.abspath(img).replace("\\", "/").replace("'", "'\\''")
            lista.write(f"file '{ruta}'\nduration {float(segundos)}\n")
        ruta = os.path.abspath(imagenes[-1]).replace("\\", "/").replace("'", "'\\''")
        lista.write(f"file '{ruta}'\n")
    comando = [ffmpeg, "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lista.name,
               "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2,format=yuv420p", "-r", "30",
               "-c:v", "libx264", "-preset", "veryfast", archivo]
    subprocess.run(comando, check=True)
    os.unlink(lista.name)
    print(f"🎬 Video creado: {archivo}")
    return archivo


def _crear_qr(archivo, contenido):
    qrcode = _necesito("qrcode", "qrcode[pil]")
    qrcode.make(str(contenido)).save(archivo)
    print(f"🔳 QR creado: {archivo}")
    return archivo


def _crear_pdf(archivo, texto, titulo=""):
    _necesito("PIL", "pillow")
    from PIL import Image, ImageDraw
    ancho, alto, margen = 1240, 1754, 100  # hoja A4
    fuente, fuente_titulo = _fuente(34), _fuente(56)
    paginas, renglones = [], []
    medidor = ImageDraw.Draw(Image.new("RGB", (1, 1)))
    for parrafo in str(texto).split("\n"):
        actual = ""
        for p in parrafo.split():
            prueba = (actual + " " + p).strip()
            if medidor.textlength(prueba, font=fuente) > ancho - 2 * margen and actual:
                renglones.append(actual)
                actual = p
            else:
                actual = prueba
        renglones.append(actual)
    y, hoja = None, None
    for i, r in enumerate([None] + renglones):
        if hoja is None or y > alto - margen:
            hoja = Image.new("RGB", (ancho, alto), "white")
            paginas.append(hoja)
            y = margen
            if titulo and len(paginas) == 1:
                ImageDraw.Draw(hoja).text((margen, y), str(titulo), fill="black", font=fuente_titulo)
                y += 100
        if r is not None:
            ImageDraw.Draw(hoja).text((margen, y), r, fill="black", font=fuente)
            y += 48
    paginas[0].save(archivo, save_all=True, append_images=paginas[1:])
    print(f"📄 PDF creado: {archivo}")
    return archivo


def _guardar_texto(archivo, contenido, agregar=False):
    with open(archivo, "a" if agregar else "w", encoding="utf-8") as f:
        f.write(_a_texto(contenido) + "\n")
    return archivo


def _leer_texto(archivo):
    with open(archivo, encoding="utf-8") as f:
        return f.read()


def _guardar_planilla(archivo, filas):
    with open(archivo, "w", newline="", encoding="utf-8-sig") as f:
        escritor = csv.writer(f, delimiter=";")
        for fila in filas:
            escritor.writerow(fila if isinstance(fila, (list, tuple)) else [fila])
    print(f"📊 Planilla guardada: {archivo} (se abre con Excel)")
    return archivo


def _leer_planilla(archivo):
    with open(archivo, newline="", encoding="utf-8-sig") as f:
        muestra = f.read(2048)
        f.seek(0)
        separador = ";" if muestra.count(";") >= muestra.count(",") else ","
        return [fila for fila in csv.reader(f, delimiter=separador)]


def _leer_pagina(url):
    pedido = urllib.request.Request(url, headers={"User-Agent": "Diamante/0.2"})
    with urllib.request.urlopen(pedido, timeout=20) as r:
        html = r.read().decode("utf-8", errors="ignore")
    html = re.sub(r"(?is)<(script|style).*?</\1>", " ", html)
    texto_plano = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", texto_plano).strip()


def _pedir_json(url):
    pedido = urllib.request.Request(url, headers={"User-Agent": "Diamante/0.2"})
    with urllib.request.urlopen(pedido, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def _clima(ciudad):
    """Clima actual con Open-Meteo (gratis y sin registrarse)."""
    q = urllib.parse.quote(str(ciudad))
    lugar = _pedir_json(f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=es")
    if not lugar.get("results"):
        return f"No encontré la ciudad {ciudad}"
    l = lugar["results"][0]
    datos = _pedir_json(
        f"https://api.open-meteo.com/v1/forecast?latitude={l['latitude']}&longitude={l['longitude']}"
        "&current=temperature_2m,wind_speed_10m"
    )["current"]
    return f"{l['name']}: {datos['temperature_2m']}°C, viento {datos['wind_speed_10m']} km/h"


def _hoy():
    return datetime.date.today().strftime("%d/%m/%Y")


def _hora():
    return datetime.datetime.now().strftime("%H:%M")


def _esperar(segundos):
    time.sleep(float(segundos))


def _abrir(archivo_o_web):
    import webbrowser
    destino = archivo_o_web if re.match(r"^https?://", str(archivo_o_web)) else "file://" + os.path.abspath(archivo_o_web)
    webbrowser.open(destino)


INCLUIDAS = {
    "_mostrar": _mostrar,
    "_preguntar": _preguntar,
    "_enviar_correo": _enviar_correo,
    "crear_imagen": _crear_imagen,
    "crear_video": _crear_video,
    "crear_qr": _crear_qr,
    "crear_pdf": _crear_pdf,
    "guardar_texto": _guardar_texto,
    "leer_texto": _leer_texto,
    "guardar_planilla": _guardar_planilla,
    "leer_planilla": _leer_planilla,
    "leer_pagina": _leer_pagina,
    "clima": _clima,
    "hoy": _hoy,
    "hora": _hora,
    "esperar": _esperar,
    "abrir": _abrir,
    "contiene": lambda t, b: str(b).lower() in str(t).lower(),
    "reemplazar": lambda t, a, b: str(t).replace(str(a), str(b)),
    "dividir": lambda t, sep=" ": str(t).split(sep),
    "unir": lambda lista, sep=" ": str(sep).join(_a_texto(x) for x in lista),
    "largo": len,
    "texto": _a_texto,
    "numero": lambda v: float(str(v).replace(",", ".")) if "." in str(v) or "," in str(v) else int(v),
    "aleatorio": random.randint,
    "elegir": random.choice,
    "mayusculas": lambda t: str(t).upper(),
    "minusculas": lambda t: str(t).lower(),
    "redondear": round,
    "rango": lambda a, b=None: list(range(a, b + 1)) if b is not None else list(range(1, a + 1)),
    "agregar": lambda lista, valor: lista.append(valor),
    "suma": sum,
    "maximo": max,
    "minimo": min,
}

# ---------------------------------------------------------------------------
# 2. El traductor: Diamante -> Python
# ---------------------------------------------------------------------------

# Palabras sueltas que se reemplazan dentro de las expresiones
PALABRAS = {
    "verdadero": "True",
    "falso": "False",
    "nada": "None",
    "y": "and",
    "o": "or",
    "no": "not",
}

# Frases que se reemplazan antes que las palabras (el orden importa)
FRASES = [
    (r"\bes mayor o igual que\b", ">="),
    (r"\bes menor o igual que\b", "<="),
    (r"\bes mayor que\b", ">"),
    (r"\bes menor que\b", "<"),
    (r"\bes distinto de\b", "!="),
    (r"\bes igual a\b", "=="),
    (r"\best[aá] en\b", "in"),
    (r"\bmódulo\b|\bmodulo\b", "%"),
]

TEXTO = re.compile(r'"(?:[^"\\]|\\.)*"|\'(?:[^\'\\]|\\.)*\'')


def traducir_expresion(expr):
    """Traduce una expresión en español a Python, sin tocar lo que está entre comillas."""
    partes, ultimo = [], 0
    for m in TEXTO.finditer(expr):
        partes.append(("codigo", expr[ultimo:m.start()]))
        partes.append(("texto", m.group()))
        ultimo = m.end()
    partes.append(("codigo", expr[ultimo:]))

    resultado = []
    for tipo, trozo in partes:
        if tipo == "codigo":
            for patron, reemplazo in FRASES:
                trozo = re.sub(patron, reemplazo, trozo)
            trozo = re.sub(
                r"\b(" + "|".join(PALABRAS) + r")\b",
                lambda m: PALABRAS[m.group(1)],
                trozo,
            )
        resultado.append(trozo)
    return "".join(resultado).strip()


REGLAS = [
    # mostrar "hola", nombre
    (r"^mostrar\s+(.+)$", lambda m: f"_mostrar({traducir_expresion(m[1])})"),
    # preguntar "¿Cómo te llamás?" y guardar en nombre
    (r"^preguntar\s+(.+?)\s+y guardar en\s+(\w+)$",
     lambda m: f"{m[2]} = _preguntar({traducir_expresion(m[1])})"),
    # si edad es mayor que 18:
    (r"^si\s+(.+):$", lambda m: f"if {traducir_expresion(m[1])}:"),
    (r"^o si\s+(.+):$", lambda m: f"elif {traducir_expresion(m[1])}:"),
    (r"^sino:$", lambda m: "else:"),
    # repetir 3 veces:
    (r"^repetir\s+(.+)\s+veces:$", lambda m: f"for _ in range(int({traducir_expresion(m[1])})):"),
    # para cada empresa en empresas:
    (r"^para cada\s+(\w+)\s+en\s+(.+):$", lambda m: f"for {m[1]} in {traducir_expresion(m[2])}:"),
    # mientras contador es menor que 10:
    (r"^mientras\s+(.+):$", lambda m: f"while {traducir_expresion(m[1])}:"),
    # función saludar(nombre):
    (r"^funci[oó]n\s+(\w+)\s*\((.*)\):$", lambda m: f"def {m[1]}({m[2]}):"),
    (r"^devolver\s+(.+)$", lambda m: f"return {traducir_expresion(m[1])}"),
    (r"^devolver$", lambda m: "return"),
    (r"^salir$", lambda m: "break"),
    (r"^seguir$", lambda m: "continue"),
    # enviar correo a "x@y.com" asunto "Hola" mensaje "Texto"
    (r"^enviar correo a\s+(.+?)\s+asunto\s+(.+?)\s+mensaje\s+(.+)$",
     lambda m: f"_enviar_correo({traducir_expresion(m[1])}, {traducir_expresion(m[2])}, {traducir_expresion(m[3])})"),
    # --- Superpoderes en frases ---
    # crear imagen "cartel.png" de 1080 x 1080 con fondo "plateado" y texto "Hola"
    (r'^crear imagen\s+(.+?)\s+de\s+(\d+)\s*x\s*(\d+)(?:\s+con fondo\s+(.+?))?(?:\s+y texto\s+(.+?))?(?:\s+en color\s+(.+))?$',
     lambda m: f"crear_imagen({traducir_expresion(m[1])}, {m[2]}, {m[3]}, "
               f"{traducir_expresion(m[4]) if m[4] else repr('plateado')}, "
               f"{traducir_expresion(m[5]) if m[5] else repr('')}, "
               f"{traducir_expresion(m[6]) if m[6] else repr('negro')})"),
    # crear video "video.mp4" con imagenes ["a.png", "b.png"] de 2 segundos cada una
    (r'^crear video\s+(.+?)\s+con im[aá]genes\s+(.+?)(?:\s+de\s+(.+?)\s+segundos cada una)?$',
     lambda m: f"crear_video({traducir_expresion(m[1])}, {traducir_expresion(m[2])}, {traducir_expresion(m[3]) if m[3] else 2})"),
    # crear qr "qr.png" con "https://..."
    (r'^crear qr\s+(.+?)\s+con\s+(.+)$',
     lambda m: f"crear_qr({traducir_expresion(m[1])}, {traducir_expresion(m[2])})"),
    # crear pdf "informe.pdf" con titulo "X" y texto t   /   crear pdf "a.pdf" con texto t
    (r'^crear pdf\s+(.+?)\s+con t[ií]tulo\s+(.+?)\s+y texto\s+(.+)$',
     lambda m: f"crear_pdf({traducir_expresion(m[1])}, {traducir_expresion(m[3])}, {traducir_expresion(m[2])})"),
    (r'^crear pdf\s+(.+?)\s+con texto\s+(.+)$',
     lambda m: f"crear_pdf({traducir_expresion(m[1])}, {traducir_expresion(m[2])})"),
    # guardar "hola" en archivo "notas.txt"  /  agregar "hola" al archivo "notas.txt"
    (r'^guardar\s+(.+?)\s+en archivo\s+(.+)$',
     lambda m: f"guardar_texto({traducir_expresion(m[2])}, {traducir_expresion(m[1])})"),
    (r'^agregar\s+(.+?)\s+al archivo\s+(.+)$',
     lambda m: f"guardar_texto({traducir_expresion(m[2])}, {traducir_expresion(m[1])}, True)"),
    # guardar planilla "ventas.csv" con filas
    (r'^guardar planilla\s+(.+?)\s+con\s+(.+)$',
     lambda m: f"guardar_planilla({traducir_expresion(m[1])}, {traducir_expresion(m[2])})"),
    # leer archivo "a.txt" y guardar en t / leer planilla ... / leer página ... / clima en ...
    (r'^leer archivo\s+(.+?)\s+y guardar en\s+(\w+)$',
     lambda m: f"{m[2]} = leer_texto({traducir_expresion(m[1])})"),
    (r'^leer planilla\s+(.+?)\s+y guardar en\s+(\w+)$',
     lambda m: f"{m[2]} = leer_planilla({traducir_expresion(m[1])})"),
    (r'^leer p[aá]gina\s+(.+?)\s+y guardar en\s+(\w+)$',
     lambda m: f"{m[2]} = leer_pagina({traducir_expresion(m[1])})"),
    (r'^ver clima en\s+(.+?)\s+y guardar en\s+(\w+)$',
     lambda m: f"{m[2]} = clima({traducir_expresion(m[1])})"),
    (r'^esperar\s+(.+?)\s+segundos?$', lambda m: f"esperar({traducir_expresion(m[1])})"),
    (r'^abrir\s+(.+)$', lambda m: f"abrir({traducir_expresion(m[1])})"),
    # agregar "x" a lista
    (r'^agregar\s+(.+?)\s+a\s+(\w+)$', lambda m: f"{m[2]}.append({traducir_expresion(m[1])})"),
    # sumar 1 a contador / restar 1 a contador
    (r"^sumar\s+(.+)\s+a\s+(\w+)$", lambda m: f"{m[2]} += {traducir_expresion(m[1])}"),
    (r"^restar\s+(.+)\s+a\s+(\w+)$", lambda m: f"{m[2]} -= {traducir_expresion(m[1])}"),
    # nombre = "Ruth"
    (r"^(\w+)\s*=\s*(.+)$", lambda m: f"{m[1]} = {traducir_expresion(m[2])}"),
]


# --- Superpoderes 0.3 ---
import superpoderes as _sp
INCLUIDAS.update(_sp.TODO)

def _e(x):
    return traducir_expresion(x)

REGLAS[0:0] = [
    (r"^intentar:$", lambda m: "try:"),
    (r"^si falla:$", lambda m: "except Exception as error:"),
    (r"^al final:$", lambda m: "finally:"),
    (r"^ver d[oó]lar\s+(\w+)\s+y guardar en\s+(\w+)$", lambda m: f"{m[2]} = dolar({m[1]!r})"),
    (r"^ver datos del pa[ií]s\s+(.+?)\s+y guardar en\s+(\w+)$", lambda m: f"{m[2]} = pais({_e(m[1])})"),
    (r"^crear gr[aá]fico\s+(.+?)\s+de\s+(barras|torta)\s+con etiquetas\s+(.+?)\s+y valores\s+(.+?)(?:\s+y t[ií]tulo\s+(.+))?$",
     lambda m: f"crear_grafico({_e(m[1])}, {_e(m[3])}, {_e(m[4])}, {_e(m[5]) if m[5] else repr('')}, {m[2]!r})"),
    (r"^crear collage\s+(.+?)\s+con fotos\s+(.+)$", lambda m: f"collage({_e(m[2])}, {_e(m[1])})"),
    (r"^crear p[aá]gina web\s+(.+?)\s+con t[ií]tulo\s+(.+?)(?:\s+y texto\s+(.+?))?(?:\s+y whatsapp\s+(.+?))?(?:\s+y color\s+(.+))?$",
     lambda m: f"crear_pagina_web({_e(m[1])}, {_e(m[2])}, {_e(m[3]) if m[3] else repr('')}, {_e(m[4]) if m[4] else repr('')}, {_e(m[5]) if m[5] else repr('plateado')})"),
    (r"^agregar m[uú]sica\s+(.+?)\s+al video\s+(.+?)(?:\s+y guardar como\s+(.+))?$",
     lambda m: f"agregar_musica({_e(m[2])}, {_e(m[1])}{', ' + _e(m[3]) if m[3] else ''})"),
    (r"^convertir video\s+(.+?)\s+en gif(?:\s+llamado\s+(.+))?$",
     lambda m: f"video_a_gif({_e(m[1])}{', ' + _e(m[2]) if m[2] else ''})"),
    (r"^recortar video\s+(.+?)\s+desde\s+(.+?)\s+hasta\s+(.+?)(?:\s+y guardar como\s+(.+))?$",
     lambda m: f"recortar_video({_e(m[1])}, {_e(m[2])}, {_e(m[3])}{', ' + _e(m[4]) if m[4] else ''})"),
    (r"^unir videos\s+(.+?)(?:\s+y guardar como\s+(.+))?$",
     lambda m: f"unir_videos({_e(m[1])}{', ' + _e(m[2]) if m[2] else ''})"),
    (r"^sacar audio de\s+(.+?)(?:\s+y guardar como\s+(.+))?$",
     lambda m: f"sacar_audio({_e(m[1])}{', ' + _e(m[2]) if m[2] else ''})"),
    (r"^ordenar la carpeta\s+(.+)$", lambda m: f"ordenar_carpeta({_e(m[1])})"),
    (r"^renombrar los archivos de\s+(.+?)\s+como\s+(.+)$", lambda m: f"renombrar_todos({_e(m[1])}, {_e(m[2])})"),
    (r"^achicar foto\s+(.+?)\s+a\s+(\d+)\s+de ancho$", lambda m: f"achicar_foto({_e(m[1])}, {m[2]})"),
    (r"^poner marca de agua\s+(.+?)\s+en\s+(.+)$", lambda m: f"marca_de_agua({_e(m[2])}, {_e(m[1])})"),
    (r"^pasar a blanco y negro\s+(.+)$", lambda m: f"blanco_y_negro({_e(m[1])})"),
    (r"^descargar\s+(.+?)\s+como\s+(.+)$", lambda m: f"descargar({_e(m[1])}, {_e(m[2])})"),
    (r"^decir\s+(.+)$", lambda m: f"hablar({_e(m[1])})"),
    (r"^mostrar men[uú]\s+(.+?)\s+con opciones\s+(.+?)\s+y guardar en\s+(\w+)$",
     lambda m: f"{m[3]} = menu({_e(m[1])}, {_e(m[2])})"),
    (r"^guardar datos\s+(.+?)\s+en\s+(.+)$", lambda m: f"guardar_datos({_e(m[2])}, {_e(m[1])})"),
    (r"^leer datos de\s+(.+?)\s+y guardar en\s+(\w+)$", lambda m: f"{m[2]} = leer_datos({_e(m[1])})"),
]


def traducir_linea(linea):
    sangria = linea[: len(linea) - len(linea.lstrip())]
    contenido = linea.strip()
    if not contenido:
        return ""
    if contenido.startswith("#"):
        return sangria + contenido
    for patron, armar in REGLAS:
        m = re.match(patron, contenido)
        if m:
            return sangria + armar(m)
    # Si no coincide ninguna regla, se intenta como expresión (por ejemplo, llamar a una función)
    return sangria + traducir_expresion(contenido)


def traducir(codigo):
    return "\n".join(traducir_linea(l) for l in codigo.splitlines())

# ---------------------------------------------------------------------------
# 3. Ejecutar y mostrar errores en español
# ---------------------------------------------------------------------------

ERRORES = {
    "NameError": "Usaste algo que no existe todavía",
    "SyntaxError": "Hay algo mal escrito",
    "IndentationError": "Revisá los espacios al principio de la línea",
    "ZeroDivisionError": "No se puede dividir por cero",
    "TypeError": "Estás mezclando tipos que no van juntos (por ejemplo, texto con número)",
    "ValueError": "Ese valor no sirve para lo que querés hacer",
    "IndexError": "Pediste una posición que la lista no tiene",
    "FileNotFoundError": "No encontré ese archivo",
    "URLError": "No pude conectarme a internet o a esa página",
    "RuntimeError": "Falta algo para hacer esto",
    "KeyError": "Ese dato no existe en la ficha",
}


def ejecutar(codigo, entorno=None, nombre="<programa>"):
    entorno = entorno if entorno is not None else dict(INCLUIDAS)
    python = traducir(codigo)
    try:
        exec(compile(python, nombre, "exec"), entorno)
    except Exception as e:
        tipo = type(e).__name__
        linea = getattr(e, "lineno", None)
        if linea is None:
            tb = e.__traceback__
            while tb is not None:
                if tb.tb_frame.f_code.co_filename == nombre:
                    linea = tb.tb_lineno
                tb = tb.tb_next
        lineas = codigo.splitlines()
        donde = f" en la línea {linea}: {lineas[linea - 1].strip()}" if linea and linea <= len(lineas) else ""
        print(f"💎 Error{donde}")
        if isinstance(e, (FaltaHerramienta, RuntimeError)):
            print(f"   {e}")
        else:
            print(f"   {ERRORES.get(tipo, 'Algo salió mal')}. ({e})")
        return False
    return True


def consola():
    print(f"💎 Diamante {VERSION} — escribí 'salir' para terminar.")
    entorno = dict(INCLUIDAS)
    bloque = []
    while True:
        try:
            linea = input("... " if bloque else "💎 ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not bloque and linea.strip() == "salir":
            break
        if bloque or linea.rstrip().endswith(":"):
            if linea.strip() == "":
                ejecutar("\n".join(bloque), entorno, "<consola>")
                bloque = []
            else:
                bloque.append(linea)
            continue
        ejecutar(linea, entorno, "<consola>")


def main(argv):
    if len(argv) == 1:
        consola()
    elif argv[1] == "--ver" and len(argv) == 3:
        with open(argv[2], encoding="utf-8") as f:
            print(traducir(f.read()))
    else:
        with open(argv[1], encoding="utf-8") as f:
            ok = ejecutar(f.read(), nombre=argv[1])
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(sys.argv)
