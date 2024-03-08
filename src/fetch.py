from cryoet_data_portal import Client, Tomogram
from urllib.parse import urlsplit
from os import path

def fetch_tomogram(session, identifier: str, ignore_cache: bool = False, **kw):
    from chimerax.core.errors import UserError

    client = Client()
    tomo = Tomogram.get_by_id(client, int(identifier))
    map_url = tomo.https_mrc_scale0
    vol_name = path.basename(urlsplit(tomo.https_mrc_scale0).path)

    if not tomo:
        raise UserError(f"Could not find tomogram with id {identifier}")

    from chimerax.core.fetch import fetch_file
    filename = fetch_file(session, map_url, tomo.name, vol_name, 'cryoet-portal',
                           uncompress=False, ignore_cache=ignore_cache)

    model_name = tomo.name
    models, status = session.open_command.open_data(filename, format='mrc',
                                                    name=model_name, **kw)

    return models, status

def fetch_annotation():
    pass

