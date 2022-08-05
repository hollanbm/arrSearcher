import datetime

from config import settings
import asyncio
from aiopyarr import QualityProfile, Tag
from aiopyarr.models.host_configuration import PyArrHostConfiguration
from aiopyarr.sonarr_client import SonarrCommands, SonarrClient, SonarrSeries


async def series_search():
    settings.IP_ADDRESS: str
    settings.API_TOKEN: str
    settings.BASE_API_PATH: str
    host_configuration = PyArrHostConfiguration(
        ipaddress=settings.IP_ADDRESS,
        api_token=settings.API_TOKEN,
        base_api_path=settings.BASE_API_PATH)

    client: SonarrClient
    async with SonarrClient(host_configuration=host_configuration) as client:
        quality_profiles: dict(int, str) = {}
        qp: QualityProfile
        for qp in await client.async_get_quality_profiles():
            quality_profiles[qp.id] = qp.name

        tags: dict(str, int) = {}
        tag: Tag
        for tag in await client.async_get_tags():
            tags[tag.label] = tag.id

        show: SonarrSeries
        for show in await client.async_get_series():
            if (show.monitored and "720p" in quality_profiles.get(show.qualityProfileId) and
                    tags.get("api_search") not in show.tags):
                print(f'initiating Series Search for {show.title}')
                await client.async_sonarr_command(SonarrCommands.SERIES_SEARCH, seriesid=show.id)
                show.tags.append(tags.get("api_search"))
                print(f'adding api_search tag')
                await client.async_edit_series(data=show)
                print('sleeping for 15mins')
                await asyncio.sleep(datetime.timedelta(minutes=15).seconds)


asyncio.run(series_search())
