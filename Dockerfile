
FROM python:3.10-slim
WORKDIR /app
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    netcat-openbsd \ 
    && apt-get clean
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

#puerto 8000 para el servidor de desarrollo de Django
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]