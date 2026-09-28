"""Auto-fill, no extras, and old bay snapshot compatibility (mocked engine)."""
import subprocess
import sys
from train_fill_fixture import CODE, ROOT, runtime

print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]))
print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip())
code = CODE.read_text(encoding='utf8')
for forbidden in ['StoreForSave', 'RestoreAfterSave', 'function HubTrain:Idle',
                  'function GetTrainsOnRoute', 'function TrackBase:CanAddVehicle',
                  'LineNeed', 'try_extra', 'ChangeClass(']:
    assert forbidden not in code, forbidden
lua = runtime()
lua.execute(r'''
local B=SMROptInTrainBay
local p=pool()
B.Tick(); now=const.HourDuration*24; B.Tick()
assert(extras()==0 and pool()==p,'need alone never deploys an extra')
route=set_route(hub,s1,station(3)); Msg('TrainRoutesRebuilt'); B.Tick()
local v=newest()
assert(v.command=='LoadTrain' and not IsKindOf(v,'HubTrain') and pool()==p-1)
leave(v); B.Tick(); assert(pool()==p-1,'one auto-fill per join')
assert(GetTrainsOnRoute(track)==3 and not track:CanAddVehicle(),'normal cap honored')
-- Pool unavailable at join: retry during the existing window, never exceed the cap.
city.available_prefabs.Train=0
route=set_route(hub,s1,station(4),station(5)); Msg('TrainRoutesRebuilt'); B.Tick()
assert(#city.labels.Train==3)
city.available_prefabs.Train=4; B.Tick()
assert(#city.labels.Train==4 and pool()==3)
leave(newest())
-- Old loaded HubTrain object: class exists; cargo, passengers and assigned work stay.
local old=PlaceObjectIn('HubTrain',hub)
old:AssignToTrack(track); old.current_station=s1
old.stockpiled_amount.Metals=42000; old.units={'passenger'}
old.assigned_resources={[s1]={Metals=42000}}
assert(HubTrain.Idle==Train.Idle and HubTrain.persist_baseclass=='Train')
old:Idle()
assert(old.idled and not old.invalid and old.stockpiled_amount.Metals==42000)
assert(GetTrainsOnRoute(track)==5,'legacy extras now count toward the route cap')
local before=pool(); PersistGame('snapshot')
assert(pool()==before and next(ObjsToDeleteOnLoadGame)==nil,'no save-time storing')
-- A snapshot made by the OLD bay already credited its pool and marked empties.
-- Vanilla still owns both the marker and its loader; no new bay hook is required.
local empty=PlaceObjectIn('HubTrain',hub); empty:AssignToTrack(track)
DeleteOnLoadGame(empty); city:AddPrefabs('Train',1,false)
local credited=pool()
Msg('PersistPostLoad')
Msg('LoadGame')
assert(empty.invalid and pool()==credited,'old snapshot deletes empties without crediting twice')
assert(IsValid(old) and old.stockpiled_amount.Metals==42000 and #old.units==1)
-- Load establishes a baseline and does not add a train to an old route.
B.Tick(); assert(pool()==credited)
''')
print('PASS auto-fill, cap, pool retry, legacy class/cargo/passengers, old delete-on-load snapshot')
