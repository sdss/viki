#!/usr/bin/env/python

from quart import render_template, Blueprint

from astropy.time import Time

from viki import wrapBlocking
from viki.dbConvenience import recentObs, queryTonight

from . import getTemplateDictBase


index_page = Blueprint("index_page", __name__)


@index_page.route('/')
async def index():
    """ Index page. """
    templateDict = getTemplateDictBase()

    now = Time.now()
    now.format = "mjd"
    mjd_now = now.value
    # use an offset so "tonight" is used until 15:00 UTC
    sjd_ish = round(mjd_now - 3 / 24)

    jd = mjd_now + 2400000.5

    tonight = await wrapBlocking(queryTonight, jd=jd)

    summary = [[t["tile_id"], t["position"], t["target"]] for t in tonight]

    obs = await wrapBlocking(recentObs)

    templateDict.update({
        "jd": [i for i in obs["jd"]],
        "lst": [i for i in obs["lst"]],
        "hz": [i for i in obs["hz"]],
        "alt": [i for i in obs["alt"]],
        "seeing": [i for i in obs["seeing"]],
        "summary": summary,
        "mjd": sjd_ish
    })

    return await render_template("index.html", **templateDict)
