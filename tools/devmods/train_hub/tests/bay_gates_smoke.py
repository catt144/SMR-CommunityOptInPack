"""Vanilla-first regression and mutation controls, with bay_smoke's archived bodies."""
import subprocess
import sys
from lupa import LuaError
from bay_smoke import CODE, ROOT, runtime

CASES = r'''
local B=SMROptInTrainBay
local v=city.labels.Train[1]
B.Tick()
now=B.settle_delay-1; B.Tick()
assert(extras()==0,'settle: no extra before three hours')
now=now+1; B.Tick()
assert(extras()==1,'sustained need can deploy at settle end')
leave(newest())
v.command='Idle'; v.at_station=true
B.Tick()
now=now+B.shortfall_delay*2; B.Tick()
assert(extras()==1,'idle vanilla blocks extras and resets the timer')
v.command='GotoStation'; v.at_station=false
B.Tick()
now=now+B.shortfall_delay-1; B.Tick()
assert(extras()==1,'fresh shortfall must last one full hour')
now=now+1; B.Tick()
assert(extras()==2,'one extra when persistence threshold is met')
leave(newest())
need=0; B.Tick()
need=40*42000; B.Tick()
assert(extras()==2,'recovered need resets persistence')
now=now+B.shortfall_delay; B.Tick()
assert(extras()==3,'persistent demand deploys once per check')
leave(newest())
Msg('LoadGame'); B.Tick()
now=now+B.settle_delay-1; B.Tick()
assert(extras()==3,'reload starts a fresh settle interval')
Msg('CityStart'); B.Tick()
now=now+B.settle_delay-1; B.Tick()
assert(extras()==3,'new game starts a fresh settle interval')
now=now+1; B.Tick()
assert(extras()==4)
leave(newest())
v.command='LoadTrain'; v.at_station=true
B.Tick(); now=now+B.shortfall_delay; B.Tick()
assert(extras()==4,'empty loading reevaluation is not proven work')
v.stockpiled_amount.Metals=1000
B.Tick(); now=now+B.shortfall_delay; B.Tick()
assert(extras()==5,'handling actual cargo counts as work')
'''

def run(code):
    lua = runtime(code)
    lua.execute(CASES)
    # Zero vanilla and a changed route must not inherit old evidence.
    lua = runtime(code)
    lua.execute(r'''
local B=SMROptInTrainBay
for _,t in ipairs(city.labels.Train) do t:AssignToTrack(false) end
B.Tick(); now=B.settle_delay; B.Tick()
assert(extras()==0,'no vanilla: do not substitute extras')
''')
    # Two hub arms / two hubs on one route: a successful request closes that
    # route for the rest of this check, even with the thread still pending.
    lua = runtime(code)
    lua.execute(r'''
local B=SMROptInTrainBay
local h2=setmetatable(station(9),SMROptInTrainHubBase)
h2.first_connector_idx,h2.last_connector_idx=1,1
h2.supply,h2.demand=hub.supply,hub.demand
h2.GetOccupyingTrain=hub.GetOccupyingTrain
local track2=setmetatable({idx=1,city=city,assigned_vehicles={}},TrackBase)
function h2:GetConnectorElement() return {track_obj=track2} end
route=set_route(hub,s1,h2)
city.train_track_routes[track2]=route
route.edges[1].tracks[2]=track2
local original=B.LineNeed
B.LineNeed=function(h,l) return original(hub,l) end
local requests=0
function track:AssignTrain() requests=requests+1 end
track2.AssignTrain=track.AssignTrain
B.Tick(); now=B.settle_delay; B.Tick()
assert(requests==1,'shared route: one request per check across hubs')
''')

def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print('HEAD:', subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip())
    code=CODE.read_text(encoding='utf8')
    run(code)
    print('PASS vanilla-first: settle, continuous shortfall, working state, reset, zero-vanilla and shared route')
    mutations={
        'settle': ('or row.settle > 0', 'or false', 'settle: no extra'),
        'working': ('not row.working', 'false', 'idle vanilla blocks'),
        'persistence': ('GameTime() - shortfall[line.key] < B.shortfall_delay', 'false', 'fresh shortfall'),
        'recovery': ('shortfall[line.key] = nil\n\t\treturn', 'return', 'fresh shortfall'),
        'one-per-line': ('not checked[line.set]', 'true', 'shared route: one request'),
    }
    for name,(before,after,expected) in mutations.items():
        assert before in code
        try:
            run(code.replace(before,after,1))
        except LuaError as exc:
            assert expected in str(exc), str(exc)
            print('PASS mutation rejected:',name)
        else:
            raise AssertionError('surviving mutation: '+name)

if __name__=='__main__':
    main()
