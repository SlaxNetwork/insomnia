FROM python:3.11.0

WORKDIR /app

COPY src ./src
COPY Pipfile ./Pipfile
COPY deployments.json ./deployments.json

RUN pip install --upgrade pip

RUN pip install pipenv

RUN pipenv lock
RUN pipenv requirements >> requirements.txt
RUN pip install -r requirements.txt

#todo: don't use flask in prod
ENTRYPOINT [ "python", "-m", "flask", "run", "--host=0.0.0.0" ]