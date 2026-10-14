import importlib.util,json,pathlib,sys
p=pathlib.Path(sys.argv[1]); spec=importlib.util.spec_from_file_location("m",p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
for fn in sys.argv[2:]: print(json.dumps(m.measure(fn,m.SPECS["ui"],pathlib.Path(fn)),allow_nan=False))
