"""
Archivo de configuración principal del proyecto Django.
Contiene todos los ajustes globales del proyecto.
"""

from pathlib import Path
import os

# Es la ruta raiz del proyecto. Se usa para construir rutas internas como la base de datos o la carpeta media de forma dinámica, sin depender del sistema operativo o ubicación
BASE_DIR = Path(__file__).resolve().parent.parent


#  Configuración de seguridad y entorno
SECRET_KEY = 'django-insecure-@b5b(60bx*nxdzd(q6jjyts*%svqvofge2n4(&vcwr6j_c^q48'
# <-- Clave secreta de Django. En producción NO debe publicarse.

DEBUG = True
# <-- Modo de depuración. True para desarrollo, False en producción.

ALLOWED_HOSTS = []
# <-- Lista de dominios que pueden acceder al servidor.
#    Vacío significa solo localhost (modo desarrollo).


#  Aplicaciones instaladas en el proyecto
INSTALLED_APPS = [
    # Apps internas de Django (funcionalidades principales)
    'django.contrib.admin',       # Panel administrador
    'django.contrib.auth',        # Sistema de autenticación/usuarios
    'django.contrib.contenttypes',# Manejo de tipos de contenido
    'django.contrib.sessions',    # Manejo de sesiones
    'django.contrib.messages',    # Sistema de mensajes
    'django.contrib.staticfiles', # Manejo archivos estáticos (CSS/JS/img)

    # Apps creadas por nosotros
    'core',       # App principal del proyecto (inventario, productos, vistas)
    'bitacora',   # App para controlar bitácora / movimientos
    'users',      # App para el sistema de usuarios personalizado

    # Librerías externas
    'crispy_forms',       # Mejora los formularios Django
    'crispy_bootstrap5',  # Template de Bootstrap 5 para Crispy Forms

    'rest_framework',
]


#  Middleware (Procesos intermedios que interceptan solicitudes HTTP)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware', # Seguridad
    'django.contrib.sessions.middleware.SessionMiddleware', # Sesiones
    'django.middleware.common.CommonMiddleware', # Funciones comunes
    'django.middleware.csrf.CsrfViewMiddleware', # Protección CSRF formularios
    'django.contrib.auth.middleware.AuthenticationMiddleware', # Usuarios login
    'django.contrib.messages.middleware.MessageMiddleware', # Mensajes
    'django.middleware.clickjacking.XFrameOptionsMiddleware', # Protege contra clickjacking
]

# Indica cuál archivo controla las rutas (urls.py)
ROOT_URLCONF = 'superproyectofab.urls'


#  Configuración de plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],  # Rutas adicionales para templates. Vacío porque usamos /templates dentro apps
        'APP_DIRS': True,  # Permite detectar templates en cada app automáticamente
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug', # Info debug
                'django.template.context_processors.request', # Acceso a request en templates
                'django.contrib.auth.context_processors.auth', # Info del usuario logueado
                'django.contrib.messages.context_processors.messages', # Mensajes en templates
            ],
        },
    },
]

# Archivo WSGI para desplegar en servidores web
WSGI_APPLICATION = 'superproyectofab.wsgi.application'


#  Base de datos usada en el proyecto
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Usamos SQLite (local, desarrollo)
        'NAME': BASE_DIR / 'db.sqlite3', # Archivo de base de datos
    }
}


#  Validación de contraseñas (buenas prácticas de seguridad)
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]


#  Configuración de idioma y zona horaria
LANGUAGE_CODE = 'es-es'  # Idioma español
TIME_ZONE = 'America/santiago' # Zona horaria Chile
USE_I18N = True  # Internacionalización habilitada
USE_TZ = True    # Uso de zona horaria real


#  Archivos estáticos (CSS, imágenes, JS)
STATIC_URL = 'static/'


#  Tipo por defecto para IDs en modelos (BigInt = más grande)
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


#  Archivos multimedia (fotos subidas por usuarios)
MEDIA_URL = '/media/'  # URL pública para acceder
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') # Carpeta donde se guardan


#  Redirecciones después de login/logout
LOGIN_REDIRECT_URL = 'product'  # Después de iniciar sesión → página de productos
LOGOUT_REDIRECT_URL = 'home'    # Después de cerrar sesión → página home


#  Configuración de formularios Crispy + Bootstrap 5
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
