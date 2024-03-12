"""
A simple flask app for TV show information
"""
import flask
from flask.views import MethodView
from index import Index
from addlist import AddList
from mylist import MyList

app = flask.Flask(__name__)       # Our Flask App


"""
Adding the URL rules for the app
"""
app.add_url_rule('/',
                 view_func=Index.as_view('index'),
                 methods=["GET"])

app.add_url_rule('/addlist',
                 view_func=AddList.as_view('addlist'),
                 methods=['GET', 'POST'])

app.add_url_rule('/mylist',
                 view_func=MyList.as_view('mylist'),
                 methods=['GET', 'POST'])

"""
Specifying the host and port for the app
"""
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
