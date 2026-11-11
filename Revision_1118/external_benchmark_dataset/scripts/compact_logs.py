"""Losslessly compact verbose completed-run reports; preserve all evidence."""
from pathlib import Path
import gzip
ROOT=Path(__file__).resolve().parents[1]
for path in (ROOT/'validation').rglob('*'):
 if path.name not in ('generation.log','verification.json') or path.stat().st_size<1024*1024:continue
 data=path.read_bytes();compressed=gzip.compress(data,compresslevel=6,mtime=0)
 assert gzip.decompress(compressed)==data
 path.with_suffix(path.suffix+'.gz').write_bytes(compressed);path.unlink()
 print(path.relative_to(ROOT),len(data),'->',len(compressed))
