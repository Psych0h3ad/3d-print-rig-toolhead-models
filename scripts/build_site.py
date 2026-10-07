"""Build the pinned native toolhead web assets."""
from pathlib import Path
import argparse,hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();target=a.output.resolve()
 if target.exists()or target.is_relative_to(ROOT/'site'):raise ValueError('Use a new build directory')
 source=ROOT/'site';index=json.loads((source/'ASSET_INDEX.json').read_text(encoding='utf-8'));expected={part['path']for v in index['files'].values()for part in v.get('parts',[v])}|{'ASSET_INDEX.json','NOTICE.txt'}
 assert {f.relative_to(source).as_posix()for f in source.rglob('*')if f.is_file()}==expected
 total=0
 total=sum(v['bytes']for v in index['files'].values())+(source/'ASSET_INDEX.json').stat().st_size+(source/'NOTICE.txt').stat().st_size
 assert total<900_000_000
 target.mkdir(parents=True)
 for r in index['files'].values():
  output=(target/r['path']).resolve();assert output.is_relative_to(target)
  output.parent.mkdir(parents=True,exist_ok=True)
  combined=hashlib.sha256();written=0
  with output.open('wb')as dest:
   for part in r.get('parts',[r]):
    f=(source/part['path']).resolve();assert f.is_relative_to(source.resolve())and f.stat().st_size==part['bytes']
    digest=hashlib.sha256()
    with f.open('rb')as stream:
     while chunk:=stream.read(1024*1024):
      digest.update(chunk);combined.update(chunk);dest.write(chunk);written+=len(chunk)
    assert digest.hexdigest()==part['sha256']
  assert written==r['bytes']and combined.hexdigest()==r['sha256']
 for name in ['ASSET_INDEX.json','NOTICE.txt']:shutil.copyfile(source/name,target/name)
 (target/'.nojekyll').touch();print(f'Built {len(index["files"])+2} toolhead files ({total:,} published bytes).')
if __name__=='__main__':main()
