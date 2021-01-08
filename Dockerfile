FROM python:3

WORKDIR /usr/src/dhtc
COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt
COPY . .
RUN pip3 install .
CMD ["dhtc", "-w"]
EXPOSE 4200:4200