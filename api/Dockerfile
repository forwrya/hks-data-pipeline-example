FROM python:3.12

EXPOSE 8000

COPY --from=project_root ./requirements.txt /api/

WORKDIR /api

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt

COPY ./app.py /api/
COPY ./settings.py /api/
COPY ./routes/*.py /api/routes/
COPY ./views/*.py /api/views/
COPY ./models/*.py /api/models/

ENTRYPOINT [ "fastapi", "dev", "--host", "0.0.0.0", "--port", "8000" ]