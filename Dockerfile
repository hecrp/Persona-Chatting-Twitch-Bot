# Usa una imagen base de Python
FROM python:3.9-slim

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos de requisitos primero para aprovechar la caché de Docker
COPY requirements.txt .

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copia el resto del código fuente del proyecto al contenedor
COPY . .

# Copia el archivo de configuración
COPY config.yml /app/config.yml

# Comando para ejecutar la aplicación
CMD ["python", "-m", "twitch_claude_bot.main"]