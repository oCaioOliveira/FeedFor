FROM python:3.9

WORKDIR /code

COPY . /code/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "feedfor.wsgi:application"]