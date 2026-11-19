"""
Superpoderes extra de Diamante 💎 (versión 0.3).
Todo funciona con herramientas gratuitas y legales.
"""

import datetime
import glob
import json
import math
import os
import random
import re
import secrets
import shutil
import statistics
import string
import subprocess
import urllib.request

# ---------------------------------------------------------------------------
# Matemática
# ---------------------------------------------------------------------------

def promedio(lista):
    return statistics.mean(lista)


def mediana(lista):
    return statistics.median(lista)


def porcentaje(parte, total):
    return round(parte * 100 / total, 2)


def calcular_porcentaje(porc, de):
    return de * porc / 100


def ordenar(lista, al_reves=False):
    return sorted(lista, reverse=al_reves)


def invertir(cosa):
    return cosa[::-1]


def mezclar(lista):
    copia = list(lista)
    random.shuffle(copia)
    return copia


def sin_repetidos(lista):
    vistos, salida = set(), []
    for x in lista:
        clave = json.dumps(x, sort_keys=True, default=str)
        if clave not in vistos:
            vistos.add(clave)
            salida.append(x)
    return salida


def es_par(n):
    return n % 2 == 0


def es_primo(n):
    if n < 2:
        return False
    for i in range(2, int(math.isqrt(n)) + 1):
        if n % i == 0:
            return False
    return True


MATEMATICA = {
    "raiz": math.sqrt, "potencia": pow, "absoluto": abs, "pi": math.pi,
    "piso": math.floor, "techo": math.ceil, "promedio": promedio, "mediana": mediana,
    "porcentaje": porcentaje, "calcular_porcentaje": calcular_porcentaje,
    "ordenar": ordenar, "invertir": invertir, "mezclar": mezclar, "sin_repetidos": sin_repetidos,
    "es_par": es_par, "es_primo": es_primo, "contar": lambda lista, x: lista.count(x),
    "posicion": lambda lista, x: lista.index(x) + 1 if x in lista else 0,
    "primero": lambda lista: lista[0] if lista else None,
    "ultimo": lambda lista: lista[-1] if lista else None,
}

# ---------------------------------------------------------------------------
# Texto
# ---------------------------------------------------------------------------

def contar_palabras(t):
    return len(str(t).split())


def capitalizar(t):
    return str(t).title()


def quitar_acentos(t):
    import unicodedata
    return "".join(c for c in unicodedata.normalize("NFD", str(t)) if unicodedata.category(c) != "Mn")


def es_numero(t):
    try:
        float(str(t).replace(",", "."))
        return True
    except ValueError:
        return False


def buscar_numeros(t):
    return [float(x.replace(",", ".")) if ("." in x or "," in x) else int(x)
            for x in re.findall(r"-?\d+(?:[.,]\d+)?", str(t))]


def generar_contrasena(largo_=12):
    caracteres = string.ascii_letters + string.digits + "!@#$%&*?"
    while True:
        c = "".join(secrets.choice(caracteres) for _ in range(int(largo_)))
        if any(x.isdigit() for x in c) and any(x.isupper() for x in c) and any(x.islower() for x in c):
            return c


def formato_plata(n, moneda="$"):
    entero, _, dec = f"{float(n):,.2f}".partition(".")
    entero = entero.replace(",", ".")
    return f"{moneda}{entero}" + ("" if dec == "00" else f",{dec}")


TEXTO = {
    "contar_palabras": contar_palabras, "capitalizar": capitalizar, "quitar_acentos": quitar_acentos,
    "empieza_con": lambda t, p: str(t).startswith(str(p)),
    "termina_con": lambda t, p: str(t).endswith(str(p)),
    "recortar": lambda t: str(t).strip(), "repetir_texto": lambda t, n: str(t) * int(n),
    "es_numero": es_numero, "buscar_numeros": buscar_numeros,
    "generar_contraseña": generar_contrasena, "generar_contrasena": generar_contrasena,
    "formato_plata": formato_plata,
}

# ---------------------------------------------------------------------------
# Fechas
# ---------------------------------------------------------------------------

DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto",
         "septiembre", "octubre", "noviembre", "diciembre"]


