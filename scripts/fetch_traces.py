"""Obtain the separately licensed SEE-V2X archive; verify before extracting.

Use --archive for a manually downloaded file, or --url for a direct HTTPS link
obtained from the official dataset portal. Nothing is downloaded by default.
"""
import argparse,hashlib,json,shutil,tarfile,tempfile,urllib.request
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
def digest(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
 return h.hexdigest()
def install(archive,expected):
 if digest(archive)!=expected:raise ValueError('Archive SHA-256 mismatch; refusing extraction')
 raw=ROOT/'data/raw';raw.mkdir(parents=True,exist_ok=True)
 target=raw/'see_parkinglot'
 if target.exists():raise FileExistsError('Extraction target exists; inspect it instead of overwriting')
 with tempfile.TemporaryDirectory(dir=raw) as td:
  dest=Path(td)
  with tarfile.open(archive,'r:gz') as tf:
   members=tf.getmembers()
   if sum(m.size for m in members)>4*1024**3:raise ValueError('Unexpected uncompressed size')
   for m in members:
    path=PurePosixPath(m.name)
    if path.is_absolute() or '..' in path.parts or not(m.isdir() or m.isfile()):raise ValueError('Unsafe archive member')
    f=dest.joinpath(*path.parts)
    if m.isdir():f.mkdir(parents=True,exist_ok=True)
    else:
     f.parent.mkdir(parents=True,exist_ok=True)
     with tf.extractfile(m) as src,f.open('wb') as dst:shutil.copyfileobj(src,dst)
  if not (dest/'outdoor_parkinglot/1_tx/parameters.csv').exists():raise ValueError('Unexpected dataset layout')
  dest.rename(target)
 stored=raw/'see_v2x_outdoor_parkinglot.tar.gz'
 if archive.resolve()!=stored.resolve():shutil.copy2(archive,stored)
 print('Verified and installed. Next: python scripts/prepare_traces.py')
def main():
 ap=argparse.ArgumentParser(description=__doc__);group=ap.add_mutually_exclusive_group();group.add_argument('--archive',type=Path);group.add_argument('--url');args=ap.parse_args()
 m=json.loads((ROOT/'data/trace_manifest.json').read_text())
 if not args.archive and not args.url:
  print('Obtain outdoor_parkinglot.tar.gz from '+m['source']);print('Expected SHA-256: '+m['archive_sha256']);print('Then use --archive FILE, or --url DIRECT_HTTPS_DOWNLOAD_URL. Review upstream terms.');return
 if args.archive:install(args.archive,m['archive_sha256']);return
 if not args.url.startswith('https://'):ap.error('A direct HTTPS URL is required')
 with tempfile.TemporaryDirectory() as td:
  f=Path(td)/'archive.tar.gz'
  with urllib.request.urlopen(args.url,timeout=120) as response,f.open('wb') as output:
   if not response.url.startswith('https://'):raise ValueError('Refusing downgrade redirect')
   total=0
   while chunk:=response.read(1024*1024):
    total+=len(chunk)
    if total>2*1024**3:raise ValueError('Unexpected archive size')
    output.write(chunk)
  install(f,m['archive_sha256'])
if __name__=='__main__':main()
