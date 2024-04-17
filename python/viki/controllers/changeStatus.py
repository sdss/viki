#!/usr/bin/env/python

from quart import render_template, Blueprint, request, jsonify

from viki import wrapBlocking
from viki.dbConvenience import tileStatus, updateTileStatus

from . import getTemplateDictBase


changeStatus_page = Blueprint("changeStatus_page", __name__)


@changeStatus_page.route('/changeStatus.html', methods=['GET'])
async def changeStatus():
    """ changeStatus page. """
    templateDict = getTemplateDictBase()

    tile_ids = list()
    exp_nos = list()

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
        if "exp_no" in request.args:
            e_text = request.args["exp_no"]
            if len(e_text) > 0:
                try:
                    if "," in e_text:
                        exp_nos = [int(d) for d in e_text.strip().split(",") if len(d)]
                    else:
                        exp_nos = [int(e_text)]
                except:
                    errors.append("invalid exp no input")
                    exp_nos = list()
    
    stat = await wrapBlocking(tileStatus, tile_ids=tile_ids, 
                              exp_nos=exp_nos)

    if len(stat) == 0 and (len(tile_ids) > 0 or len(exp_nos) > 0):
        errors.append("No tiles and/or exposures matching query")

    templateDict.update({"dithers": stat,
                         "tile_ids": tile_ids,
                         "exp_nos": exp_nos,
                         "errorMsg": errors
                         })

    return await render_template("changeStatus.html", **templateDict)

@changeStatus_page.route('/updateStatus/', methods=["GET"])
async def updateStatus():
    tile_id = int(request.args["tile_id"])
    dither = int(request.args["dither"])
    status = request.args["status"]

    if status == "done":
        done = True
    else:
        done = False

    success = await wrapBlocking(updateTileStatus, tile_id, dither, done)
    if success:
        return jsonify(status)
    else:
        return jsonify("failed")