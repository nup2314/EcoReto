import os
from functools import wraps
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, abort)
from werkzeug.security import generate_password_hash, check_password_hash
from .db import consultar, ejecutar

bp = Blueprint("main", __name__)

CATEGORIAS = ["Reciclaje", "Agua", "Energía", "Transporte", "Reutilización"]


def login_required(vista):
    @wraps(vista)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            return redirect(url_for("main.login"))
        return vista(*args, **kwargs)
    return envoltura


def leer_formulario():
    """Lee y valida el formulario. Devuelve (datos, errores)."""
    f = request.form
    datos = {
        "titulo": f.get("titulo", "").strip(),
        "categoria": f.get("categoria", "").strip(),
        "descripcion": f.get("descripcion", "").strip(),
        "propuesto_por": f.get("propuesto_por", "").strip(),
        "fecha": f.get("fecha", "").strip(),
        "impacto": f.get("impacto", "").strip(),
    }
    errores = []
    if not datos["titulo"] or len(datos["titulo"]) > 80:
        errores.append("El título es obligatorio (máximo 80 caracteres).")
    if datos["categoria"] not in CATEGORIAS:
        errores.append("Elige una categoría válida.")
    if not datos["descripcion"]:
        errores.append("Escribe qué hiciste.")
    if not datos["propuesto_por"]:
        errores.append("Indica quién propone la acción.")
    if not datos["fecha"]:
        errores.append("Elige una fecha.")
    return datos, errores


# ---------- Acceso ----------
def usuario_valido(usuario, clave):
    """Acepta el usuario de Render (APP_USUARIO / APP_CLAVE) o uno registrado."""
    if (usuario == os.environ.get("APP_USUARIO", "estudiante")
            and clave == os.environ.get("APP_CLAVE", "ecoreto")):
        return True
    try:
        fila = consultar("SELECT clave_hash FROM usuarios WHERE usuario = %s",
                         (usuario,), uno=True)
    except Exception:
        return False
    return bool(fila) and check_password_hash(fila["clave_hash"], clave)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "")
        if usuario_valido(usuario, clave):
            session["usuario"] = usuario
            return redirect(url_for("main.index"))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("login.html")


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        usuario = request.form.get("usuario", "").strip()
        clave = request.form.get("clave", "")
        repetir = request.form.get("repetir", "")
        errores = []
        if not 3 <= len(usuario) <= 30:
            errores.append("El usuario debe tener entre 3 y 30 caracteres.")
        if len(clave) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres.")
        if clave != repetir:
            errores.append("Las contraseñas no coinciden.")
        if usuario == os.environ.get("APP_USUARIO", "estudiante"):
            errores.append("Ese usuario ya existe.")
        if not errores:
            try:
                existe = consultar("SELECT 1 FROM usuarios WHERE usuario = %s",
                                   (usuario,), uno=True)
                if existe:
                    errores.append("Ese usuario ya existe.")
                else:
                    ejecutar("INSERT INTO usuarios (usuario, clave_hash) "
                             "VALUES (%s, %s)",
                             (usuario, generate_password_hash(clave)))
            except Exception:
                errores.append("No se pudo crear la cuenta. Revisa que exista "
                               "la tabla usuarios en Neon.")
        if not errores:
            session["usuario"] = usuario
            flash("Cuenta creada. ¡Bienvenido!", "ok")
            return redirect(url_for("main.index"))
        for e in errores:
            flash(e, "error")
    return render_template("registro.html")


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("main.login"))


# ---------- Lista ----------
@bp.route("/")
@login_required
def index():
    q = request.args.get("q", "").strip()
    if q:
        patron = f"%{q}%"
        acciones = consultar(
            "SELECT id, titulo, categoria, descripcion, propuesto_por, fecha, impacto "
            "FROM acciones WHERE titulo ILIKE %s OR descripcion ILIKE %s "
            "ORDER BY id DESC", (patron, patron))
    else:
        acciones = consultar(
            "SELECT id, titulo, categoria, descripcion, propuesto_por, fecha, impacto "
            "FROM acciones ORDER BY id DESC")
    resumen = consultar(
        "SELECT COUNT(*) AS total, COUNT(DISTINCT categoria) AS categorias, "
        "COUNT(DISTINCT propuesto_por) AS personas FROM acciones", uno=True)
    return render_template("index.html", acciones=acciones, resumen=resumen, q=q)


# ---------- Crear ----------
@bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva():
    datos = {"categoria": CATEGORIAS[0], "propuesto_por": session["usuario"]}
    if request.method == "POST":
        datos, errores = leer_formulario()
        if not errores:
            ejecutar(
                "INSERT INTO acciones "
                "(titulo, categoria, descripcion, propuesto_por, fecha, impacto) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (datos["titulo"], datos["categoria"], datos["descripcion"],
                 datos["propuesto_por"], datos["fecha"], datos["impacto"]))
            flash("Acción guardada.", "ok")
            return redirect(url_for("main.index"))
        for e in errores:
            flash(e, "error")
    return render_template("formulario.html", accion=datos, categorias=CATEGORIAS,
                           modo="nueva")


# ---------- Detalle ----------
@bp.route("/accion/<int:id>")
@login_required
def detalle(id):
    accion = consultar("SELECT * FROM acciones WHERE id = %s", (id,), uno=True)
    if not accion:
        abort(404)
    return render_template("detalle.html", accion=accion)


# ---------- Editar ----------
@bp.route("/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar(id):
    accion = consultar("SELECT * FROM acciones WHERE id = %s", (id,), uno=True)
    if not accion:
        abort(404)
    if request.method == "POST":
        datos, errores = leer_formulario()
        if not errores:
            ejecutar(
                "UPDATE acciones SET titulo=%s, categoria=%s, descripcion=%s, "
                "propuesto_por=%s, fecha=%s, impacto=%s WHERE id=%s",
                (datos["titulo"], datos["categoria"], datos["descripcion"],
                 datos["propuesto_por"], datos["fecha"], datos["impacto"], id))
            flash("Cambios guardados.", "ok")
            return redirect(url_for("main.detalle", id=id))
        for e in errores:
            flash(e, "error")
        accion = {**datos, "id": id}
    return render_template("formulario.html", accion=accion, categorias=CATEGORIAS,
                           modo="editar")


# ---------- Eliminar ----------
@bp.route("/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar(id):
    ejecutar("DELETE FROM acciones WHERE id = %s", (id,))
    flash("Acción eliminada.", "ok")
    return redirect(url_for("main.index"))


# ---------- Estadísticas ----------
@bp.route("/estadisticas")
@login_required
def estadisticas():
    por_categoria = consultar(
        "SELECT categoria, COUNT(*) AS total FROM acciones "
        "GROUP BY categoria ORDER BY total DESC, categoria")
    por_persona = consultar(
        "SELECT propuesto_por, COUNT(*) AS total FROM acciones "
        "GROUP BY propuesto_por ORDER BY total DESC, propuesto_por LIMIT 5")
    maximo = max([c["total"] for c in por_categoria], default=1)
    return render_template("estadisticas.html", por_categoria=por_categoria,
                           por_persona=por_persona, maximo=maximo)
