# Saved Posts - Extractor de Posts Guardados de Instagram

Herramienta en Python para extraer y exportar tus posts guardados de Instagram a un archivo CSV. Utiliza la biblioteca `instaloader` para acceder a la API de Instagram de forma segura.

## 📋 Descripción

Este script te permite:

- Extraer todos tus posts guardados de Instagram
- Exportar la información a un archivo CSV
- Guardar la sesión para evitar iniciar sesión repetidamente
- Limitar la cantidad de posts a extraer
- Manejar errores y reintentos automáticos

## 🔧 Requisitos

- Python 3.9 o superior
- `instaloader` (se instalará automáticamente con pipenv)
- Cuenta de Instagram válida

## 📦 Instalación

### Opción 1: Usando Pipenv (Recomendado)

```bash
# Instalar pipenv si no lo tienes
pip install pipenv

# Instalar dependencias
pipenv install instaloader

# Activar el entorno virtual
pipenv shell
```

### Opción 2: Usando pip

```bash
# Instalar instaloader directamente
pip install instaloader
```

## 🚀 Uso

### Uso Básico

Ejecuta el script y sigue las instrucciones:

```bash
python saved_posts.py
```

El script te pedirá:

1. Tu nombre de usuario de Instagram (no el email)
2. Tu contraseña (solo la primera vez, para crear la sesión)

### Uso con Variables de Entorno

Puedes configurar el script usando variables de entorno para evitar ingresar credenciales cada vez:

```bash
# Configurar usuario
export IG_USERNAME="tu_usuario"

# Configurar contraseña (opcional, solo si no existe sesión)
export IG_PASSWORD="tu_contraseña"

# Limitar cantidad de posts (opcional)
export IG_MAX=100

# Personalizar nombre del archivo CSV (opcional)
export IG_CSV="mis_posts_guardados.csv"

# Personalizar archivo de sesión (opcional)
export IG_SESSIONFILE="mi_sesion.session"

# Personalizar tiempo de espera entre requests (opcional, default: 3 segundos)
export IG_SLEEP=5

# Solo extraer posts con videos/reels (opcional)
export IG_VIDEOS_ONLY=1

# Personalizar User-Agent (opcional)
export IG_UA="Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15"

# Ejecutar el script
python saved_posts.py
```

### Ejemplo Completo

```bash
# Primera ejecución (crea la sesión)
export IG_USERNAME="mi_usuario"
export IG_PASSWORD="mi_contraseña"
python saved_posts.py

# Ejecuciones posteriores (usa la sesión guardada)
export IG_USERNAME="mi_usuario"
python saved_posts.py

# Extraer solo los primeros 50 posts
export IG_USERNAME="mi_usuario"
export IG_MAX=50
python saved_posts.py

# Extraer solo posts con videos (reels)
export IG_USERNAME="mi_usuario"
export IG_VIDEOS_ONLY=1
python saved_posts.py

# Extraer solo los primeros 30 videos guardados
export IG_USERNAME="mi_usuario"
export IG_VIDEOS_ONLY=1
export IG_MAX=30
python saved_posts.py
```

## 📊 Formato del CSV

El archivo CSV generado contiene las siguientes columnas:

- `shortcode`: Código único del post
- `date_utc`: Fecha y hora en formato ISO (UTC)
- `typename`: Tipo de contenido (GraphVideo, GraphSidecar, GraphImage)
- `likes`: Número de likes
- `comments`: Número de comentarios
- `url`: URL completa del post
- `owner_username`: Nombre de usuario del autor
- `videos`: `True` si es un video, `False` si no
- `video_url`: URL del video (solo si es video)

## 🔐 Seguridad y Sesiones

El script guarda tu sesión de Instagram en un archivo `{usuario}.session` para evitar tener que iniciar sesión cada vez. Este archivo contiene información de autenticación, así que:

- **NO compartas** el archivo `.session`
- **NO subas** el archivo `.session` a repositorios públicos
- Agrega `*.session` a tu `.gitignore`

### Autenticación de Dos Factores (2FA)

Si tu cuenta tiene 2FA habilitado, el script usará el modo interactivo para completar la autenticación.

## ⚙️ Variables de Entorno

| Variable         | Descripción                           | Valor por Defecto                                    |
| ---------------- | ------------------------------------- | ---------------------------------------------------- |
| `IG_USERNAME`    | Nombre de usuario de Instagram        | Se solicita interactivamente                         |
| `IG_PASSWORD`    | Contraseña de Instagram               | Se solicita interactivamente (solo si no hay sesión) |
| `IG_MAX`         | Límite de posts a extraer             | `None` (sin límite)                                  |
| `IG_VIDEOS_ONLY` | Solo extraer posts con videos (reels) | `false` (extrae todos los posts)                     |
| `IG_CSV`         | Nombre del archivo CSV de salida      | `saved_posts_{usuario}.csv`                          |
| `IG_SESSIONFILE` | Nombre del archivo de sesión          | `{usuario}.session`                                  |
| `IG_SLEEP`       | Segundos de espera entre requests     | `3`                                                  |
| `IG_UA`          | User-Agent personalizado              | User-Agent de iPhone por defecto                     |

## 📁 Estructura del Proyecto

```
saved_posts/
├── saved_posts.py              # Script principal
├── Pipfile                     # Configuración de Pipenv
├── README.md                   # Este archivo
├── {usuario}.session           # Archivo de sesión (generado)
└── saved_posts_{usuario}.csv   # Archivo CSV de salida (generado)
```

## 🛠️ Solución de Problemas

### Error: "Instagram rechazó el login"

Si ves este error, puede ser porque:

- Has iniciado sesión desde un dispositivo nuevo
- Instagram requiere verificación adicional

**Solución:**

1. Ve a instagram.com y aprueba el acceso desde tu navegador
2. Vuelve a ejecutar el script
3. Alternativamente, puedes importar cookies del navegador:
   ```bash
   instaloader --load-cookies cookies.txt --sessionfile {usuario}.session
   ```

### Error: "Credenciales incorrectas"

- Asegúrate de usar tu **nombre de usuario** (no el email)
- Verifica que la contraseña sea correcta
- Si tienes 2FA, el script debería manejarlo automáticamente

### Error: "No se pudo acceder a los guardados"

- Verifica que la sesión esté activa
- Elimina el archivo `.session` y vuelve a iniciar sesión
- Asegúrate de tener posts guardados en tu cuenta

### Rate Limiting

Si Instagram limita tus requests:

- Aumenta el valor de `IG_SLEEP` (ej: `export IG_SLEEP=10`)
- Espera unos minutos antes de volver a ejecutar
- El script tiene reintentos automáticos con backoff

### Posts eliminados o no disponibles

Algunos posts guardados pueden haber sido eliminados por el autor. El script maneja esto automáticamente y continúa con el siguiente post.

## 📝 Notas Importantes

- ⚠️ **Usa tu nombre de usuario, no tu email** para iniciar sesión
- ⚠️ El script respeta los límites de rate de Instagram con pausas entre requests
- ⚠️ Los archivos de sesión son sensibles, no los compartas
- ⚠️ El script no descarga imágenes ni videos, solo extrae metadatos y URLs

## 🔄 Actualización de Dependencias

Para actualizar `instaloader`:

```bash
pipenv update instaloader
# o
pip install --upgrade instaloader
```

## 📄 Licencia

Este proyecto es de código abierto. Úsalo responsablemente y respeta los términos de servicio de Instagram.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

---

**Nota:** Este script es para uso personal. Asegúrate de cumplir con los términos de servicio de Instagram al usarlo.
