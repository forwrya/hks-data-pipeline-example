FROM python:3.12

EXPOSE 8000

RUN ls -la

COPY ./app.py /api/
COPY ./routes/*.py /api/routes/
COPY --from=project_root ./requirements.txt /api/

WORKDIR /api

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT [ "fastapi", "dev", "--host", "0.0.0.0" ]