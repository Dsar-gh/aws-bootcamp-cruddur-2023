FROM python:3.10-slim-buster
# Inside the container
# make a new folder inside container
WORKDIR /backend-flask

# Outside the container -> Inside the container
#  this contains the libraries to insatll to run the app
COPY requirements.txt requirements.txt

# install python libraries used for the app
RUN pip3 install -r requirements.txt

# outside container -> inside container
# . named period means everything in the current directory
# first period from /backend-flask outside container
# second period to /backend-flask inside container (WORKDIR)
COPY . .

# Set enviroment variables (env Vars) inside container
# this will remain set when the container is running 
ENV FLASK_ENV=development

EXPOSE ${PORT}
# python3 -m flask run --host=0.0.0.0 --port=4567
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=4567"]