def _fecha(f):
    if isinstance(f, datetime.date):
        return f
    d, m, a = [int(x) for x in re.split(r"[/-]", str(f))]
    return datetime.date(a, m, d)


def dias_entre(a, b):
    return abs((_fecha(b) - _fecha(a)).days)


def sumar_dias(fecha, n):
    return (_fecha(fecha) + datetime.timedelta(days=int(n))).strftime("%d/%m/%Y")


def dia_de_la_semana(fecha=None):
    return DIAS[(_fecha(fecha) if fecha else datetime.date.today()).weekday()]


def fecha_larga(fecha=None):
    f = _fecha(fecha) if fecha else datetime.date.today()
    return f"{DIAS[f.weekday()]} {f.day} de {MESES[f.month - 1]} de {f.year}"


def edad(nacimiento):
    n, h = _fecha(nacimiento), datetime.date.today()
    return h.year - n.year - ((h.month, h.day) < (n.month, n.day))


def dias_hasta(fecha):
    return (_fecha(fecha) - datetime.date.today()).days


FECHAS = {
    "dias_entre": dias_entre, "sumar_dias": sumar_dias, "dia_de_la_semana": dia_de_la_semana,
    "fecha_larga": fecha_larga, "edad": edad, "dias_hasta": dias_hasta,
    "año": lambda: datetime.date.today().year, "mes": lambda: MESES[datetime.date.today().month - 1],
}

# ---------------------------------------------------------------------------
# Archivos y carpetas
# ---------------------------------------------------------------------------

def listar_archivos(carpeta=".", tipo="*"):
    patron = os.path.join(carpeta, tipo if "." in tipo or tipo == "*" else f"*.{tipo}")
    return sorted(os.path.basename(p) for p in glob.glob(patron) if os.path.isfile(p))


def crear_carpeta(nombre):
    os.makedirs(nombre, exist_ok=True)
    return nombre


def copiar(origen, destino):
    shutil.copy2(origen, destino)
    return destino


def mover(origen, destino):
    shutil.move(origen, destino)
    return destino


def existe(ruta):
    return os.path.exists(ruta)


def ordenar_carpeta(carpeta="."):
    """Ordena los archivos de una carpeta en subcarpetas por tipo (Imágenes, Videos, Documentos...)."""
    grupos = {
        "Imágenes": {"jpg", "jpeg", "png", "gif", "webp", "bmp"},
        "Videos": {"mp4", "mov", "avi", "mkv", "webm"},
        "Música": {"mp3", "wav", "ogg", "m4a"},
        "Documentos": {"pdf", "doc", "docx", "txt", "xls", "xlsx", "csv", "ppt", "pptx"},
        "Comprimidos": {"zip", "rar", "7z"},
    }
    movidos = 0
    for nombre in os.listdir(carpeta):
        ruta = os.path.join(carpeta, nombre)
        if not os.path.isfile(ruta):
            continue
        ext = nombre.rsplit(".", 1)[-1].lower() if "." in nombre else ""
        for grupo, extensiones in grupos.items():
            if ext in extensiones:
                os.makedirs(os.path.join(carpeta, grupo), exist_ok=True)
                shutil.move(ruta, os.path.join(carpeta, grupo, nombre))
                movidos += 1
                break
    print(f"🗂️  Ordené {movidos} archivos")
    return movidos


def renombrar_todos(carpeta, prefijo, tipo="*"):
    archivos = listar_archivos(carpeta, tipo)
    for i, nombre in enumerate(archivos, 1):
        ext = os.path.splitext(nombre)[1]
        os.rename(os.path.join(carpeta, nombre), os.path.join(carpeta, f"{prefijo}_{i:03d}{ext}"))
    print(f"✏️  Renombré {len(archivos)} archivos")
    return len(archivos)


def guardar_datos(archivo, datos):
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    return archivo


def leer_datos(archivo):
    with open(archivo, encoding="utf-8") as f:
        return json.load(f)


ARCHIVOS = {
    "listar_archivos": listar_archivos, "crear_carpeta": crear_carpeta, "copiar": copiar,
    "mover": mover, "existe": existe, "ordenar_carpeta": ordenar_carpeta,
    "renombrar_todos": renombrar_todos, "guardar_datos": guardar_datos, "leer_datos": leer_datos,
}

