import os

# 1. Define household extensions:
mHousehold = f"""from HouseholdFiles.ramsey import StaticNCES, StaticGHH, Ramsey, RamseyGHH"""

from HouseholdFiles._writeClassExtensions import writeMain
for k,v in writeMain.items():
	with open(os.path.join('HouseholdFiles',f'{k}.py'), "w") as f:
		f.write(v['text'])
	mHousehold += f"\nfrom HouseholdFiles.{k} import {', '.join(v['classes'])}"

with open('mHousehold.py', "w") as f:
	f.write(mHousehold)

# 2. Production extensions
