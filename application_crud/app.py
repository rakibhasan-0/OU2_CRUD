import datetime 
from datetime import date, timedelta
import logging
from flask import Flask, render_template, redirect, url_for,request
from library_user import Library_User
from book import Library_Book
from db_connection import create_tables, get_db_connection, close_db_connection
import os


app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

from view import * 
from model import *




if __name__ == "__main__":
    create_tables()
    app.run(debug=True)


