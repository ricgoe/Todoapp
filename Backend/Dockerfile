FROM python:3.12.3

COPY main_db.py requirements.txt ./

RUN pip install -r ./requirements.txt && apt-get update && apt-get install -y

CMD python main_db.py