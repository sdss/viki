#!/usr/bin/env/python

from os import listdir

from quart import render_template, Blueprint, request, current_app

from viki import wrapBlocking
from viki.dbConvenience import recentObs, queryTonight

from . import getTemplateDictBase


mjdSummary = Blueprint("mjdSummary", __name__)


@mjdSummary.route('/summary.html')
async def summary():
    """ summary page. """
    templateDict = getTemplateDictBase()

    mjd = int(request.args["mjd"])
    jd = mjd + 2400000.5
    tonight = await wrapBlocking(queryTonight, jd=jd)

    summary = [[t["tile_id"], t["position"]] for t in tonight]

    imgdir = current_app.config["STORE_FOLDER"]
    pngs = await wrapBlocking(listdir, imgdir)

    templateDict.update({
        "summary": summary,
        "mjd": mjd,
        "pngs": pngs
    })

    return await render_template("summary.html", **templateDict)
