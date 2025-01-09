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
    
    targ_counts ={
        "MW": 0,
        "THOR": 0,
        "MCs": 0,
        "ORI": 0,
        "FULLSKY": 0,
        "GUM": 0,
        "LV": 0
    }

    targ_mjds = {
        "MW": [],
        "THOR": [],
        "MCs": [],
        "ORI": [],
        "FULLSKY": [],
        "GUM": [],
        "LV": []
    }

    targ_coords = {
        "MW": {"x": [], "y": [], "name": []},
        "THOR": {"x": [], "y": [], "name": []},
        "MCs": {"x": [], "y": [], "name": []},
        "ORI": {"x": [], "y": [], "name": []},
        "FULLSKY": {"x": [], "y": [], "name": []},
        "GUM": {"x": [], "y": [], "name": []},
        "LV": {"x": [], "y": [], "name": []}
    }

    targ_coords_all = {
        "MW": {"x": [], "y": [], "name": []},
        "THOR": {"x": [], "y": [], "name": []},
        "MCs": {"x": [], "y": [], "name": []},
        "ORI": {"x": [], "y": [], "name": []},
        "FULLSKY": {"x": [], "y": [], "name": []},
        "GUM": {"x": [], "y": [], "name": []},
        "LV": {"x": [], "y": [], "name": []}
    }

    min_mjd = 99999
    max_mjd = 0

    tile_list = [["tile_id", "target", "jd", "dither_pos", "ra", "dec"]]

    ids = list()

    for d in done:
        if "MW" in d["target"]:
            targ = "MW"
        elif "THOR" in d["target"]:
            targ = "THOR"
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
        if d["tile_id"] not in ids:
            ids.append(d["tile_id"])
            targ_counts[targ] += int(d["total_exptime"]/900)
        if targ != "FULLSKY":
            targ_coords_all[targ]["x"].append(d["ra"])
            targ_coords_all[targ]["y"].append(d["dec"])
        if not d["jd"]:
            continue
        mjd = d["jd"] - 2400000.5
        if mjd < min_mjd:
            min_mjd = mjd
        if mjd > max_mjd:
            max_mjd = mjd
        targ_mjds[targ].append(mjd)
        targ_coords[targ]["x"].append(d["ra"])
        targ_coords[targ]["y"].append(d["dec"])
        targ_coords[targ]["name"].append(d["tile_id"])
        tile_list.append([d['tile_id'], d['target'], d['jd'], d['position'],
                          f"{d['ra']:.2f}", f"{d['dec']:.2f}"])

    x_axis = np.arange(min_mjd, max_mjd, 1)
    x_axis = [int(m) for m in x_axis]

    cumulative = {}
    fractional = {}

    all_targs = []
    survey_counts = 0

    for k, v in targ_mjds.items():
        mjds = np.array(v)
        counts = [[m, len(np.where(mjds < m)[0])] for m in x_axis]
        cumulative[k] = counts
        planned = targ_counts[k]
        frac = [[m, len(np.where(mjds < m)[0])/planned] for m in x_axis]
        fractional[k] = frac

        # print(f"{k}, {len(mjds)}, {planned}")

        all_targs.extend(v)
        survey_counts += targ_counts[k]

    all_targs = np.array(all_targs)
    counts = [[m, len(np.where(all_targs < m)[0])] for m in x_axis]
    frac = [[m, len(np.where(all_targs < m)[0])/survey_counts] for m in x_axis]
    fractional["Full Survey"] = frac

    templateDict.update({
        "cumulative": cumulative,
        "fractional": fractional,
        "targ_coords": targ_coords,
        "targ_coords_all": targ_coords_all,
        "full_survey_count": len(all_targs),
        "tile_list": tile_list
    })

    return await render_template("progress.html", **templateDict)
