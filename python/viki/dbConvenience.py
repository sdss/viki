# from peewee import fn, JOIN
import pandas as pd

from sdssdb.peewee.lvmdb.lvmopsdb import Observation, Weather


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


def tonight(jd):
    """
    return dither, completion, obs, for one night, 
    defined to be jd < obs.jd <= jd + 1
    """
    return
