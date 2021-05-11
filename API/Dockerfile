FROM python:3.9

#WORKDIR /usr/src/app

COPY requirements.txt ./
#COPY packages/ ./packages

COPY Cisco_Umbrella_Root_CA.cer ./

RUN pip install --requirement requirements.txt || \
    pip install --cert Cisco_Umbrella_Root_CA.cer  --trusted-host pypi.org --requirement requirements.txt 

EXPOSE 80

COPY ./app /app 

ENTRYPOINT [ "uvicorn" ]
CMD ["--host", "0.0.0.0", "--port", "80", "app.main:app"]