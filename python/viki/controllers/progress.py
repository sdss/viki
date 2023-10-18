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

    targ_counts ={
        "MW": 0,
        "MCs": 0,
        "ORI": 0,
        "FULLSKY": 0,
        "GUM": 0,
        "LV": 0
    }

    targ_mjds = {
        "MW": [],
        "MCs": [],
        "ORI": [],
        "FULLSKY": [],
        "GUM": [],
        "LV": []
    }

    targ_coords = {
        "MW": [],
        "MCs": [],
        "ORI": [],
        "FULLSKY": [],
        "GUM": [],
        "LV": []
    }

    targ_coords_all = {
        "MW": [],
        "MCs": [],
        "ORI": [],
        "FULLSKY": [],
        "GUM": [],
        "LV": []
    }

    min_mjd = 99999
    max_mjd = 0

    for d in done:
        if "MW" in d["target"] or "THOR" in d["target"]:
            targ = "MW"
        elif "MC" in d["target"]:
            targ = "MCs"
        elif "ORI" in d["target"]:
            targ = "ORI"
        elif "FULLSKY" in d["target"]:
            targ = "FULLSKY"
        elif "Gum" in d["target"]:
            targ = "GUM"
        else:
            targ = "LV"
        targ_counts[targ] += int(d["total_exptime"]/900)
        if targ != "FULLSKY":
            targ_coords_all[targ].append([d["ra"], d["dec"]])
        if not d["jd"]:
            continue
        mjd = d["jd"] - 2400000.5
        if mjd < min_mjd:
            min_mjd = mjd
        if mjd > max_mjd:
            max_mjd = mjd
        targ_mjds[targ].append(mjd)
        targ_coords[targ].append({"x": d["ra"], "y": d["dec"], "name": d["tile_id"]})

    x_axis = np.arange(min_mjd, max_mjd, 1)
    x_axis = [int(m) for m in x_axis]

    cumulative = {}
    fractional = {}

    for k, v in targ_mjds.items():
        mjds = np.array(v)
        counts = [[m, len(np.where(mjds < m)[0])] for m in x_axis]
        cumulative[k] = counts
        planned = targ_counts[k]
        frac = [[m, len(np.where(mjds < m)[0])/planned] for m in x_axis]
        fractional[k] = frac

    templateDict.update({
        "cumulative": cumulative,
        "fractional": fractional,
        "targ_coords": targ_coords,
        "targ_coords_all": targ_coords_all
    })

    return await render_template("progress.html", **templateDict)
