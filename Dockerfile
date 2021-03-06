FROM python:3.9.10

ENV HOME /root
WORKDIR /root

COPY . .

RUN pip3 install -r src/requirements.txt

EXPOSE 8000
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.9.0/wait /wait
RUN chmod +x /wait
CMD /wait && python3 src/server.py