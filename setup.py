from setuptools import setup

setup(
    name="pygc",
    use_scm_version={
        "write_to": "pygc/_version.py",
        "write_to_template": '__version__ = "{version}"',
        "tag_regex": r"^(?P<prefix>v)?(?P<version>[^\+]+)(?P<suffix>.*)?$",
    },
)
