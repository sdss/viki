#!/usr/bin/env/python

from quart import render_template, Blueprint

from shire import wrapBlocking
from shire.dbConvenience import recentObs

from . import getTemplateDictBase


index_page = Blueprint("index_page", __name__)


@index_page.route('/')
async def index():
    """ Index page. """
    templateDict = getTemplateDictBase()

    obs = await wrapBlocking(recentObs)

    templateDict.update({
        "jd": [i for i in obs["jd"]],
        "lst": [i for i in obs["lst"]],
        "hz": [i for i in obs["hz"]],
        "alt": [i for i in obs["alt"]],
        "seeing": [i for i in obs["seeing"]]
    })

    return await render_template("index.html", **templateDict)
