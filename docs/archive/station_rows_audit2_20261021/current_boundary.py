"""Probe the literal 'current station always' claim against native working-state filtering."""
from pathlib import Path
prior=Path('docs/archive/station_rows_audit_20261021/adversarial.py').read_text(encoding='utf8')
prefix,chunk=prior.split("lua.execute(r'''",1)
exec(compile(prefix,'audit1_runtime_setup','exec'),globals())
lua.execute(chunk.split('-- Junction topology:',1)[0])
def check(runtime, revision):
    print('BOUNDARY REVISION:',revision,flush=True)
    runtime.execute(r'''
for _,working in ipairs({true,false}) do
    local ns,ts,vs=network({60,0},{60,60},{{1,2}})
    assert(D.Set(ns[1],'Metals','export',0)); assert(D.Set(ns[2],'Metals','import',100))
    ns[1].working=working
    local a,c=local_view(vs[1],ts[1]); assert(a and c)
    print('BOUNDARY current working='..tostring(working)..' receiver view='..a[ns[2]].Metals.capacity)
    checked_transfer(vs[1])
    print('BOUNDARY current working='..tostring(working)..' native load='..(vs[1].stockpiled_amount.Metals or 0))
end
''')
check(lua,'3aa5402')
for rev in ['83149ea','5ba8f3f']:
    work=Path.cwd()/'scratch/station_audit2/boundary_versions'/rev
    (work/'Code').mkdir(parents=True,exist_ok=True)
    for name in ['StationRows_10_TrainFloor.lua','StationRows_40_TrainDistribution.lua']:
        code=subprocess.check_output(['git','show',rev+':Code/'+name],text=True,encoding='utf8')
        (work/'Code'/name).write_text(code,encoding='utf8',newline='\n')
    h.MOD=work
    lua=h.runtime()
    lua.execute('TrackConnectedObjBase={}; IsBeingDestructed=function() return false end; const.trfInclusive=1; const.trfPassengerTransport=2; const.trfBidirectional=4; const.trfRunnableOnly=8; table.clear=function(t) for k in pairs(t) do t[k]=nil end end')
    for start,end in [('function TrackConnectedObjBase:ForEachConnectedTrack(', 'function TrackConnectedObjBase:OrientConnectorElements('),('local stations_visited = false','function GetTrainsOnRoute(')]:
        lua.execute(route[route.index(start):route.index(end)])
    lua.execute(chunk.split('-- Junction topology:',1)[0])
    check(lua,rev)
print('NOT RUN: actual inactive-station scheduling or engine reachability; this compares native-walk desk inputs only.',flush=True)
