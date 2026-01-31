# PBEback
TFG backend from PBE quiz make it with django.

To run this proyect only you need is the proyect django theirs directories and hosted in your work's dircetory.

Could you allow this project in your own repository or working dircetory moving files like backend, api, apps directory and manage.py file into your directory and running the commands below:

## Steps to Run Backend Server
Move it to your directory and follow this Steps:
1. Create an enviroment
2. Activate your enviroment
3. Install requirements
4. Verifying installation
5. Making migrations to BD
6. Run server Django

1. Create and enviroment:
    - python -m venv env

2. Activate it:
    - On windows:
        - env\Scripts\activate

3. Install requirements
    - pip install -r requirements.txt

    Can you show it with:
    - pip list

4. Verifying installation(OPTIONAL)
To use manage.py command you should be in its dircetory.

    - python manage.py check

5. Making migrations to DB

This command create what are the migrations will be done and their dependencies 
to generate the models into the migrations file in apps directory from django files.

    - python manage.py make migrations 
    - python manage.py migrate --  Create the models(tables) into Database(DB)

6. Run server Django
If this command works you show a new window running into default localhost django server 127.0.0.8/
    - python manage.py runserver