# ---------------------------------------------------------------------------
# Fotos y diseño (con Pillow, gratis)
# ---------------------------------------------------------------------------

def _pil():
    try:
        from PIL import Image  # noqa: F401
    except ImportError:
        raise RuntimeError("Para fotos instalá la herramienta gratuita:  pip install pillow")
    from PIL import Image, ImageDraw, ImageFilter, ImageOps
    return Image, ImageDraw, ImageFilter, ImageOps


def achicar_foto(archivo, ancho, salida=None):
    Image, *_ = _pil()
    img = Image.open(archivo)
    alto = int(img.height * ancho / img.width)
    salida = salida or archivo
    img.resize((int(ancho), alto)).save(salida)
    return salida


def convertir_foto(archivo, formato):
    Image, *_ = _pil()
    salida = os.path.splitext(archivo)[0] + "." + formato.lower().strip(".")
    img = Image.open(archivo)
    if formato.lower() in ("jpg", "jpeg"):
        img = img.convert("RGB")
    img.save(salida)
    return salida


def blanco_y_negro(archivo, salida=None):
    Image, _, _, ImageOps = _pil()
    salida = salida or archivo
    ImageOps.grayscale(Image.open(archivo)).save(salida)
    return salida


def recortar_cuadrado(archivo, salida=None):
    Image, _, _, ImageOps = _pil()
    img = Image.open(archivo)
    lado = min(img.size)
    salida = salida or archivo
    ImageOps.fit(img, (lado, lado)).save(salida)
    return salida


def desenfocar(archivo, cuanto=5, salida=None):
    Image, _, ImageFilter, _ = _pil()
    salida = salida or archivo
    Image.open(archivo).filter(ImageFilter.GaussianBlur(cuanto)).save(salida)
    return salida


def girar_foto(archivo, grados=90, salida=None):
    Image, *_ = _pil()
    salida = salida or archivo
    Image.open(archivo).rotate(-grados, expand=True).save(salida)
    return salida


