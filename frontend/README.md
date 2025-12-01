# Frontend 

## 0. Requisitos

Instalar [Node.js](https://nodejs.org/) y [npm](https://www.npmjs.com/).

### 0.1. Instalación de dependencias

Ejecutar el siguiente comando en la terminal para instalar las dependencias del proyecto:

```bash
    npm install
``` 

### 0.2. Ejecutar el servidor de desarrollo

Ejecutar el siguiente comando en la terminal para iniciar el servidor de desarrollo:

```bash
    npm run dev
```

### 1. Requerimientos 

- Crear un sistema de inicio de sesión con roles de usuario (administrador y candidatos).
- Los administradores podrán:
    - Crear nuevas entrevistas
    - Ver una lista de entrevistas con metadatos (fecha, hora, candidato, estado)
    - Descargar transcripciones y evaluaciones.

- Los candidatos podrán:
    - Ver sus entrevistas programadas
    - Unirse a la entrevista a través de un enlace
    - Ver la transcripción en tiempo real durante la entrevista.

- Páginas principales:
    1. Página de inicio de sesión
    2. Dashboard administrador
        - Tabla con:
            - Nombre del candidato.
            - Fecha y hora de la entrevista.
            - Transcripción.
            - Calificación.
    3. Panel de candidato
    4. Página formulario antes de iniciar la entrevista.
    5. Página de entrevista en vivo (Chat): 
        - Graba la sesión
        - Temporizador de la entrevista
        - Transcribe las respuestas 
        - Provee una evaluación automática.

### 2. Tecnologías seleccionada

- React.js para la construcción de la interfaz de usuario.
- Next.js para el enrutamiento y la renderización del lado del servidor.
- Tailwind CSS para el diseño y la estilización.

### 3. Estructura del proyecto

- `src/`: Código fuente de la aplicación.
    - `app/`: Configuración global y layout de la aplicación.
        - `(app)/`: Contiene las páginas principales de la aplicación.
        - `(auth)/`: Contiene las páginas de autenticación (login, registro).
    - `components/`: Componentes reutilizables de la interfaz de usuario.
    - `styles/`: Archivos de estilos globales y específicos.
    - `utils/`: Funciones utilitarias y helpers.
- `public/`: Archivos estáticos como imágenes y fuentes.
- `package.json`: Archivo de configuración del proyecto y dependencias.
- `next.config.js`: Configuración específica de Next.js.