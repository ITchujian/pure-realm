from typing import Iterable


class SoftwareVersion:
    def __init__(self, version: str, features: Iterable, paths: Iterable):
        self.version = version
        self.features = features
        self.paths = paths


class Software:
    def __init__(self, name: str):
        self.name = name
        self.versions = []

    def add_version(self, version: SoftwareVersion):
        self.versions.append(version)