def marca_de_agua(archivo, texto, salida=None):
    Image, ImageDraw, _, _ = _pil()
    from diamante import _fuente
    img = Image.open(archivo).convert("RGBA")
    capa = Image.new("RGBA", img.size, (0, 0, 0, 0))
    dibujo = ImageDraw.Draw(capa)
    tamano = max(16, img.width // 25)
    fuente = _fuente(tamano)
    ancho_texto = dibujo.textlength(str(texto), font=fuente)
    dibujo.text((img.width - ancho_texto - 20, img.height - tamano - 20), str(texto),
                fill=(255, 255, 255, 170), font=fuente)
    salida = salida or archivo
    Image.alpha_composite(img, capa).convert("RGB").save(salida)
    return salida


def collage(archivos, salida="collage.png", columnas=2, lado=540):
    Image, _, _, ImageOps = _pil()
    filas = math.ceil(len(archivos) / columnas)
    lienzo = Image.new("RGB", (columnas * lado, filas * lado), "white")
    for i, a in enumerate(archivos):
        foto = ImageOps.pad(Image.open(a).convert("RGB"), (lado, lado), color="white")
        lienzo.paste(foto, ((i % columnas) * lado, (i // columnas) * lado))
    lienzo.save(salida)
    print(f"🧩 Collage creado: {salida}")
    return salida


def crear_grafico(archivo, etiquetas, valores, titulo="", tipo="barras"):
    """Gráfico de barras o de torta, dibujado sin herramientas pagas."""
    Image, ImageDraw, _, _ = _pil()
    from diamante import _fuente, COLORES
    paleta = ["#1E5BD8", "#E53935", "#2E9E5B", "#FB8C00", "#8E44AD", "#00ACC1", "#F06292", "#795548"]
    ancho, alto = 1200, 800
    img = Image.new("RGB", (ancho, alto), "white")
    d = ImageDraw.Draw(img)
    f, ft = _fuente(26), _fuente(44)
    if titulo:
        d.text(((ancho - d.textlength(str(titulo), font=ft)) / 2, 30), str(titulo), fill="#222", font=ft)
    if tipo == "torta":
        total = sum(valores) or 1
        caja = (120, 140, 640, 660)
        inicio = -90
        for i, v in enumerate(valores):
            fin = inicio + 360 * v / total
            d.pieslice(caja, inicio, fin, fill=paleta[i % len(paleta)])
            inicio = fin
        for i, (e, v) in enumerate(zip(etiquetas, valores)):
            y = 220 + i * 50
            d.rectangle((720, y, 752, y + 32), fill=paleta[i % len(paleta)])
            d.text((770, y), f"{e}: {round(v * 100 / total)}%", fill="#222", font=f)
    else:
        izq, abajo, arriba = 120, alto - 100, 140
        maximo = max(valores) or 1
        espacio = (ancho - izq - 60) / len(valores)
        d.line((izq, arriba, izq, abajo), fill="#999", width=2)
        d.line((izq, abajo, ancho - 40, abajo), fill="#999", width=2)
        for i, (e, v) in enumerate(zip(etiquetas, valores)):
            x0 = izq + i * espacio + espacio * 0.15
            x1 = izq + (i + 1) * espacio - espacio * 0.15
            y0 = abajo - (abajo - arriba) * v / maximo
            d.rectangle((x0, y0, x1, abajo), fill=paleta[i % len(paleta)])
            etiqueta_v = str(int(v) if float(v).is_integer() else v)
            d.text(((x0 + x1) / 2 - d.textlength(etiqueta_v, font=f) / 2, y0 - 36), etiqueta_v, fill="#222", font=f)
            d.text(((x0 + x1) / 2 - d.textlength(str(e), font=f) / 2, abajo + 12), str(e), fill="#222", font=f)
    img.save(archivo)
    print(f"📈 Gráfico creado: {archivo}")
    return archivo


FOTOS = {
    "achicar_foto": achicar_foto, "convertir_foto": convertir_foto, "blanco_y_negro": blanco_y_negro,
    "recortar_cuadrado": recortar_cuadrado, "desenfocar": desenfocar, "girar_foto": girar_foto,
    "marca_de_agua": marca_de_agua, "collage": collage, "crear_grafico": crear_grafico,
}

# ---------------------------------------------------------------------------
# Video y audio (con ffmpeg, gratis)
# ---------------------------------------------------------------------------

def _ffmpeg():
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ruta = shutil.which("ffmpeg")
        if not ruta:
            raise RuntimeError("Para video y audio instalá la herramienta gratuita:  pip install imageio-ffmpeg")
        return ruta


def _correr(*args):
    subprocess.run([_ffmpeg(), "-y", "-loglevel", "error", *args], check=True)


def agregar_musica(video, musica, salida="video_con_musica.mp4"):
    _correr("-i", video, "-i", musica, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-shortest", salida)
    print(f"🎵 Video con música: {salida}")
    return salida


def recortar_video(video, desde, hasta, salida="recorte.mp4"):
    _correr("-i", video, "-ss", str(desde), "-to", str(hasta), "-c:v", "libx264", "-preset", "veryfast", salida)
    print(f"✂️  Video recortado: {salida}")
    return salida


def video_a_gif(video, salida="animacion.gif", ancho=480):
    _correr("-i", video, "-vf", f"fps=12,scale={int(ancho)}:-1:flags=lanczos", salida)
    print(f"🎞️  GIF creado: {salida}")
    return salida


def sacar_audio(video, salida="audio.mp3"):
    _correr("-i", video, "-vn", "-q:a", "2", salida)
    print(f"🎧 Audio extraído: {salida}")
    return salida


def convertir_audio(archivo, formato="mp3"):
    salida = os.path.splitext(archivo)[0] + "." + formato
    _correr("-i", archivo, salida)
    return salida


def foto_de_video(video, segundo=1, salida="captura.png"):
    _correr("-ss", str(segundo), "-i", video, "-frames:v", "1", salida)
    return salida


def unir_videos(videos, salida="video_unido.mp4"):
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as l:
        for v in videos:
            l.write("file '" + os.path.abspath(v).replace("\\", "/").replace("'", "'\\''") + "'\n")
    _correr("-f", "concat", "-safe", "0", "-i", l.name, "-c:v", "libx264", "-preset", "veryfast", salida)
    os.unlink(l.name)
    print(f"🎬 Videos unidos: {salida}")
    return salida


VIDEO = {
    "agregar_musica": agregar_musica, "recortar_video": recortar_video, "video_a_gif": video_a_gif,
    "sacar_audio": sacar_audio, "convertir_audio": convertir_audio, "foto_de_video": foto_de_video,
    "unir_videos": unir_videos,
}

# ---------------------------------------------------------------------------
# Internet (servicios gratuitos, sin registrarse)
# ---------------------------------------------------------------------------

def _json(url):
    pedido = urllib.request.Request(url, headers={"User-Agent": "Diamante/0.3"})
    with urllib.request.urlopen(pedido, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def dolar(tipo="blue"):
    """Cotización del dólar en Argentina (dolarapi.com, gratis)."""
    d = _json(f"https://dolarapi.com/v1/dolares/{tipo}")
    return {"compra": d.get("compra"), "venta": d.get("venta")}


def descargar(url, archivo):
    pedido = urllib.request.Request(url, headers={"User-Agent": "Diamante/0.3"})
    with urllib.request.urlopen(pedido, timeout=60) as r, open(archivo, "wb") as f:
        shutil.copyfileobj(r, f)
    print(f"⬇️  Descargado: {archivo}")
    return archivo


def pais(nombre):
    """Datos de un país (restcountries.com, gratis)."""
    d = _json("https://restcountries.com/v3.1/name/" + urllib.request.quote(str(nombre)))[0]
    return {
        "nombre": d.get("translations", {}).get("spa", {}).get("common", d["name"]["common"]),
        "capital": (d.get("capital") or [""])[0],
        "poblacion": d.get("population"),
        "moneda": ", ".join(d.get("currencies", {}).keys()),
    }


def crear_pagina_web(archivo, titulo, texto="", whatsapp="", color="plateado"):
    """Crea una página web simple lista para subir a internet."""
    from diamante import COLORES
    c = COLORES.get(str(color).lower(), color)
    boton = ""
    if whatsapp:
        numero = re.sub(r"\D", "", str(whatsapp))
        boton = f'<a class="wa" href="https://wa.me/{numero}">Escribinos por WhatsApp</a>'
    html = f"""<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>{titulo}</title>
<style>body{{margin:0;font-family:system-ui,sans-serif;background:#fafafa;color:#222}}
header{{background:{c};padding:64px 20px;text-align:center}}h1{{margin:0;font-size:2.4rem}}
main{{max-width:680px;margin:32px auto;padding:0 20px;font-size:1.15rem;line-height:1.6}}
.wa{{display:inline-block;margin-top:24px;background:#25D366;color:#fff;padding:14px 26px;
border-radius:30px;text-decoration:none;font-weight:700}}</style></head>
<body><header><h1>{titulo}</h1></header><main><p>{texto}</p>{boton}</main></body></html>"""
    with open(archivo, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"🌐 Página web creada: {archivo}")
    return archivo


INTERNET = {"dolar": dolar, "descargar": descargar, "pais": pais, "crear_pagina_web": crear_pagina_web}

# ---------------------------------------------------------------------------
# Voz y menú
# ---------------------------------------------------------------------------

def hablar(texto):
    try:
        import pyttsx3
    except ImportError:
        print(f"🔊 (instalá 'pip install pyttsx3' para escuchar la voz) {texto}")
        return
    motor = pyttsx3.init()
    motor.say(str(texto))
    motor.runAndWait()


def menu(titulo, opciones):
    print(f"\n{titulo}")
    for i, o in enumerate(opciones, 1):
        print(f"  {i}. {o}")
    while True:
        r = input("Elegí un número: ").strip()
        if r.isdigit() and 1 <= int(r) <= len(opciones):
            return opciones[int(r) - 1]
        print("Ese número no está en la lista, probá de nuevo.")


OTROS = {"hablar": hablar, "menu": menu}

TODO = {}
for grupo in (MATEMATICA, TEXTO, FECHAS, ARCHIVOS, FOTOS, VIDEO, INTERNET, OTROS):
    TODO.update(grupo)
