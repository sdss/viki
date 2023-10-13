#!/usr/bin/env/python

import numpy as np
from quart import render_template, Blueprint

from viki import wrapBlocking
from viki.dbConvenience import doneTiles

from . import getTemplateDictBase


progress_page = Blueprint("progress_page", __name__)


@progress_page.route('/progress.html')
async def progress():
    """ progress page. """
    templateDict = getTemplateDictBase()

    # actually done dithers, so x9 for some tiles
    done = await wrapBlocking(doneTiles)
    
    "MW*", "SMC*", "LMC*", "ORION*", "Gum*"

    targ_mjds = {
        "MW": [],
        "MCs": [],
        "ORI": [],
        "GUM": [],
        "LV": []
    }

    min_mjd = 99999
    max_mjd = 0

    for d in done:
        if "MW" in d["target"]:
            targ = "MW"
        elif "MC" in d["target"]:
            targ = "MCs"
        elif "ORI" in d["target"]:
            targ = "ORI"
        elif "Gum" in d["target"]:
            targ = "GUM"
        else:
            targ = "LV"
        mjd = d["jd"] - 2400000.5
        if mjd < min_mjd:
            min_mjd = mjd
        if mjd > max_mjd:
            max_mjd = mjd
        targ_mjds[targ].append(mjd)
    
    x_axis = np.arange(min_mjd, max_mjd, 1)
    x_axis = [int(m) for m in x_axis]

    cumulative = {}

    for k, v in targ_mjds.items():
        mjds = np.array(v)
        counts = [[m, len(np.where(mjds < m)[0])] for m in x_axis]
        cumulative[k] = counts

    templateDict.update({
        "cumulative": cumulative
    })

    return await render_template("progress.html", **templateDict)
