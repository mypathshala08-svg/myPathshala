# TiffinGo Spark image: Python 3.12 + Java 21 + PySpark 4.3.0 (driver, master, workers, history server)
FROM eclipse-temurin:21-jre AS jre
FROM python:3.12-slim-bookworm
COPY --from=jre /opt/java/openjdk /opt/java/openjdk
RUN pip install --no-cache-dir pyspark==4.3.0 "pandas<3" pyarrow
ENV JAVA_HOME=/opt/java/openjdk \
    SPARK_HOME=/usr/local/lib/python3.12/site-packages/pyspark \
    PYSPARK_PYTHON=python3
ENV PATH=$JAVA_HOME/bin:$SPARK_HOME/bin:$SPARK_HOME/sbin:$PATH
