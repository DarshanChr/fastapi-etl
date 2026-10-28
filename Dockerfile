FROM maven:3.9-eclipse-temurin-17 AS java-base
FROM python:3.11-slim

WORKDIR /app

# Copy Java 17 runtime from the Temurin image

COPY --from=java-base /opt/java/openjdk /opt/java/openjdk

ENV JAVA_HOME=/opt/java/openjdk
ENV PATH="${JAVA_HOME}/bin:${PATH}"

# Install Java and curl
RUN apt-get update &&  \
apt-get install -y --no-install-recommends curl && \
rm -rf /var/lib/apt/lists/*


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