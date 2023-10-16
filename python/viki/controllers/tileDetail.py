#!/usr/bin/env/python

from quart import render_template, Blueprint, request

from viki import wrapBlocking
from viki.dbConvenience import tileInfo

from . import getTemplateDictBase


tileDetail_page = Blueprint("tileDetail_page", __name__)


@tileDetail_page.route('/tileDetail.html', methods=['GET'])
async def tile():
    """ Tile page. """
    templateDict = getTemplateDictBase()

    tile_id = int(request.args["tile_id"])
    
    tile, dithers = await wrapBlocking(tileInfo, tile_id)

    dithers = [[t["position"],
                int(t["jd"] - 2400000.5),
                t["exposure_no"]] 
                for t in dithers]

    templateDict.update({"tile": tile,
                         "dithers": dithers
    })

    return await render_template("tileDetail.html", **templateDict)
