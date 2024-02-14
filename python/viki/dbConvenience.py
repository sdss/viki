import os

from peewee import fn, JOIN
import pandas as pd

from sdssdb.peewee.lvmdb.lvmopsdb import (Observation, Weather, Exposure,
                                          Tile, Dither, CompletionStatus,
                                          Version, AGCamFrame)


def recentObs(jd=None):
    """
    return observations since jd, or all
    """

    obs = Observation.select(Observation.jd, Observation.lst, Observation.hz,
                             Observation.alt, Observation.lunation,
                             Weather.seeing)\
                     .join(Weather)

    if jd:
        obs = obs.where(Observation.jd > jd)
    
    dataframe = pd.DataFrame(obs.dicts())

    zeropoint_query = AGCamFrame.select(AGCamFrame.zero_point).tuples()

    zeropoints = [float(z[0]) for z in zeropoint_query if z[0]]

    return dataframe, zeropoints


def queryTonight(jd):
    """
    return dither, completion, obs, for one night, 
    defined to be jd < obs.jd <= jd + 1
    """
    dithers = Tile.select(Tile.tile_id, Tile.target,
                          Dither.position)\
                  .join(Dither)\
                  .join(Observation)\
                  .where(Observation.jd > jd,
                         Observation.jd < jd + 1)

    return dithers.dicts()


def tileInfo(tile_id):
    """
    return tile level info
    """

    tile = Tile.get(tile_id=tile_id)

    tile = {"tile_id": tile.tile_id,
            "ra": tile.ra,
            "dec": tile.dec,
            "pa": tile.pa,
            "target": tile.target}

    dithers = Tile.select(Tile.tile_id, Dither.position,
                          Observation.jd, Exposure.exposure_no)\
                  .join(Dither)\
                  .join(Observation)\
                  .join(Exposure)\
                  .where(Tile.tile_id == tile_id)

    return tile, dithers.dicts()


def findTiles(ra=None, dec=None, radius=None, tile_ids=None,
              target=None, returnObserved=False):
    """
    return tiles matching criteria
    """
    
    redFlag = True

    tile_alias = Tile.alias()

    dithersDone = Dither.select(fn.count(CompletionStatus.pk))\
                        .join(CompletionStatus, JOIN.LEFT_OUTER)\
                        .switch(Dither).join(tile_alias, JOIN.LEFT_OUTER)\
                        .where(CompletionStatus.done,
                               tile_alias.tile_id == Tile.tile_id).alias("done")

    tileQuery = Tile.select(Tile.tile_id, Tile.target,
                            Tile.ra, Tile.dec,
                            Tile.total_exptime,
                            dithersDone)


    if ra and dec and radius:
        redFlag = False
        tileQuery = tileQuery.where(Tile.cone_search(ra, dec, radius))

    if tile_ids and type(tile_ids) is list:
        redFlag = False
        tileQuery = tileQuery.where(Tile.tile_id << tile_ids)
    else:
        ver = Version.get(label=os.getenv("TILE_VER"))
        tileQuery = tileQuery.where(Tile.version_pk == ver.pk)
    
    if target:
        tileQuery = tileQuery.where(Tile.target == target)
    
    if returnObserved:
        tileQuery = tileQuery.where(dithersDone > 0)

    if redFlag:
        tileQuery = tileQuery.limit(10)
    else:
        tileQuery = tileQuery.limit(50)
    
    tiles = tileQuery.dicts()

    return tiles


def doneTiles():
    """grab everything that's done
    """

    ver = Version.get(label=os.getenv("TILE_VER"))

    hist = Tile.select(Tile.tile_id, Tile.target, Tile.ra, Tile.dec,
                       Tile.total_exptime,
                       Dither.pk, CompletionStatus.done,
                       fn.Max(Observation.jd).alias("jd"))\
               .join(Dither, JOIN.LEFT_OUTER)\
               .join(CompletionStatus, JOIN.LEFT_OUTER)\
               .switch(Dither)\
               .join(Observation, JOIN.LEFT_OUTER)\
               .where(Tile.version_pk == ver.pk)\
               .group_by(Tile.tile_id, Tile.target,
                         Dither.pk, CompletionStatus.done).dicts()
    return hist


def tileStatus(tile_ids=[], exp_nos=[]):
    """grab everything that's done
    """

    ver = Version.get(label=os.getenv("TILE_VER"))

    done = Tile.select(Tile.tile_id, 
                       Exposure.exposure_no, Exposure.exposure_time,
                       Dither.position, CompletionStatus.done)\
               .join(Dither, JOIN.LEFT_OUTER)\
               .join(CompletionStatus, JOIN.LEFT_OUTER)\
               .switch(Dither)\
               .join(Observation, JOIN.LEFT_OUTER)\
               .join(Exposure)\
               .where(Tile.version_pk == ver.pk).limit(20)

    if len(tile_ids) > 0:
        done = done.where(Tile.tile_id << tile_ids)
    if len(exp_nos) > 0:
        done = done.where(Exposure.exposure_no << exp_nos)

    return done.dicts()


def updateTileStatus(tile_id, dither, done):
    statuses = CompletionStatus.select(CompletionStatus.pk)\
               .join(Dither).join(Tile)\
               .where(Tile.tile_id == tile_id,
                      Dither.position == dither)

    res = CompletionStatus.update(done=done)\
          .where(CompletionStatus.pk << statuses).execute()
    return res

def listTargets():
    ver = Version.get(label=os.getenv("TILE_VER"))
    targets = Tile.select(fn.Distinct(Tile.target))\
                  .where(Tile.version_pk == ver.pk)
    
    return [t.target for t in targets]
