FROM python:3.9

ENV VIRTUAL_ENV=/usr/local
RUN pip install uv

ENV PYTHONASYNCIODEBUG=1
COPY ./files .

CMD [ "/bin/bash" ]