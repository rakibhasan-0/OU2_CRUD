# Sample Python base for lab 2

This is an example CRUD application using Python and Flask. The example
stores and loads data from a global Python list, in your example this list
should be replaced with calls to your database (for example by using 
`psycopg2`).

## Setup
This example requires `pip` and Python 3. If you get an error
similar to "Could not find module pip", you need to install `pip` before
proceeding: [Pip installation](https://pip.pypa.io/en/stable/installing/).

Download the entire [`python_example`](../python_example/) directory to your
computer. Following this guide over SSH will **not** work as you will most
likely not have access to the remote machine through your browser.

## Install Flask
From within this sample directory, run the command:
```bash
python3 -m pip install -r requirements.txt
```
If successful, this should install Flask. The next step is to start the Flask
web-server. This can be done with the following command: 
```bash
flask run
```

If all went well, you should now be able to test the sample snack application by
visiting [http://localhost:5000/](http://localhost:5000/) 
(or the URL output by Flask).

### Error: `flask: command not found`
If you still cannot run Flask after the installation, you might have to
add your local bin folder to the PATH. To do this, you can run:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```
and then restart your terminal. If the problem persists, check the output of the
`python3 -m pip install -r requirements.txt` command for additional information.

## Application structure

The application contains a couple of files, briefly described below.

* `app.py` Contains the actual application, with the routes that the user can
  visit, as well as the logic.
* `templates/` Contains templates that flask can render.
    * `templates/base.html` Contains the base template that all other templates
    can
      be derived from.
    * `templates/index.html` The first page that the user sees when opening the
    application.
    * `templates/snacks.html` The snack interface. The interface shows all
    available snacks, as well as controls that allows a user to add or remove
    snacks.

## Links
* [Flask quickstart](https://flask.palletsprojects.com/en/2.0.x/quickstart/)
* [Psycopg2 documentation](https://www.psycopg.org/docs/)
