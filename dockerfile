# Dokerfile to create the container image for the DCA app
FROM python:3.12
LABEL maintainer="Wolf Paulus <wolf@paulus.com>"

RUN apt-get update && \
    apt-get install -yq tzdata && \
    ln -fs /usr/share/zoneinfo/America/Phoenix /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

COPY . /dca
RUN pip install --no-cache-dir --upgrade -r /dca/requirements.txt
RUN chmod +x /dca/healthcheck.sh
WORKDIR /dca/

EXPOSE 8000

#  prevents Python from writing .pyc files to disk
#  ensures that the python output is sent straight to terminal (e.g. the container log) without being first buffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/dca/src
CMD ["python3.12",  "-m", "streamlit", "run", "--server.port", "8000", "src/app.py"]
