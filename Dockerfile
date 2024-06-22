FROM python:3.9

WORKDIR /code

COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

COPY ./entrypoint.sh .
RUN chmod +x /code/entrypoint.sh

COPY . .

EXPOSE 8000

ENTRYPOINT ["/code/entrypoint.sh"]