from bio3dbeacons.api import PROXY_URL


def get_model_asset_url(entry_id: str, model_format: str = "cif") -> str:
    """Returns model URL for an entry

    Args:
        entry_id (str): Unique ID for the model.
        model_format (str, optional): Model format. Defaults to "cif".

    Returns:
        [str]: Model URL
    """
    model_format = model_format.lower()
    return f"{PROXY_URL}/{model_format}/{entry_id}.{model_format}"
