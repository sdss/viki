#!/usr/bin/env/python

from quart import render_template, Blueprint, request, jsonify

from viki import wrapBlocking
from viki.dbConvenience import disabledTiles, disableTile

from . import getTemplateDictBase


disable_page = Blueprint("disable_page", __name__)


@disable_page.route('/disabled.html', methods=['GET'])
async def disable():
    """ disable page. """
    templateDict = getTemplateDictBase()

    tile_ids = list()

    errors = list()
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
                    errors.append("invalid tile id input")
                    tile_ids = list()
    
    tiles = await wrapBlocking(disabledTiles, tile_ids=tile_ids)

    templateDict.update({"tiles": tiles,
                         "tile_ids": tile_ids,
                         "errorMsg": errors
                         })

    return await render_template("disabled.html", **templateDict)


@disable_page.route('/disableTile/', methods=["GET"])
async def disableTileWrap():
    tile_id = int(request.args["tile_id"])
    disable = request.args["disable"] == "true"

    N = await wrapBlocking(disableTile, tile_id, disable)
    if N == 1 and disable:
        return jsonify("disabled")
    elif N == 1:
        return jsonify("enabled")
    else:
        return jsonify("failed")
