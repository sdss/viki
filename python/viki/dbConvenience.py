from peewee import fn
import pandas as pd

from sdssdb.peewee.lvmdb.lvmopsdb import (Observation, Weather,
                                          Tile, Dither, CompletionStatus)


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

    return dataframe


def queryTonight(jd):
    """
    return dither, completion, obs, for one night, 
    defined to be jd < obs.jd <= jd + 1
    """
    dithers = Tile.select(Tile.tile_id, Tile.target,
                          Dither.position)\
                  .join(Dither)\
                  .join(Observation)\
                  .where(Observation.jd > jd -1)

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
                          Observation.jd)\
                  .join(Dither)\
                  .join(Observation)\
                  .where(Tile.tile_id == tile_id)

    return tile, dithers.dicts()


def findTiles(ra=None, dec=None, radius=None, tile_ids=None):
    """
    return tiles matching criteria
    """
    
    redFlag = True

    tileQuery = Tile.select(Tile.tile_id, Tile.target,
                            Tile.ra, Tile.dec)

    if ra and dec and radius:
        redFlag = False
        tileQuery = tileQuery.where(Tile.cone_search(ra, dec, radius))

    if tile_ids and type(tile_ids) is list:
        redFlag = False
        tileQuery = tileQuery.where(Tile.tile_id << tile_ids)
    
    if redFlag:
        tileQuery = tileQuery.limit(10)
    else:
        tileQuery = tileQuery.limit(50)
    
    tiles = tileQuery.dicts()

    return tiles


def doneTiles():
    """grab everything that's done
    """

    hist = Tile.select(Tile.tile_id, Tile.target,
                       Dither.pk, fn.Max(Observation.jd).alias("jd"))\
                   .join(Dither)\
                   .join(CompletionStatus)\
                   .switch(Dither)\
                   .join(Observation)\
                   .where(CompletionStatus.done)\
                   .group_by(Tile.tile_id, Tile.target,
                             Dither.pk).dicts()
    return hist