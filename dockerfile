FROM python:3.8.1
COPY ./ /www/wwwroot/
WORKDIR /www/wwwroot/
RUN python -m pip install --upgrade pip -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
RUN python -m pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com

CMD ["python", "run.py"]
