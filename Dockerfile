FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
# Set time synchronization between container and host
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime

CMD ["sh", "-c", "python main.py && tail -f /dev/null"]
