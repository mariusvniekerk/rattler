from __future__ import annotations
import os
from typing import List, Optional
from rattler.package.package_name import PackageName

from rattler.rattler import PyPrefixRecord
from rattler.prefix.prefix_paths import PrefixPaths
from rattler.version.with_source import VersionWithSource


class PrefixRecord:
    def __init__(self, source: str) -> None:
        if not isinstance(source, str):
            raise TypeError(
                "PrefixRecord constructor received unsupported type "
                f" {type(source).__name__!r} for the `source` parameter"
            )
        self._record = PyPrefixRecord(source)

    @classmethod
    def _from_py_prefix_record(cls, py_prefix_record: PyPrefixRecord) -> PrefixRecord:
        """Construct Rattler PrefixRecord from FFI PyPrefixRecord object."""
        record = cls.__new__(cls)
        record._record = py_prefix_record
        return record

    @staticmethod
    def from_path(path: os.PathLike[str]) -> PrefixRecord:
        """
        Parses a PrefixRecord from a file.

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>>
        ```
        """
        return PrefixRecord._from_py_prefix_record(PyPrefixRecord.from_path(path))

    def write_to_path(self, path: os.PathLike[str], pretty: bool) -> None:
        """
        Writes the contents of this instance to the file at the specified location.
        """
        self._record.write_to_path(path, pretty)

    @property
    def package_tarball_full_path(self) -> Optional[os.PathLike[str]]:
        """
        The path to where the archive of the package was stored on disk.

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>> r.package_tarball_full_path
        'C:\\\\Users\\\\bas\\\\micromamba\\\\pkgs\\\\requests-2.28.2-pyhd8ed1ab_0.tar.bz2'
        >>>
        ```
        """
        return self._record.package_tarball_full_path

    @property
    def extracted_package_dir(self) -> Optional[os.PathLike[str]]:
        """
        The path that contains the extracted package content.

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>> r.extracted_package_dir
        'C:\\\\Users\\\\bas\\\\micromamba\\\\pkgs\\\\requests-2.28.2-pyhd8ed1ab_0'
        >>>
        ```
        """
        return self._record.extracted_package_dir

    @property
    def files(self) -> List[os.PathLike[str]]:
        """
        A sorted list of all files included in this package

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>> r.files # doctest:+ELLIPSIS
        [...]
        >>>
        ```
        """
        return self._record.files

    @property
    def paths_data(self) -> PrefixPaths:
        """
        Information about how files have been linked when installing the package.

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>> r.paths_data
        PrefixPaths()
        >>>
        ```
        """
        return PrefixPaths._from_py_prefix_paths(self._record.paths_data)

    @property
    def requested_spec(self) -> Optional[str]:
        """
        The spec that was used when this package was installed.
        Note that this field is not currently updated if another
        spec was used. If this package was not directly requested by the
        user but was instead installed as a dependency of another package
        `None` will be returned.

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>> r.requested_spec
        ''
        >>>
        ```
        """
        return self._record.requested_spec

    @property
    def name(self) -> PackageName:
        """
        Package name of the PrefixRecord.

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>> r.name
        PackageName("requests")
        >>>
        ```
        """
        return PackageName._from_py_package_name(self._record.name)

    @property
    def version(self) -> VersionWithSource:
        """
        Version of the PrefixRecord.

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>> r.version
        VersionWithSource("2.28.2")
        >>>
        ```
        """
        return VersionWithSource(self._record.version)

    def __repr__(self) -> str:
        """
        Returns a representation of the version

        Examples
        --------
        ```python
        >>> r = PrefixRecord.from_path(
        ...     "../test-data/conda-meta/requests-2.28.2-pyhd8ed1ab_0.json"
        ... )
        >>> r
        PrefixRecord(name="requests", version="2.28.2")
        >>>
        ```
        """
        return f'PrefixRecord(name="{self.name.normalized}", version="{self.version}")'
