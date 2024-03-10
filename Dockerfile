FROM python:3.11-slim

ARG PACKAGE_NAME=package
ARG USER=user
ARG WORKDIR=/app

WORKDIR $WORKDIR

RUN pip3 install --no-cache-dir --upgrade pip setuptools
COPY ./requirements.txt $WORKDIR/requirements.txt
COPY ./setup.py $WORKDIR/setup.py
COPY --chown=${USER}:${USER} ./code_snippet_gen/ $WORKDIR/code_snippet_gen/
RUN pip3 install --no-cache-dir -r $WORKDIR/requirements.txt

COPY ./test.py $WORKDIR/test.py

RUN useradd --create-home ${USER}
USER ${USER}

EXPOSE 8000

CMD ["sh", "-c", "cd /app/code_snippet_gen/ && uvicorn main:app --host 0.0.0.0 --port 8000"]
