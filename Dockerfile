FROM python:3.9

COPY ./files .

ENV VIRTUAL_ENV=/usr/local
RUN pip install uv

CMD [ "/bin/bash" ]