"""Vanilla auto-fill spawn placement, including wrong native lookup.

Geometry uses the hub's actual siding helper, then archived AssignTrain runs through
the bay's real TransportLinkChanged handler. Engine rendering remains an attended check.
"""
import hashlib
import json
import subprocess
import sys
from lupa import LuaRuntime, LuaError
import train_fill_fixture as bay


def geometry():
    traffic = bay.module('traffic_smoke')
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(traffic.STUBS)
    code = traffic.SOURCE.read_text(encoding='utf8')
    lua.execute(code[:code.index('-- Vanilla creates only indices 0..4')])
    lua.execute(traffic.between(code, 'DefineClass.SMROptInTrainHub6Base =', '-- The BuildingTemplate companion'))
    n = lua.execute(r'''
local n=0
for rotation=0,5 do for _,start in ipairs({true,false}) do for k=1,6 do
 local h=newhub(rotation,start)
 local pos,angle=SMROptInTrainFloor.HubSpawnLocation(h,k)
 local stop=h:GetSpotPos(h:GetSpotBeginIndex('Stop'..k))
 assert(pos.xx==stop.xx and pos.yy==stop.yy and pos.zz==stop.zz,'siding target differs from parked Stop')
 local _,out=h:GetSpotAxisAngle(h:GetSpotBeginIndex('Rampdepart'..k))
 assert(angle==out,'target must face out')
 n=n+1
end end end
return n
''')
    print('PASS computed siding geometry: arms x rotations x track ends =', n)
    return lua.eval("function() local h=newhub(0,true); local p,a=SMROptInTrainFloor.HubSpawnLocation(h,1); return p.xx,p.yy,p.zz,a end")()


def placement(code, target):
    lua = bay.runtime(code)
    x,y,z,angle = target
    lua.globals().target = lua.table_from({'x':x,'y':y,'z':z})
    lua.globals().out_angle = angle
    lua.execute(r'''
local B=SMROptInTrainBay
SMROptInTrainFloor.HubSpawnLocation=function(h,idx)
 assert(h==hub and idx==track.idx,'wrong hub/arm')
 return target,out_angle
end
-- Native spawn lookup is deliberately wrong; the final event must place it.
function hub:GetSpotLoc() return 'centre',123 end
route=set_route(hub,s1,station(3)); Msg('TrainRoutesRebuilt'); B.Tick()
local v=newest()
assert(not IsKindOf(v,'HubTrain') and v.command=='LoadTrain')
assert(v.pos==target and v.angle==out_angle,'vanilla spawn must stand on siding facing out')
leave(v)
v.pos='travelling'; Msg('TransportLinkChanged',track,v,'add')
assert(v.pos=='travelling','travelling trains are untouched')
v.at_spawn_track=true; v.current_station=hub
Msg('TransportLinkChanged',track,v,'remove')
assert(v.pos=='travelling','removal does not place a train')
''')


def main():
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]))
    print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=bay.ROOT,text=True).strip())
    asset=bay.ROOT/'Entities/SMROptInTrainHub6.entjson'
    data=json.loads(asset.read_text())['$value']
    spots=[s['name'] for mesh in data['meshDescriptions'] for s in mesh.get('attaches',[])]
    # This guards the rejected baked-Spawn hypothesis against the actual source asset.
    assert len([s for s in spots if s.startswith('Trackconnector')])==6
    assert not [s for s in spots if s.startswith(('Spawn','Stop'))]
    print('asset sha256:',hashlib.sha256(asset.read_bytes()).hexdigest(),
          'connectors=6 Spawn/Stop=0; no baked-spawn cause established')
    target=geometry()
    code=bay.CODE.read_text(encoding='utf8')
    placement(code,target)
    print('PASS final placement: vanilla fill, travelling/removal controls')
    mutant=code.replace('vehicle:SetPos(pos)','-- omitted placement',1)
    try:
        placement(mutant,target)
    except LuaError as exc:
        assert 'vanilla spawn must stand on siding facing out' in str(exc), str(exc)
        print('PASS mutation rejected: no final placement')
    else:
        raise AssertionError('placement mutation survived')
    print('LIVE OWED: spawn log before/target/actual pose plus owner sighting before departure; native cause unresolved')


if __name__=='__main__':
    main()
