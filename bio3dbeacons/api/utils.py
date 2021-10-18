from bio3dbeacons.api import SOLR_COLLECTION_URL, SingletonAiohttp


async def query_solr(query: str):

    # default URL
    solr_url = f"{SOLR_COLLECTION_URL}/select?q=uniprotAccession:{query}&wt=json"

    return await SingletonAiohttp.query_url(solr_url)
