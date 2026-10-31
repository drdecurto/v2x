from pathlib import Path
import subprocess
from v2x.credentials import ROOT
p=ROOT/'data/derived/network';p.mkdir(exist_ok=True)
(p/'nodes.nod.xml').write_text('''<nodes>
<node id="s" x="-300" y="0"/><node id="j" x="0" y="0"/>
<node id="m" x="600" y="0"/><node id="d" x="300" y="450"/>
<node id="e" x="900" y="0"/>
</nodes>''')
(p/'edges.edg.xml').write_text('''<edges>
<edge id="approach" from="s" to="j" speed="13.89" numLanes="1"/>
<edge id="main" from="j" to="m" speed="13.89" numLanes="1"/>
<edge id="detour1" from="j" to="d" speed="13.89" numLanes="1"/>
<edge id="detour2" from="d" to="m" speed="13.89" numLanes="1"/>
<edge id="exit" from="m" to="e" speed="13.89" numLanes="1"/>
</edges>''')
subprocess.run([str(ROOT/'.venv/bin/netconvert'),'--node-files',str(p/'nodes.nod.xml'),'--edge-files',str(p/'edges.edg.xml'),'--output-file',str(p/'network.net.xml'),'--no-turnarounds','true'],check=True)
