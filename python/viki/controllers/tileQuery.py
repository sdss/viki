#!/usr/bin/env/python

from quart import render_template, Blueprint, request

from viki import wrapBlocking
from viki.dbConvenience import findTiles

from . import getTemplateDictBase


tileQuery_page = Blueprint("tileQuery_page", __name__)


@tileQuery_page.route('/tileQuery.html', methods=['GET'])
async def tile():
    """ Tile query page. """

    ra = None
    dec = None
    radius = None
    tile_ids = []

    if request.args:
        if "tiles" in request.args:
            t_text = request.args["tiles"]
            if len(t_text) > 0:
                try:
                    if "," in t_text:
                        tile_ids = [int(d) for d in t_text.strip().split(",") if len(d)]
                    else:
                        tile_ids = [int(t_text)]
                except:
                    errors.append("invalid design input")
                    tile_ids = list()
        if "ra" in request.args:
            try:
                ra = float(request.args["ra"])
                dec = float(request.args["dec"])
                radius = float(request.args["radius"])
            except ValueError:
                ra = None
                dec = None
                radius = None

    tiles = await wrapBlocking(findTiles, ra=ra, dec=dec,
                               radius=radius, tile_ids=tile_ids)
    
    # if ra is None:
    #     ra = 0.0
    # if dec is None:
    #     dec = 0.0
    # if radius is None:
    #     radius = 1.0

    templateDict = getTemplateDictBase()

    templateDict.update({"tiles": tiles,
                         "ra": ra,
                         "dec": dec,
                         "radius": radius,
                         "tile_ids": tile_ids
    })

    return await render_template("tileQuery.html", **templateDict)
