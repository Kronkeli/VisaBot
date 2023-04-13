FROM python:3.9

ADD ./ ./

RUN pip install python-telegram-bot
RUN pip install psycopg2
RUN pip install python-dotenv

CMD ["python", "./main.py"]