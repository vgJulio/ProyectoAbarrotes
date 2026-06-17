from flask import Flask, render_template, request
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()
uri = os.getenv("MONGO_URI")
cliente = MongoClient(uri)
db = cliente['abarrotes']
