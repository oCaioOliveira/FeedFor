FROM python:3.9

RUN apt-get update && apt-get install -y libpango-1.0-0
WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /code/

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
