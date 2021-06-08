FROM python

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN python db.py

EXPOSE 5893

CMD ["python", "app.py"]