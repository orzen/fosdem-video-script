FROM python:3.5

RUN pip install -U pip

RUN pip install requests cssselect lxml

RUN useradd --create-home --system --shell /bin/bash fosdem

COPY ./fosdem-video-script.py /home/fosdem/
WORKDIR /home/fosdem

ENTRYPOINT ["python3", "./fosdem-video-script.py"]
