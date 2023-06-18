#!/usr/bin/env/python

import sys
from logging import getLogger, ERROR

import psycopg2
from quart import Quart, render_template

from shire import observatory, getTemplateDictBase

getLogger('quart.serving').setLevel(ERROR)

app = Quart(__name__)

print("{0}App '{1}' created.{2}".format('\033[92m', __name__, '\033[0m')) # to remove later

STORE_FOLDER = f"/home/sdss5/tmp/metrics_plots/"

app.config.update({
    "STORE_FOLDER": STORE_FOLDER
    })

# -----------------------------------------------------------------------------
# The JSON module is unable to serialize Decimal objects, which is a problem
# as psycopg2 returns Decimal objects for numbers. This block of code overrides
# how psycopg2 parses decimal data types coming from the database, using
# the "float" data type instead of Decimal. This must be done separately for
# array data types.
#
# See link for other data types: http://initd.org/psycopg/docs/extensions.html
# -----------------------------------------------------------------------------
DEC2FLOAT = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMAL.values,
    'DEC2FLOAT',
    lambda value, curs: float(value) if value is not None else None)
psycopg2.extensions.register_type(DEC2FLOAT)

# the decimal array is returned as a string in the form:
# "{1,2,3,4}"
DECARRAY2FLOATARRAY = psycopg2.extensions.new_type(
    psycopg2.extensions.DECIMALARRAY.values,
    'DECARRAY2FLOATARRAY',
    lambda value, curs: [float(x) if x else None for x in value[1:-1].split(",")]
        if value else None)
psycopg2.extensions.register_type(DECARRAY2FLOATARRAY)
# -----------------------------------------------------------------------------

# -------------------
# Register blueprints
# -------------------
from shire.controllers.index import index_page

from shire.controllers.local import localSource

app.register_blueprint(index_page)
app.register_blueprint(localSource)


@app.errorhandler(404)
async def page_not_found(e):
    return await render_template('404.html'), 404


@app.errorhandler(500)
async def err_page(e):
    """ Err page. """
    return await render_template("500.html", **getTemplateDictBase())
