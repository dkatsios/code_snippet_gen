FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive
ARG PACKAGE_NAME=package
ARG USER=user
ARG WORKDIR=/app

WORKDIR $WORKDIR

# Update and install dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends apt-utils \
    vim curl wget git fish \
    software-properties-common \
    && add-apt-repository ppa:deadsnakes/ppa \
    && apt-get update

# Install Python 3.11 and necessary Python tools
RUN apt-get install -y --no-install-recommends \
    python3.11 python3.11-venv python3.11-distutils python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install required Python packages
RUN python3.11 -m pip install --upgrade --no-cache-dir pip setuptools wheel
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1

# Copy the requirements and setup files
COPY ./requirements.txt $WORKDIR/requirements.txt
COPY ./setup.py $WORKDIR/setup.py

# Install the Python dependencies
COPY --chown=${USER}:${USER} ./code_snippet_gen/ $WORKDIR/code_snippet_gen/
RUN python3.11 -m pip install --no-cache-dir -r $WORKDIR/requirements.txt

# Copy the test configuration files
COPY ./test.py $WORKDIR/test.py
COPY ./pytest.ini $WORKDIR/pytest.ini

# Setup the non-root user
RUN useradd --create-home ${USER}
RUN chown -R ${USER}:${USER} $WORKDIR

USER ${USER}

EXPOSE 8000

CMD ["sh", "-c", "cd /app/code_snippet_gen/ && uvicorn main:app --host 0.0.0.0 --port 8000"]
