FROM python:3.9
 
COPY ./scripts ./scripts

ENV VIRTUAL_ENV=/usr/local
RUN pip install uv
 
CMD [ "/bin/bash" ]