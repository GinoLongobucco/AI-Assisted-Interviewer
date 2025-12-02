# AI-Assisted Interviewer --- Backend (FastAPI)

Este backend implementa la lógica necesaria para administrar entrevistas
por voz, almacenar candidatos, preguntas, respuestas, transcripciones y
evaluaciones generadas por IA. Está construido con FastAPI, Supabase,
OpenAI y Docker.

## Requisitos

-   Docker y Docker Compose instalados\
-   Archivo `.env` ubicado en `/backend` con las claves necesarias:

```{=html}
<!-- -->
```
    SUPABASE_URL=your_supabase_project_url
    SUPABASE_KEY=your_supabase_service_key
    OPENAI_API_KEY=your_openai_key

## Ejecutar Backend con Docker

1.  Ir al directorio del backend:

```{=html}
<!-- -->
```
    cd backend

2.  Construir e iniciar el servicio:

```{=html}
<!-- -->
```
    docker compose up --build

3.  Acceder a la documentación interactiva:

http://localhost:8000/docs

# Endpoints Principales

## 1. Registrar candidato

**POST /register_candidate**

Body:

``` json
{
  "email": "test@mail.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

Devuelve el `candidate_id`.

## 2. Iniciar entrevista

**POST /start_interview/{candidate_id}**

Body:

``` json
{ "role": "Machine Learning Engineer" }
```

Devuelve `interview_id`.

## 3. Generar preguntas automáticamente

**POST /generate_questions_for_role**

Body:

``` json
{ "role": "Backend Developer" }
```

Genera 5 preguntas nuevas si no existen en la base de datos.

## 4. Obtener siguiente pregunta

**GET /next_question/{interview_id}**

Devuelve la siguiente pregunta pendiente según las ya respondidas.

## 5. Subir respuesta en audio

**POST /submit_answer**

Form-data: - interview_id - question_id - audio (.wav)

Transcribe el audio usando Whisper y guarda la respuesta.

## 6. Evaluar respuesta

**POST /evaluate_answer**

Body:

``` json
{ "answer_id": "uuid" }
```

Genera score y feedback usando IA.

## 7. Finalizar entrevista

**POST /finish_interview/{interview_id}**

Calcula el puntaje final y cierra la entrevista.

# Flujo General

1.  Registrar candidato\
2.  Crear entrevista según el rol\
3.  Obtener pregunta\
4.  Enviar audio\
5.  Recibir transcripción\
6.  Evaluación automática\
7.  Mostrar siguiente pregunta\
8.  Finalizar entrevista

# Estructura del Proyecto

    backend/
    │── app/
    │   ├── main.py
    │   ├── db.py
    │   └── __init__.py
    │── .env
    │── Dockerfile
    │── docker-compose.yml
    │── requirements.txt

# Uso para el equipo

-   El frontend se comunica únicamente a través de los endpoints HTTP.\
-   El módulo de IA puede usar las rutas de evaluación y generación.\
-   No se requiere acceso directo a Supabase; el backend gestiona toda
    la comunicación con la base de datos.
