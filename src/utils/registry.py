from src.cleaner.sources.tonaton.cleaner import TonatonCleaner
from src.scraper.sources.tonaton.scraper import TonatonScraper

REGISTRY = {
    "tonaton": {
        "scraper": TonatonScraper,
        "cleaner": TonatonCleaner,
    },
}


def get_component(source: str, component: str):
    try:
        return REGISTRY[source][component]
    except KeyError as e:
        available_sources = list(REGISTRY.keys())
        available_components = (
            list(REGISTRY.get(source, {}).keys()) if source in REGISTRY else []
        )
        raise ValueError(
            f"[REGISTRY] {component} not registered for source: {source}. "
            f"Available sources: {available_sources}. "
            f"Available components for {source}: {available_components}"
        ) from e
