FROM python:3.9

ADD ./ ./

RUN pip install python-telegram-bot
RUN pip install psycopg2

CMD ["python", "./main.py"]