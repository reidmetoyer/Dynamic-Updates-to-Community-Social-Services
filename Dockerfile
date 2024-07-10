#python language
FROM python:3.12-slim

#working directory
WORKDIR /app

#copy directory contents into /app container
COPY . /app

#upgrade pip
RUN pip install --upgrade pip
#install any packages in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#make port 8080 available
EXPOSE 8080

#define environment variable
ENV PORT 8080

RUN echo "environment variables: " &&printenv

#run app.py when container launches
CMD ["python", "app.py"]