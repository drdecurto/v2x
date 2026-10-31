import importlib.util,io,tarfile
from pathlib import Path
import pytest
spec=importlib.util.spec_from_file_location('public_fetch',Path(__file__).parents[1]/'scripts/fetch_traces.py')
fetch=importlib.util.module_from_spec(spec);spec.loader.exec_module(fetch)
def archive(path,name):
 with tarfile.open(path,'w:gz') as t:
  content=b'id\n1\n';m=tarfile.TarInfo(name);m.size=len(content);t.addfile(m,io.BytesIO(content))
def test_checksum_mismatch_cannot_install(tmp_path,monkeypatch):
 monkeypatch.setattr(fetch,'ROOT',tmp_path);f=tmp_path/'a.tar.gz';archive(f,'outdoor_parkinglot/1_tx/parameters.csv')
 with pytest.raises(ValueError,match='SHA-256'):fetch.install(f,'0'*64)
 assert not (tmp_path/'data/raw/see_parkinglot').exists()
def test_archive_traversal_rejected(tmp_path,monkeypatch):
 monkeypatch.setattr(fetch,'ROOT',tmp_path);f=tmp_path/'a.tar.gz';archive(f,'../outside.csv')
 with pytest.raises(ValueError,match='Unsafe'):fetch.install(f,fetch.digest(f))
 assert not (tmp_path/'data/raw/see_parkinglot').exists()
def test_verified_archive_installs_expected_layout(tmp_path,monkeypatch):
 monkeypatch.setattr(fetch,'ROOT',tmp_path);f=tmp_path/'a.tar.gz';archive(f,'outdoor_parkinglot/1_tx/parameters.csv');fetch.install(f,fetch.digest(f))
 assert (tmp_path/'data/raw/see_parkinglot/outdoor_parkinglot/1_tx/parameters.csv').read_bytes()==b'id\n1\n'
