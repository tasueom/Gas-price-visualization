from flask import Flask, render_template as ren, request, redirect, url_for
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return ren('index.html')

if __name__ == "__main__":
    app.run(debug=True)