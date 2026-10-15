import urllib.request,zipfile,io,pathlib
p=pathlib.Path('output/experiments/public_semantics_20261015/data')
for id,name in [(602,'dry+bean+dataset'),(545,'rice+cammeo+and+osmancik'),(850,'raisin'),(357,'occupancy+detection'),(471,'electrical+grid+stability+simulated+data')]:
 u=f'https://archive.ics.uci.edu/static/public/{id}/{name}.zip'
 b=urllib.request.urlopen(u).read(); (p/f'{id}.zip').write_bytes(b)
 z=zipfile.ZipFile(io.BytesIO(b)); print(id,z.namelist()); z.extractall(p/str(id))
 if id==850:
  for f in (p/str(id)).rglob('*.zip'): zipfile.ZipFile(f).extractall(p/str(id))
