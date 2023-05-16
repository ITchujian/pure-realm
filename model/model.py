from typing import Iterable


class SoftwareVersion:
    def __init__(self, version: str, feature: str, paths: Iterable):
        self.version = version
        self.feature = feature
        self.paths = paths


class Software:
    def __init__(self, name: str):
        self.name = name
        self.versions = []

    def add_version(self, version: SoftwareVersion):
        self.versions.append(version)
