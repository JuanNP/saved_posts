import instaloader
import json
import csv
import os
import sys
import time
from getpass import getpass
from typing import Optional
from instaloader import BadCredentialsException, TwoFactorAuthRequiredException, ConnectionException, LoginRequiredException
from instaloader.exceptions import LoginException, BadResponseException
 

def fetch_saved_posts(user: str, password: Optional[str], max_posts: Optional[int] = None) -> str:
    """
    Inicia sesión con Instaloader (usando sesión en disco si existe) y obtiene publicaciones guardadas del propio usuario. Puedes limitar con 
    
    						`max_posts` (None = sin límite). Retorna un JSON con información relevante de cada una.

    NOTA IMPORTANTE: `user` debe ser tu *nombre de usuario* de Instagram, no el email.
    """
    L = instaloader.Instaloader(
        download_pictures=False,
        download_videos=False,
        download_video_thumbnails=False,
        save_metadata=False,
        quiet=False,
        max_connection_attempts=3,
    )
    L.context.user_agent = os.environ.get("IG_UA", "Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")

    # ——— Login con sesión persistente ———
    session_file = os.environ.get("IG_SESSIONFILE") or f"{user}.session"
    try:
        if os.path.exists(session_file):
            L.load_session_from_file(user, filename=session_file)
        else:
            # Primer intento: login clásico si hay contraseña
            try:
                if password:
                    L.login(user, password)
                else:
                    # Fuerza flujo interactivo si no hay password provista
                    raise LoginException("no password provided")
            except (LoginException, TwoFactorAuthRequiredException, BadCredentialsException):
                # Fallback robusto: maneja 2FA/challenge en modo interactivo
                L.interactive_login(user)
            # Guardar la sesión para usos futuros
            L.save_session_to_file(filename=session_file)
    except LoginException as e:
        print("[warn] Instagram rechazó el login (status: fail). Si acabas de iniciar desde un dispositivo nuevo, aprueba el acceso en instagram.com y vuelve a ejecutar. También puedes importar cookies del navegador y convertirlas a sesión con:\n  instaloader --load-cookies cookies.txt --sessionfile {}".format(session_file), file=sys.stderr)
        raise
    except BadCredentialsException:
        raise SystemExit("Credenciales incorrectas. Verifica que usas el NOMBRE DE USUARIO (no el email).")
    except ConnectionException as e:
        raise SystemExit(f"Error de red al iniciar sesión: {e}")

    # ——— Obtener publicaciones guardadas ———
    try:
        profile = instaloader.Profile.from_username(L.context, user)
        saved_posts = profile.get_saved_posts()
        sleep_s = float(os.environ.get("IG_SLEEP", "3"))

        posts_data = []

        def get_video_url_safe(p: instaloader.Post):
            """Devuelve la URL de video o None si el recurso ya no está disponible.

            Algunos posts guardados pueden haber sido eliminados/archivados por el autor
            o por Instagram. Acceder a `post.video_url` puede disparar un 400/`BadResponseException`.
            En ese caso devolvemos None para no abortar el procesamiento del resto.
            """
            if not p.is_video:
                return None
            try:
                return p.video_url
            except BadResponseException as e:
                # Mensajes típicos: "400 Bad Request when accessing …"
                print(f"[warn] Video no disponible para {getattr(p,'shortcode','?')}: {e}")
                return None
        for idx, post in enumerate(saved_posts):
            if isinstance(max_posts, int) and idx >= max_posts:
                break

            # Reintentos con backoff por post para manejar rate limit / fallos transitorios
            attempts = [0, 60, 120]  # en segundos
            success = False
            for wait in attempts:
                if wait:
                    print(f"[warn] Reintentando {post.shortcode} en {wait}s…")
                    time.sleep(wait)
                try:
                    owner_user = getattr(post, "owner_username", None)
                    if not owner_user:
                        # Evita llamada extra a post.owner_profile; usa owner_id como fallback ligero
                        owner_user = getattr(post, "owner_id", None)

                    row = {
                        "shortcode": post.shortcode,
                        "date_utc": post.date_utc.isoformat(),
                        "typename": post.typename,
                        # "caption": (post.caption or "").strip(),
                        "likes": post.likes,
                        "comments": post.comments,
                        "url": f"https://www.instagram.com/p/{post.shortcode}/",
                        "owner_username": owner_user,
                        "videos": post.is_video,
                        "video_url": get_video_url_safe(post),
                    }
                    posts_data.append(row)
                    success = True
                    break
                except (BadResponseException, ConnectionException) as e:
                    # Deja que el siguiente ciclo haga el backoff definido en 'attempts'
                    print(f"[warn] Error obteniendo metadata de {getattr(post,'shortcode','?')}: {e}")
                    continue
                except Exception as e:
                    print(f"[skip] Falló {getattr(post,'shortcode','?')}: {e}")
                    break

            if not success:
                print(f"[skip] Omitiendo post {getattr(post,'shortcode','?')} tras reintentos.")
                continue

            # Acelerador neutralizable por IG_SLEEP
            time.sleep(sleep_s)

        return json.dumps({"saved_posts": posts_data}, ensure_ascii=False, indent=2)
    except LoginRequiredException:
        raise SystemExit("No se pudo acceder a los guardados. Asegúrate de que la sesión está iniciada en tu cuenta.")
    except ConnectionException as e:
        raise SystemExit(f"Error de red durante la extracción: {e}")

# Ejemplo de uso
if __name__ == "__main__":
    # Usa variables de entorno para no hardcodear credenciales
    user = os.environ.get("IG_USERNAME") or input("Usuario de Instagram: ")
    password = os.environ.get("IG_PASSWORD")
    if not password and not os.path.exists(f"{user}.session"):
        password = getpass("Contraseña (solo la primera vez, para crear sesión): ")

    # Permite controlar cuántos posts traer vía IG_MAX (None = sin límite)
    max_env = os.environ.get("IG_MAX")
    try:
        max_posts = int(max_env) if max_env not in (None, "", "none", "None") else None
    except ValueError:
        max_posts = None

    # Ejecuta la extracción y guarda CSV en la ruta indicada por IG_CSV o por defecto
    result_json = fetch_saved_posts(user, password, max_posts=max_posts)
    payload = json.loads(result_json)
    rows = payload.get("saved_posts", [])

    # Define columnas y archivo de salida
    fieldnames = [
        "shortcode",
        "date_utc",
        "typename",
        # "caption",
        "likes",
        "comments",
        "url",
        "owner_username",
        "videos",
        "video_url",
    ]
    out_csv = os.environ.get("IG_CSV") or f"saved_posts_{user}.csv"

    # Escribe el CSV (utf-8-sig para compatibilidad con Excel)
    with open(out_csv, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"CSV guardado en {out_csv} con {len(rows)} filas.")