#python language
FROM python:3.9.12

#copy directory contents into /app container
COPY . /app


#working directory
WORKDIR /app

#env variables
ENV GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json

RUN chmod 644 /app/credentials.json

#upgrade pip
RUN pip install --upgrade pip
#install any packages in requirements.txt
RUN pip install -r requirements.txt

#make port 8080 available
EXPOSE 8080

#define environment variable
ENV PORT=8080



#run app.py when container launches
CMD ["python", "app.py"]