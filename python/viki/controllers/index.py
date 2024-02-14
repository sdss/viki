#!/usr/bin/env/python

from quart import render_template, Blueprint

from astropy.time import Time
import numpy as np

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

    obs, zeropoints = await wrapBlocking(recentObs)

    ZP0 = -23.25

    transp = np.power(10, -0.4*(np.array(zeropoints) - ZP0))

    # transp = np.clip(transp, 0, 1)

    mjds = np.array([int(i - 2400000.5) for i in obs["jd"]])

    mjds = mjds[np.where(mjds > sjd_ish - 30)]

    mjds, counts = np.unique(mjds, return_counts=True)

    recentMjds = [[m, c] for m, c in zip (mjds, counts)]
    recentMjds.reverse()

    templateDict.update({
        "jd": [i for i in obs["jd"]],
        "lst": [i for i in obs["lst"]],
        "hz": [i for i in obs["hz"]],
        "alt": [i for i in obs["alt"]],
        "seeing": [i for i in obs["seeing"]],
        "transparency": list(transp),
        "summary": summary,
        "mjd": sjd_ish,
        "recentMjds": recentMjds
    })

    return await render_template("index.html", **templateDict)
