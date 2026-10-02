"""Desk checks for brief 26's read/individual-repair path; no native save claim.

The map fixture distinguishes CObject from Object, with a rope that the old
sweep cannot enumerate. Tests execute the whole dev Lua, not a copied repair.
"""
from pathlib import Path
import subprocess

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'Code/ElevatorDepot_10_ElevatorDepot.lua'

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
logs = {}
function print(...)
  local parts = {}
  for i=1,select('#',...) do parts[i]=tostring(select(i,...)) end
  logs[#logs+1] = table.concat(parts, ' ')
end
function has_log(text)
  for _,line in ipairs(logs) do if line:find(text,1,true) then return true end end
  return false
end
local point_meta = {__eq=function(a,b) return a.px==b.px and a.py==b.py and a.pz==b.pz end,
  __tostring=function(p) return ('(%s,%s,%s)'):format(p.px,p.py,tostring(p.pz)) end}
function point(x,y,z)
  return setmetatable({px=x,py=y,pz=z,x=function(p) return p.px end,
    y=function(p) return p.py end,z=function(p) return p.pz end},point_meta)
end
DefineClass=setmetatable({}, {__newindex=function(t,k,v) rawset(t,k,v); _G[k]=v end})
function Untranslated(s) return s end
OnMsg={}; empty_table={}; guim=100; max_int=2147483647; min_int=-2147483648
Min=math.min; Max=math.max
const={gofPermanent=1}
function IsValid(o) return type(o)=='table' and o.valid==true end
function IsKindOf(o,k) return IsValid(o) and not not o.kinds[k] end
function IsValidThread(t) return type(t)=='table' and t.thread end
function CreateGameTimeThread() return {thread=true} end
function DoneObject(o) o.valid=false; deleted=deleted+1 end
deleted=0
function table.keys(t,sort)
  local keys={}; for k in pairs(t) do keys[#keys+1]=k end
  if sort then table.sort(keys) end; return keys
end
maps={}; objects={}; ObjsToDeleteOnLoadGame={}
function new_map(slot,env)
  local m={slot=slot,env=env}
  function m:MapForEach(area,filter,callback,...)
    -- Measure's radius query supplies (object, radius, class, callback).
    if type(filter)=='number' then filter,callback=callback,... end
    for _,o in ipairs(objects) do
      if o.map==self and IsKindOf(o,filter) then callback(o) end
    end
  end
  maps[#maps+1]=m; return m
end
function AllMapsForEach(...)
  for _,m in ipairs(maps) do m:MapForEach(...) end
end
function GetEnvironment(m) return m.env end
surface=new_map(1,'Surface'); cave=new_map(2,'Underground'); CurrentMap=cave
function obj(class,entity,map,is_object)
  local o={valid=true,class=class,entity=entity,map=map or cave,scale=75,
    pos=point(100,200,10000),parent=nil,attaches={},flags=1,
    kinds={CObject=true,Object=is_object},handle=#objects+1}
  function o:GetEntity() return self.entity end
  function o:GetMap() return self.map end
  function o:GetMapSlot() return self.map.slot end
  function o:GetPos() return self.pos end
  function o:GetVisualPos() return point(self.pos:x(),self.pos:y(),self.pos:z() or 10000) end
  function o:GetScale() return self.scale end
  function o:GetParent() return self.parent end
  function o:GetGameFlags(mask) return mask and (self.flags & mask) or self.flags end
  function o:GetEnumFlags() return 0 end
  function o:ForEachAttach(fn) for _,a in ipairs(self.attaches) do fn(a) end end
  function o:GetEntityBBox() return {IsValid=function() return true end,maxz=function() return 100 end} end
  objects[#objects+1]=o; return o
end
function index_of(o)
  for i,row in ipairs(SMRElevatorDepotDev.inspected_props) do
    if row.object==o then return i end
  end
  error('object omitted from census')
end
terrain={GetHeight=function() return 10000 end}
cameraRTS={GetPosLookAt=function() return point(0,0,22000),point(0,0,10000) end,
  GetZoom=function() return 10 end,GetZoomLimits=function() return 0,1000 end}
''')
lua.execute(SOURCE.read_text(encoding='utf-8'))
lua.execute(r'''
local D=SMRElevatorDepotDev
local ghost=obj('SpaceElevatorRope','SpaceElevatorRope')
local old_seen=false
AllMapsForEach('map','Object',function(o) if o==ghost then old_seen=true end end)
assert(not old_seen,'fixture must reproduce the old filter omission')
local depot=obj('Depot','SMROptInElevatorDepot',cave,true)
depot.kinds.SMROptInElevatorDepotDevBase=true
local owned=obj('SpaceElevatorRope','SpaceElevatorRope')
D.rigs[depot]={ropes={owned}}
local preview=obj('SpaceElevatorRope','SpaceElevatorRope')
D.previews={{ropes={preview}}}
local wonder=obj('SpaceElevator','SpaceElevator',surface,true)
wonder.kinds.SpaceElevatorBase=true
local native=obj('SpaceElevatorRope','SpaceElevatorRope') -- even on another map, ownership wins
wonder.ropes={native}
local attached=obj('SpaceElevatorRope','SpaceElevatorRope')
attached.parent=depot; depot.attaches={attached}
local surfaced=obj('SpaceElevatorRope','SpaceElevatorRope',surface)
local fullsize=obj('SpaceElevatorRope','SpaceElevatorRope'); fullsize.scale=100
local cabin=obj('SpaceElevatorCabin','SpaceElevatorCabin',cave,true)
local shifted=obj('Shapeshifter','SpaceElevatorRope',cave,true)
ObjsToDeleteOnLoadGame[owned]=true
local rows=D.InspectProps()
assert(deleted==0,'inspection must not mutate the world')
assert(has_log('ropes_outside_Object=7'), 'CObject ropes need positive coverage')
assert(has_log('owner=vanilla:'),'vanilla owner must be named')
local attached_rows=0
for _,row in ipairs(rows) do if row.object==attached then attached_rows=attached_rows+1 end end
assert(attached_rows==1,'attachments must not be duplicated')
assert(rows[index_of(shifted)].entity=='SpaceElevatorRope','match entity, not class')
for _,o in ipairs{owned,preview,native,attached,surfaced,fullsize,cabin} do
  assert(not D.RemoveInspectedRope(index_of(o)) and o.valid,'protected object deleted')
end
local i=index_of(ghost)
ghost.pos=point(100,201,10000)
assert(not D.RemoveInspectedRope(i),'moved object is stale')
ghost.pos=point(100,200,10000); ghost.scale=70
assert(not D.RemoveInspectedRope(i),'rescaled object is stale')
ghost.scale=75; ghost.entity='SpaceElevatorCabin'
assert(not D.RemoveInspectedRope(i),'changed entity is stale')
ghost.entity='SpaceElevatorRope'; ghost.map=surface
assert(not D.RemoveInspectedRope(i),'changed map is stale')
ghost.map=cave; D.rigs[depot].ropes[#D.rigs[depot].ropes+1]=ghost
assert(not D.RemoveInspectedRope(i),'new ownership must be read again')
table.remove(D.rigs[depot].ropes)
assert(D.RemoveInspectedRope(i) and not ghost.valid and deleted==1,'exact orphan removal')
assert(not D.RemoveInspectedRope(i),'repeated removal must refuse')
assert(not D.RemoveInspectedRope(9999),'unknown index must refuse')
-- Native log: four parentless tiles exactly overlap four attached/current tiles.
-- A new process loses the inspection indices; Sweep re-identifies the saved set.
local legacy={}
for _,z in ipairs{10000,17500,25000,32500} do
  local o=obj('SpaceElevatorRope','SpaceElevatorRope')
  o.pos=point(384000,303100,z); o.flags=0; legacy[#legacy+1]=o
  local live=obj('SpaceElevatorRope','SpaceElevatorRope')
  live.pos=point(384000,303100,z); live.flags=0; live.parent=depot
  D.rigs[depot].ropes[#D.rigs[depot].ropes+1]=live
end
-- Ownership wins even if a protected prop matches the complete legacy signature.
for _,o in ipairs{owned,preview,native,attached,surfaced,fullsize,cabin,shifted} do
  o.pos=point(384000,303100,10000); o.flags=0
end
preview.smr_depot_prop=true
local unrelated=obj('SpaceElevatorRope','SpaceElevatorRope')
unrelated.pos=point(384001,303100,10000); unrelated.flags=0
local wrong_z=obj('SpaceElevatorRope','SpaceElevatorRope')
wrong_z.pos=point(384000,303100,10001); wrong_z.flags=0
local other_map=obj('SpaceElevatorRope','SpaceElevatorRope',new_map(3,'Underground'))
other_map.pos=point(384000,303100,10000); other_map.flags=0
local permanent=obj('SpaceElevatorRope','SpaceElevatorRope')
permanent.pos=point(384000,303100,10000)
D.inspected_props=nil; logs={}; D.Sweep()
assert(deleted==5,'sweep must remove the four identified tiles only')
assert(has_log('0 props of gone depots and 4 orphaned props'),'native-shaped removal count')
for _,o in ipairs(legacy) do assert(not o.valid,'legacy tile missed') end
for _,o in ipairs{owned,preview,native,attached,surfaced,fullsize,cabin,shifted,unrelated,wrong_z,other_map,permanent} do
  assert(o.valid,'sweep removed a protected or unmatched object')
end
for _,o in ipairs(D.rigs[depot].ropes) do assert(o.valid,'sweep removed a current rope') end
logs={}; D.Sweep()
assert(deleted==5 and has_log('0 props of gone depots and 0 orphaned props'),'repeat sweep must be inert')
-- The historical Measure line subtracted nil from ground for terrain-relative objects.
local lift=obj('ElevatorBase','ElevatorUnderground',cave,true); lift.kinds.ElevatorBase=true
local terrain_relative=obj('Rock','PillarTest',cave,false); terrain_relative.pos=point(1,2)
assert(terrain_relative:GetPos():z()==nil)
logs={}; D.Measure()
assert(has_log('elevators on this map 1') and has_log('PillarTest'),'nil-Z census must finish')
-- Invalid/stale inspection handles do not survive the module's load handler.
OnMsg.LoadGame()
assert(D.inspected_props==nil,'load must invalidate the inspection list')
assert(deleted==5,'load must not apply repairs automatically')
-- Brief 28 (2026-10-01): the placement cursor gets the elevator art and the resting cabin, painted
-- with the template's colours; a foreign or template-less cursor is untouched.
const.efCollision=2; const.efApplyToGrids=4; const.efWalkable=8; const.efSelectable=16
function IsValidEntity(e) return e=='SpaceElevator' or e=='SpaceElevatorCabin' end
local placed={}
function PlaceObjectIn(class,map)
  local o=obj(class,'',map,true); o.cleared=0
  function o:ChangeEntity(e) self.entity=e end
  function o:ClearEnumFlags(m) self.cleared=self.cleared+m end
  function o:ClearGameFlags(m) self.flags=self.flags & ~m end
  function o:SetAttachOffset(p) self.offset=p end
  function o:SetAttachAngle(a) self.angle=a end
  function o:SetScale(s) self.scale=s end
  function o:SetObjectPaletteRecursive(a,b,c,d) self.palette={a,b,c,d} end
  placed[#placed+1]=o; return o
end
function DeleteOnLoadGame(o) ObjsToDeleteOnLoadGame[o]=true end
function GetCurrentColonyColorScheme() return 'Space_Y' end
function GetBuildingColors(ccs,t) assert(ccs=='Space_Y'); return 11,22,33,44 end
local function cursor_for(template)
  local c=obj('CursorBuilding','SMROptInElevatorDepot',surface,true); c.template=template
  function c:GetSpotBeginIndex(name) return name=='Origin' and 0 or -1 end
  function c:Attach(a,spot) a.parent=self; a.spot=spot; self.attaches[#self.attaches+1]=a end
  return c
end
local other=obj('DroneHub','DroneHub',surface,true)
logs={}; OnMsg.CursorBuildingInit(cursor_for(other))
assert(#placed==0 and not has_log('cursor dressed'),'a foreign cursor is untouched')
OnMsg.CursorBuildingInit({})
assert(#placed==0,'a template-less cursor is untouched')
local tmpl=obj('Template','SMROptInElevatorDepot',surface,true); tmpl.kinds.SMROptInElevatorDepotDevBase=true
local c=cursor_for(tmpl); logs={}; OnMsg.CursorBuildingInit(c)
assert(#placed==2 and #c.attaches==2,'the elevator and the cabin hang on the cursor')
assert(placed[1].entity=='SpaceElevator' and placed[2].entity=='SpaceElevatorCabin','the two arts')
for _,o in ipairs(placed) do
  assert(o.scale==75 and o.spot==0 and o.offset==point(0,0,0),'scale 75 at the origin')
  assert(o.palette[1]==11 and o.palette[4]==44,'painted with the template colours')
  assert(o.cleared==30 and o.flags==0,'unselectable, never saved')
end
assert(placed[1].angle==90*60 and placed[1].fx_actor_class=='SpaceElevator','the elevator angle and actor')
assert(has_log('cursor dressed elevator=true cabin=true scale=75 palette=2'),'the cursor log line')
D.layout.cabin_on=false; placed={}; logs={}; OnMsg.CursorBuildingInit(cursor_for(tmpl))
assert(#placed==1 and has_log('cabin=false') and has_log('palette=1'),'cabin_on off leaves the elevator alone')
D.layout.cabin_on=true
''')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
print(f'props_smoke: PASS; HEAD={head} + working tree; {lua.eval("_VERSION")}')
print('Covered: CObject census, exact repair, identified legacy sweep, ownership/signature/stale guards, repeat sweep, nil-Z measurement, load reset, the placement cursor dress.')
