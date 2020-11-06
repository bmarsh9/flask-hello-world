#Build
docker build -t simple-flask-app:latest .

#Run
docker run -d -p 5000:5000 simple-flask-app
