def _get_version_from_setuptools() -> str:
    from pkg_resources import get_distribution

    return get_distribution("eevee-chat").version


__all__ = ["__version__"]
__version__ = _get_version_from_setuptools()
