FROM python:3.9

ADD source/ source/

RUN pip install python-telegram-bot

CMD ["python", "./source/main.py"]