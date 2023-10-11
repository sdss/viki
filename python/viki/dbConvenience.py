# from peewee import fn, JOIN
import pandas as pd

from sdssdb.peewee.lvmdb.lvmopsdb import (Observation, Weather,
                                          Tile, Dither)


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