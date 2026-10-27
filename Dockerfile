FROM python:3.11-slim

WORKDIR /app

# Install Java and curl
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        openjdk-17-jre-headless \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Configure Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Download PostgreSQL JDBC driver into the image
RUN mkdir -p /opt/spark/jars && \
    curl -fL \
    https://jdbc.postgresql.org/download/postgresql-42.7.8.jar \
    -o /opt/spark/jars/postgresql-42.7.8.jar

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]