"""Desk checks for brief 27's wiring of the Elevator Depot pair (surface-owned rows, 2026-10-01); no native claim.

Runs the whole dev Lua under a mock world: two halves (surface, underground),
their per-resource requests, drone controllers and vanilla's Station setters.
Min/Max/Clamp/MulDivRound are integer-only here, as the engine's are (EF-116),
and the WIRING section is gated against a bare '/'. What a mock cannot show
(the panel's look, real drones, real trains, the save file) is the sitting's.
"""
from pathlib import Path
import re
import subprocess

from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
SOURCE = ROOT / 'tools/devmods/elevator_station/Code/10_ElevatorDepotDev.lua'
text = SOURCE.read_text(encoding='utf-8')

# Gate: no float division in the wiring (engine int/int is int; lupa would hide a float).
wiring = text[text.index('-- ==== WIRING'):]
code = re.sub(r'--[^\n]*', '', wiring)
code = re.sub(r'"(?:\\.|[^"\\])*"', '""', code)
assert '/' not in code, 'bare / in the WIRING section'

lua = LuaRuntime(unpack_returned_tuples=True)
lua.execute(r'''
logs = {}
function print(...)
  local parts = {}
  for i=1,select('#',...) do parts[i]=tostring(select(i,...)) end
  logs[#logs+1] = table.concat(parts, ' ')
end
function has_log(t) for _,l in ipairs(logs) do if l:find(t,1,true) then return l end end return false end
local function int(v, what) assert(math.type(v)=='integer', (what or 'value')..' must be an integer: '..tostring(v)) return v end
function Min(a,b) int(a,'Min a'); int(b,'Min b'); return a<b and a or b end
function Max(a,b) int(a,'Max a'); int(b,'Max b'); return a>b and a or b end
function Clamp(v,lo,hi) int(v,'Clamp'); return Max(lo, Min(v, hi)) end
function MulDivRound(a,b,c)
  int(a,'MulDivRound a'); int(b,'MulDivRound b'); int(c,'MulDivRound c')
  local x = a*b
  if x >= 0 then return (x + c//2)//c end
  return -((-x + c//2)//c)
end
local point_meta = {__eq=function(a,b) return a.px==b.px and a.py==b.py and a.pz==b.pz end,
  __add=function(a,b) return point(a.px+b.px,a.py+b.py,(a.pz or 0)+(b.pz or 0)) end,
  __tostring=function(p) return ('(%s,%s,%s)'):format(p.px,p.py,tostring(p.pz)) end}
function point(x,y,z)
  return setmetatable({px=x,py=y,pz=z,x=function(p) return p.px end,
    y=function(p) return p.py end,z=function(p) return p.pz end},point_meta)
end
DefineClass=setmetatable({}, {__newindex=function(t,k,v) rawset(t,k,v); _G[k]=v end})
OnMsg={}; empty_table={}; guim=100; max_int=2147483647; min_int=-2147483648
const={gofPermanent=1, efVisible=2, ResourceScale=1000, MinuteDuration=500}
now=0
function GameTime() return now end
function IsValid(o) return type(o)=='table' and o.valid==true end
function IsKindOf(o,k) return type(o)=='table' and o.kinds and not not o.kinds[k] end
function IsValidThread(t) return type(t)=='table' and t.thread end
threads = {}
function CreateGameTimeThread(fn, ...) local t={thread=true, fn=fn, args={...}}; threads[#threads+1]=t; return t end
function DeleteThread(t) t.thread=false end
function DoneObject(o) o.valid=false end
function ObjModified(o) modified=(modified or 0)+1 end
function Untranslated(s) return s end
function PlayFX() end
function empty_func() end
function IsValidEntity() return false end   -- the load handler re-dresses; no art in this mock
function Sleep() end
function table.keys(t,sort)
  local keys={}; for k in pairs(t) do keys[#keys+1]=k end
  if sort then table.sort(keys) end; return keys
end
function table.copy(t) local c={}; for k,v in pairs(t) do c[k]=v end; return c end
function table.find(t,v) for i,x in ipairs(t) do if x==v then return i end end end
maps={}
function new_map(slot,env)
  local m={slot=slot,env=env}
  function m:MapForEach() end
  maps[#maps+1]=m; return m
end
function AllMapsForEach(area, class, fn) for _,o in ipairs(UIColony.labels.SMROptInElevatorDepotDev) do if IsKindOf(o,class) then fn(o) end end end
function GetEnvironment(m) return m.env end
surface_map=new_map(1,'Surface'); cave=new_map(2,'Underground'); CurrentMap=surface_map
UIColony={labels={SMROptInElevatorDepotDev={}}, underground_map_unlocked=true}
function UIColony:IsUpgradeUnlocked() return true end
RESOURCES={'Concrete','Metals','Polymers'}

-- vanilla's Station setters, as the depot calls them (Station.lua:964-995, :1021-1051)
accept_calls, desired_calls = 0, 0
g_Classes={Station={
  SetAcceptResourceState=function(o,res,state,broadcast)
    assert(not broadcast, 'the wiring never broadcasts')
    accept_calls=accept_calls+1; o.enabled[res] = state ~= 'disabled'
  end,
  SetDesiredAmount=function(o,dial) desired_calls=desired_calls+1; int(dial,'dial'); o.desired_amount=dial end,
}}

function request(res, amount, flag)
  local r={res=res, amount=amount, assigned=0, flag=flag}
  function r:GetResource() return self.res end
  function r:GetActualAmount() return self.amount end
  function r:GetTargetAmount() return self.amount-self.assigned end
  function r:AddAmount(n) int(n,'AddAmount'); self.amount=self.amount+n end
  return r
end

handles=100
function depot(map, stock)
  handles=handles+1
  local o={valid=true, handle=handles, map=map, kinds={SMROptInElevatorDepotDevBase=true, Building=true},
    supply={}, demand={}, enabled={}, storable_resources={}, desired_amount=10000, working=true,
    command_centers={}, reconnects=0, interrupts=0, city={}}
  for _,res in ipairs(RESOURCES) do
    o.storable_resources[#o.storable_resources+1]=res
    local n=(stock and stock[res] or 0)*1000
    o.supply[res]=request(res, n, 'supply'); o.demand[res]=request(res, 60000-n, 'demand'); o.enabled[res]=true
  end
  o.maintenance=request('Metals', 0, 'demand')
  setmetatable(o, {__index=SMROptInElevatorDepotDevBase})
  function o:GetMap() return self.map end
  function o:GetMapSlot() return self.map.slot end
  function o:IsResourceEnabled(res) return self.enabled[res] end
  function o:GetMaxStorage(res) return 60000 end
  -- Keep this legacy fixture small; the revision smoke below uses native resize/upgrade bodies.
  function o:SetBase(prop,value) self['base_'..prop]=value end
  function o:AddResource(n,res) int(n,'AddResource'); self.supply[res]:AddAmount(n); self.demand[res]:AddAmount(-n) end
  function o:InterruptDrones(cc_filter, filter)
    for _,cc in ipairs(self.command_centers) do for _,d in ipairs(cc.drones) do
      if filter(d) then self.interrupts=self.interrupts+1; d.d_request=false; d.s_request=false end
    end end
  end
  function o:DisconnectFromCommandCenters() self.reconnects=self.reconnects+1 end
  function o:ConnectToCommandCenters() end
  function o:IsValidPos() return true end
  function o:DestroyAttaches() end
  function o:GetAttaches() return {} end
  function o:GetVisualPos() return point(1,2,3) end
  function o:GetAngle() return 0 end
  table.insert(UIColony.labels.SMROptInElevatorDepotDev, o)
  if SMRElevatorDepotDev and SMRElevatorDepotDev.HalfPlaced then SMRElevatorDepotDev.HalfPlaced(o) end  -- GameInit's call
  return o
end
function stock(o,res) return o.supply[res]:GetActualAmount()//1000 end
function minute_tick(n) for i=1,n do now=now+500; OnMsg.NewMinute(0, (now//500) % 60) end end
function to_hour() while (now//500) % 60 ~= 59 do now=now+500 end end  -- the next tick is minute 0
stockpiles={}
function PlaceResourceStockpile_Delayed(pos, map, res, amount) int(amount,'stockpile'); stockpiles[#stockpiles+1]={map=map,res=res,amount=amount} end
''')
lua.execute(text)
lua.execute(r'''
local D = SMRElevatorDepotDev
local Base = SMROptInElevatorDepotDevBase
assert(D.layout.cabin_leg_minutes==60 and D.layout.cabin_capacity==250 and D.layout.row_words=='station')
D.layout.cabin_capacity=42 -- legacy small fixture; production capacities exercised separately

-- 1 a lone half: no pair, no cabin, a plain station to a hub, build limits
local S = depot(surface_map, {Metals=30, Concrete=20})
assert(D.PairOf()==nil and D.TwinOf(S)==nil, 'a lone half is not a pair')
assert(D.HubEntry(S,'Metals')==false and D.HubEntry({kinds={}},'Metals')==nil, 'hub read: lone=false, non-depot=nil')
CurrentMap=surface_map; assert(Base.CanBuildOnlyOnce({})==true, 'a depot on the surface: build once')
CurrentMap=cave; assert(Base.CanBuildOnlyOnce({})==false, 'none underground yet: buildable')
local locks={}; OnMsg.GetAdditionalBuildingLocks({template_name='SMROptInElevatorDepotDev'}, locks)
assert(locks.smr_depot_needs_underground==false, 'unlocked underground: no lock')
UIColony.underground_map_unlocked=false; locks={}
OnMsg.GetAdditionalBuildingLocks({class='SMROptInElevatorDepotDev'}, locks)
assert(locks.smr_depot_needs_underground==true, 'locked underground hides the depot')
locks={}; OnMsg.GetAdditionalBuildingLocks({template_name='DroneHub'}, locks)
assert(locks.smr_depot_needs_underground==nil, 'other templates untouched')
UIColony.underground_map_unlocked=true

-- 2 the pair forms; every unset row is Import; Drone Access default off re-registers both halves once
local U = depot(cave, {Metals=0})
local hub = {kinds={DroneControl=true}, drones={}}
S.command_centers={hub}; U.command_centers={hub}
D.Tick(5)
assert(has_log('pair formed: surface '..S.handle..' underground '..U.handle), 'pair formed line')
assert(S.reconnects==1 and U.reconnects==1, 'first tick re-registers both halves (old fixtures pick up the default)')
for _, res in ipairs(RESOURCES) do
  assert(D.State(S,res)=='to_underground' and D.State(U,res)=='to_underground' and S.enabled[res] and U.enabled[res]
    and D.RowWord(U,res)=='import', 'an unset row is Import, vanilla storage on (old Balanced rows load this way): '..res)
end
assert(next(rawget(S,'SMROptIn_depot_rows'))==nil, 'nothing stored for the default')
-- Not accepted is stored explicitly; the later sections keep Concrete and Polymers Not accepted
assert(D.SetRow(S,'Concrete','disabled') and D.SetRow(S,'Polymers','disabled'))
assert(rawget(S,'SMROptIn_depot_rows').Concrete=='disabled' and rawget(U,'SMROptIn_depot_rows').Polymers=='disabled'
  and U.enabled.Concrete==false and S.enabled.Polymers==false, 'explicit Not accepted, copied, vanilla off')
-- an earlier build's explicit "disabled" still reads Not accepted; an unknown stored value reads as the default
assert(D.State(S,'Concrete')=='disabled')
D.Tick(6); assert(S.reconnects==1, 'no repeat re-registration')
CurrentMap=cave; assert(Base.CanBuildOnlyOnce({})==true, 'one per map: the underground is now taken')

-- 3 Drone Access: off refuses storage requests to drone controllers only; one switch per half
local lr_map = surface_map
assert(S:ShouldAddRequestToCommandCenter(S.supply.Metals, hub)==false, 'off: storage supply refused')
assert(S:ShouldAddRequestToCommandCenter(S.demand.Metals, hub)==false, 'off: storage demand refused')
assert(S:ShouldAddRequestToCommandCenter(S.maintenance, hub)==true, 'off: maintenance stays vanilla')
assert(S:ShouldAddRequestToCommandCenter(S.supply.Metals, lr_map)==true, 'shuttles (a map) untouched')
local drone={d_request=S.demand.Metals}; hub.drones={drone}
assert(D.SetDroneAccess(S, true) and rawget(S,'SMROptIn_depot_drones')==true, 'on is stored')
assert(S.reconnects==2 and S.interrupts==1 and drone.d_request==false, 'toggle resets drones on storage, re-registers')
assert(S:ShouldAddRequestToCommandCenter(S.supply.Metals, hub)==false and S:ShouldAddRequestToCommandCenter(S.demand.Metals, hub)==true,
  'on + Import (the default): drones bring in only')
assert(S:ShouldAddRequestToCommandCenter(S.supply.Concrete, hub)==true, 'on + Not accepted: vanilla rules')
assert(rawget(U,'SMROptIn_depot_drones')==nil, 'each half has its own toggle')
Base.ToggleDroneAccess(U, true)   -- Ctrl+click is a plain click: drone hubs are per map
assert(rawget(U,'SMROptIn_depot_drones')==true and rawget(S,'SMROptIn_depot_drones')==true, 'U on, S untouched (was on)')
Base.ToggleDroneAccess(S, true)
assert(rawget(S,'SMROptIn_depot_drones')==nil and rawget(U,'SMROptIn_depot_drones')==true, 'Ctrl on S changes S only')
Base.ToggleDroneAccess(S)
assert(rawget(S,'SMROptIn_depot_drones')==true, 'both on again')

-- 4 rows: one setting and ONE word for the pair, written on the surface only (owner, 2026-10-01)
assert(D.SetRow(S,'Metals','import'))
assert(D.State(S,'Metals')=='to_underground' and D.State(U,'Metals')=='to_underground', 'the underground reads the surface')
assert(S.enabled.Metals and U.enabled.Metals, 'a chosen row enables vanilla storage on both halves')
assert(rawget(U,'SMROptIn_depot_rows').Metals==nil and rawget(U,'SMROptIn_depot_rows').Concrete=='disabled', 'its read-only copy follows (Import stored as absence)')
assert(D.RowWord(S,'Metals')=='import' and D.RowWord(U,'Metals')=='import', 'one word on both panels: Import = goes down')
assert(D.HalfWord(S,'Metals')=='gather' and D.HalfWord(U,'Metals')=='hand_out', 'the flows behind it')
assert(S.transport_policy.Metals=='send' and U.transport_policy.Metals=='accept', 'drone desires follow the flow')
assert(S:ShouldAddRequestToCommandCenter(S.demand.Metals, hub)==true and S:ShouldAddRequestToCommandCenter(S.supply.Metals, hub)==false,
  'on + gathering half: drones bring in only')
assert(U:ShouldAddRequestToCommandCenter(U.supply.Metals, hub)==true and U:ShouldAddRequestToCommandCenter(U.demand.Metals, hub)==false,
  'on + handing-out half: drones take out only')
local h = D.HubEntry(S,'Metals'); assert(h.mode=='import' and h.percent==17, 'hub reads the surface Import at its target (unset: the dial, 10 of 60)')
h = D.HubEntry(U,'Metals'); assert(h.mode=='export' and h.percent==0, 'the underground hands out everything')
assert(D.HubEntry(S,'Concrete')==false, 'Not accepted: the hub default (vanilla storage is off)')
-- the underground cannot write: console refused, a click does nothing
local ok, why = D.SetRow(U,'Metals','import')
assert(not ok and why:find('surface Elevator Depot'), 'SetRow on the underground refused')
logs={}; Base.ToggleAcceptResource(U,'Metals')
assert(D.State(S,'Metals')=='to_underground' and has_log('underground rows are read-only; change Metals'), 'an underground click writes nothing')
assert(not D.SetRow(S,'Metals','balanced'), 'Balanced is gone')
-- the arrows: down = it goes down, on both panels
assert(Base.GetResAcceptIcon(S,'Metals'):find('down') and Base.GetResAcceptIcon(U,'Metals'):find('down'), 'down on both')
local ut = Base.ResourceRolloverText(U,'Metals')
assert(ut:find('^Import %(set on the surface Elevator Depot%)%. Arrives here') and ut:find('use the surface Elevator Depot')
  and not ut:find('Export'), 'the underground infotip: the surface word, the flow, where to change it; no inverted word')
assert(Base.ResourceRolloverText(S,'Metals'):find('^Import'), 'the surface rollover leads with the same word')
-- surface click cycle, the hub's order without Balanced: Import -> Not accepted -> Export -> Import
Base.ToggleAcceptResource(S,'Metals'); assert(D.State(U,'Metals')=='disabled' and U.enabled.Metals==false, 'Not accepted shows underground')
Base.ToggleAcceptResource(S,'Metals')
assert(D.State(U,'Metals')=='to_surface' and Base.GetResAcceptIcon(U,'Metals'):find('up') and D.RowWord(U,'Metals')=='export'
  and Base.ResourceRolloverText(U,'Metals'):find('^Export %(set on the surface Elevator Depot%)%. Leaves this half'), 'Export = comes up, on both')
Base.ToggleAcceptResource(S,'Metals'); assert(D.State(S,'Metals')=='to_underground', 'and back to Import')
D.layout.row_words='elevator'
Base.ToggleAcceptResource(S,'Metals')   -- vanilla order: to_underground -> disabled
Base.ToggleAcceptResource(S,'Metals'); Base.ToggleAcceptResource(S,'Metals')
assert(D.State(U,'Metals')=='to_underground', 'elevator cycle: disabled -> to_surface -> to_underground')
assert(Base.ResourceRolloverText(S,'Metals'):find('Status: Underground') and Base.ResourceRolloverText(U,'Metals'):find('^Status: Underground'),
  'elevator words on both panels')
D.layout.row_words='station'
assert(Base.GetResAcceptStateText(U,'Metals')=='Underground')
-- the witness: the underground panel shows what the surface row says
D.SetRow(S,'Concrete','export')
logs={}; local out = D.Pair()
assert(out.underground_panel=='matches' and out.copy=='current' and has_log('0 differ; read-only copy current'), 'panel witness')
local shown, expected, tip_ok = D.UndergroundPanel(U, S, 'Metals'); assert(shown=='down' and expected=='down' and tip_ok)
U.enabled.Concrete=false   -- something switched the underground's vanilla storage off behind the depot
logs={}; out = D.Pair(); assert(out.underground_panel=='DIFFERENT' and has_log('u_panel=off,Not accepted(surface says up) TITLE-WRONG DIFFERENT'), 'the witness can fail')
-- vanilla's "apply to all" never writes the setting: vanilla is put back to the surface row
Base.SetAcceptResourceState(U,'Concrete','store')
assert(U.enabled.Concrete==true and D.State(S,'Concrete')=='to_surface', 'a broadcast store re-applies the row')
Base.SetAcceptResourceState(S,'Concrete','disabled')
assert(S.enabled.Concrete==true and D.State(S,'Concrete')=='to_surface', 'a broadcast disable does not write the row')
D.SetRow(S,'Concrete','disabled')
logs={}; out = D.Pair(); assert(out.underground_panel=='matches', 'matches again')
rawget(U,'SMROptIn_depot_rows').Metals = 'to_surface'   -- a stale copy is reported, the panel still reads the surface
out = D.Pair(); assert(out.copy=='STALE' and out.underground_panel=='matches', 'stale copy reported')
rawset(U,'SMROptIn_depot_rows', table.copy(rawget(S,'SMROptIn_depot_rows')))
-- the rows in the hub's station-row shape: title, slider (surface), read-only underground
function box(a,b,c,d) return {a,b,c,d} end
UIL = {MeasureText=function(word) return #word * 10 end}
local function win(id)
  local w = {Id=id}
  for _, m in ipairs{'SetDock','SetMaxWidth','SetMinWidth','SetMaxHeight','SetShorten'} do
    w[m] = function(self, v) self['_'..m] = v end
  end
  return w
end
sliders = {}
InfopanelSlider = {new=function(self, args, parent, context)
  local sl = {args=args, parent=parent, idBar={win('bar'), win('knob')}, enabled=true}
  sl.idBar.SetMinWidth = function(self, v) self.min=v end
  function sl:SetEnabled(v) self.enabled=v end
  function sl:GetEnabled() return self.enabled end
  function sl:SetScroll(v) self.scroll=v end
  function sl:GetScroll() return self.scroll end
  function sl:Open() self.window_state='open' end
  function sl:UpdateProgress() self.progressed=true end
  sliders[#sliders+1] = sl
  return sl
end}
function T(t) return t end
local row_class = {OnContextUpdate=function(self, ctx) self.updated=(self.updated or 0)+1 end}
sectionStorageRow = row_class
assert(D.InstallRowHook() and D.InstallRowHook(), 'installed once')
local function row_for(o, res)
  local r = setmetatable({context={o, res=res}, window_state='open'}, {__index=row_class})
  local line = {}
  r.idSectionTitle = win('title'); r.idSectionTitleRight = win('right')
  r.idSectionTitle.parent, r.idSectionTitleRight.parent = line, line
  r.idSectionTitle.font_height, r.idSectionTitle.scale = 20, {xy=function() return 1000, 1000 end}
  function r.idSectionTitle:GetFontId() return 1 end
  function r.idSectionTitle:GetPadding() return {minx=function() return 2 end, maxx=function() return 2 end, miny=function() return 1 end, maxy=function() return 1 end} end
  function r:SetTitle(t) self.title=t; self.idSectionTitle.text=t[1] end
  function r:SetRolloverOnFocus(v) self.focus=v end
  function r:SetRolloverHint(t) self.hint=t end
  function r:SetRolloverHintGamepad(t) self.pad=t end
  function r:SetRolloverText(t) self.rollover=t end
  function r:OnActivate() self.activated=true end
  return r
end
assert(D.State(S,'Metals')=='to_underground')
local sr, ur = row_for(S,'Metals'), row_for(U,'Metals')
sr:OnContextUpdate(sr.context); ur:OnContextUpdate(ur.context)
assert(sr.updated==1 and ur.updated==1, 'vanilla row update ran first')
assert(sr.rollover==D.RowText(S,'Metals') and ur.rollover==D.RowText(U,'Metals'), 'both actual controls receive their current tooltip')
-- The displayed control, not just the object method: missing twins on either
-- map, then re-pairing on an already-open row. This is presentation only.
S.destroyed=true; D.InvalidatePair(); ur:OnContextUpdate(ur.context)
assert(ur.rollover:find('^No surface twin:') and ur.rollover:find('setting is kept for the next surface depot',1,true))
S.destroyed=false; U.destroyed=true; D.InvalidatePair(); sr:OnContextUpdate(sr.context)
assert(sr.rollover:find('^No underground twin:'))
U.destroyed=false; D.InvalidatePair()
sr:OnContextUpdate(sr.context); ur:OnContextUpdate(ur.context)
assert(not sr.rollover:find('No underground twin',1,true) and not ur.rollover:find('No surface twin',1,true))
assert(sr.title[1]=='<resource(res)> · Import' and sr.title[2]==sr.context, 'surface title: the hub string, verbatim shape')
assert(sr.hint=='<left_click> Not accepted' and sr.pad=='<ButtonA> Not accepted', 'surface hint: the next word, as the hub')
local sl = sr.depot_slider
assert(sl and sl.args.Id=='idDistributionSlider' and sl.args.Min==0 and sl.args.Max==100 and sl.args.StepSize==1, 'the hub slider')
assert(sl.window_state=='open' and sl.enabled and sl.scroll==D.Target(S,'Metals') and sl.progressed, 'opened, enabled, at the target')
assert(sr.idSectionTitleRight._SetDock=='right' and sr.idSectionTitle._SetDock=='left' and sr.idSectionTitle._SetShorten==true, 'the hub layout')
assert(math.type(sr.idSectionTitle._SetMinWidth)=='integer' and sr.idSectionTitle._SetMinWidth>=154, 'fit_title in integers')
assert(ur.title[1]=='<resource(res)> · Import' and ur.depot_slider==nil, 'underground: the same title, the same word, no slider')
assert(ur.hint:find('surface Elevator Depot') and ur.pad, 'underground read-only hint')
ur:OnActivate(); assert(not ur.activated, 'the underground row does not act')
sr:OnActivate(); assert(sr.activated, 'the surface row still cycles')
-- the slider writes the target on the surface; the underground copy follows; refreshing saves nothing
logs={}; sl.args.OnScroll(sl, 64)
assert(D.Target(S,'Metals')==64 and rawget(U,'SMROptIn_depot_targets').Metals==64 and has_log('target Metals = 64%'), 'slider -> target, copy')
sr:OnContextUpdate(sr.context); assert(#sliders==1 and sl.scroll==64, 'one slider per row, at the new target')
local hs = D.HubEntry(S,'Metals'); assert(hs.mode=='import' and hs.percent==64, 'the hub reads the surface target')
assert(Base.ResourceRolloverText(S,'Metals'):find('Slider: 64% of current capacity (38).', 1, true), 'the hub slider line in the infotip')
assert(not D.SetTarget(U,'Metals',10), 'no target from the underground')
assert(select(2, D.SetTarget(S,'Metals',101))=='slider must be 0 to 100 percent', 'the hub bounds message')
-- Not accepted: red X and red text are vanilla's; the title word and a disabled slider are the hub's
D.SetRow(S,'Metals','disabled'); sr:OnContextUpdate(sr.context); ur:OnContextUpdate(ur.context)
assert(sr.title[1]=='<resource(res)> · Not accepted' and not sl.enabled and ur.title[1]=='<resource(res)> · Not accepted', 'Not accepted')
sl.args.OnScroll(sl, 5); assert(D.Target(S,'Metals')==64, 'a disabled row saves no target')
D.SetRow(S,'Metals','import')
local out2 = D.Pair(); assert(out2.underground_panel=='matches' and has_log('target=64%'), 'witness includes the title word')
assert(not D.SetRow(S,'Water','import'), 'unknown resource refused')
assert(not D.SetRow(S,'Metals','sideways'), 'unknown mode refused')

-- 5 the cabin: first leg on the hour, down then up, nothing crosses while it travels; only rows that send
assert(D.State(S,'Metals')=='to_underground' and D.State(S,'Concrete')=='disabled')
to_hour(); minute_tick(1)
local rec = rawget(S,'SMROptIn_depot_cabin')
assert(rec.phase=='down' and rec.cargo.Metals==30000 and rec.cargo.Concrete==nil,
  'down leg loads all Import Metals (30); Not accepted Concrete never crosses')
assert(stock(S,'Metals')==0 and stock(U,'Metals')==0, 'nothing crosses while it travels')
assert(has_log('cabin departed down (leg 1) loaded Metals=30000'))
minute_tick(59); assert(rec.phase=='down' and stock(U,'Metals')==0, 'still travelling at 59 min')
minute_tick(1)
assert(stock(U,'Metals')==30 and U.supply.Concrete.amount==0, 'arrival hands the cargo to the underground half')
assert(rec.legs==1 and rec.phase=='up', 'arrived and left again: one leg per hour, pause 0')
assert(has_log('cabin arrived underground (leg 1) delivered Metals=30000'))
-- capacity is shared and the carried direction loads first
D.SetRow(S,'Concrete','export')    -- surface Export = underground Import = carried up
U.supply.Concrete.amount=50000; U.demand.Concrete.amount=10000
S.supply.Concrete.amount=10000; S.demand.Concrete.amount=50000   -- room for 50 on the surface
minute_tick(60)
assert(rec.phase=='down' and rec.legs==2, 'up leg arrived')
-- the up leg left at the previous hour, before Concrete was restocked: it carried nothing
assert(stock(S,'Concrete')==10, 'nothing arrived on the empty up leg')
minute_tick(60)  -- down leg: Metals is to_underground but surface has none; Concrete goes up only
minute_tick(1)
assert(rec.phase=='up' and rec.cargo.Concrete==42000, 'capacity caps the up load at 42 units')
-- room at the destination: what does not fit rides back and is delivered where it came from
S.supply.Concrete.amount=50000; S.demand.Concrete.amount=10000   -- surface has 10 units of room
minute_tick(59)
assert(stock(S,'Concrete')==60 and rec.cargo.Concrete==32000, '10 fit, 32 stay aboard')
assert(has_log('still aboard Concrete=32000'))
-- the next down leg carries the 32 back to the underground half
local before_u = stock(U,'Concrete')
minute_tick(60)
assert(stock(U,'Concrete')==before_u+32 and rec.cargo.Concrete==nil, 'leftover returned to its origin')
for _,o in ipairs{S,U} do for _,res in ipairs(RESOURCES) do
  assert(math.type(o.supply[res].amount)=='integer' and o.supply[res].amount>=0, 'integer, non-negative stock')
end end
-- a half switched off holds the cabin at the end it reached
local legs=rec.legs; U.working=false
minute_tick(120)
assert(rec.legs==legs+1 and has_log('cabin held: surface working true underground working false'), 'held after arriving')
U.working=true; minute_tick(1); assert(rec.phase=='down' or rec.phase=='up', 'resumes')

-- 6 the cabin art follows the legs (integers only)
local rig={bld=S, base=point(0,0,1000), far=point(0,0,-5000), cabin={valid=true}}
local urig={bld=U, base=point(0,0,1000), far=point(0,0,31000), cabin={valid=true}}
rec.phase, rec.leg_ms, rec.ends = 'down', 30000, now+15000
local z, moving = D.FollowTarget(rig); assert(z==-2000 and moving, 'surface cabin halfway down: '..tostring(z))
z = D.FollowTarget(urig); assert(z==16000, 'underground cabin halfway down from the ceiling')
rec.phase='at_bottom'; assert(D.FollowTarget(rig)==-5000 and D.FollowTarget(urig)==1000, 'at the bottom')
rec.phase='at_top'; assert(D.FollowTarget(rig)==1000 and D.FollowTarget(urig)==31000, 'at the top')

-- Not accepted never crosses, whatever the stock and the target
assert(D.State(S,'Polymers')=='disabled'); D.SetTarget(S,'Polymers',50)
S.supply.Polymers.amount, S.demand.Polymers.amount = 0, 60000
U.supply.Polymers.amount, U.demand.Polymers.amount = 40000, 20000
rec.phase, rec.ends, rec.started, rec.cargo = 'at_bottom', now, true, {}
minute_tick(1)
assert(rec.phase=='up' and rec.cargo.Polymers==nil, 'an up leg carries no Not accepted Polymers')
-- 7 the pair read
logs={}; local out = D.Pair()
assert(has_log('pair surface='..S.handle) and has_log('rows=read-only') and has_log('row Metals') and out.underground_panel=='matches', 'Pair() read')
assert(out[S.handle].drones==true and out.legs==rec.legs)

-- 8 a half demolished mid-leg: the cargo goes to the survivor; overflow becomes a stockpile
rec.phase, rec.ends, rec.cargo = 'down', now+1000, {Metals=20000, Concrete=5000}
S.supply.Metals.amount=55000; S.demand.Metals.amount=5000   -- room for 5 of the 20 Metals
local rows_before = table.copy(rawget(U,'SMROptIn_depot_rows'))
logs={}; Base.Done(U)
-- surface Concrete is full (60 of 60): all 5 Concrete and 15 of the Metals become stockpiles
assert(stock(S,'Metals')==60 and #stockpiles==2 and stockpiles[1].res=='Concrete' and stockpiles[1].amount==5000
  and stockpiles[2].res=='Metals' and stockpiles[2].amount==15000 and stockpiles[2].map==surface_map,
  '5 Metals fit; the rest is stockpiled beside the survivor')
assert(rec.phase=='at_top' and next(rec.cargo)==nil, 'the cabin resets at the surface')
assert(has_log('half gone: underground '..U.handle..' survivor '..S.handle), 'half gone line')
U.valid=false; table.remove(UIColony.labels.SMROptInElevatorDepotDev, table.find(UIColony.labels.SMROptInElevatorDepotDev, U))
now=now+500; D.Tick(1)
assert(has_log('no pair: surface '..S.handle), 'the pair is broken')
local z, moving = D.FollowTarget(rig)
assert(z==rig.base:z() and moving==false, 'the orphan surface cabin rests at its landing')
rig.elevator={valid=true}; D.rigs[S]=rig
OnMsg.SaveGameDone()
assert(rig.thread.fn==D.FollowLoop, 'an orphan restarts the schedule follower, never the display cycle')
D.rigs[S]=nil
assert(D.HubEntry(S,'Metals')==false and D.HalfWord(S,'Metals')=='plain', 'the survivor works as a plain station')
assert(D.State(S,'Metals')=='to_underground', 'and keeps its row for the next twin')
assert(S:ShouldAddRequestToCommandCenter(S.supply.Metals, hub)==true, 'unpaired + on: both ways')
-- a new twin adopts the survivor's rows
local U2 = depot(cave)
now=now+500; D.Tick(2)
assert(D.State(U2,'Metals')=='to_underground' and D.HalfWord(U2,'Metals')=='hand_out' and D.RowWord(U2,'Metals')=='import', 'the new twin adopts the rows')
for k,v in pairs(rows_before) do assert(D.State(U2,k)==v, 'row '..k..' adopted') end
assert(rawget(U2,'SMROptIn_depot_targets').Metals==64, 'the new underground half gets the targets copy')
assert(rawget(U2,'SMROptIn_depot_drones')==nil, 'Drone Access starts off on the new half')
-- a further depot on a taken map stays unpaired
local extra = depot(cave); logs={}; D.HalfPlaced(extra)
assert(has_log('pair limit: a further depot on the Underground map'), 'extra warned')
assert(D.TwinOf(extra)==nil and D.TwinOf(U2)==S, 'the first by handle stays paired')
-- the surface half destroyed: its cabin cargo goes underground
local srec = rawget(S,'SMROptIn_depot_cabin'); srec.cargo={Concrete=3000}
local u2c = stock(U2,'Concrete'); S.destroyed=true
Base.OnDestroyed(S)
assert(stock(U2,'Concrete')==u2c+3, 'destroyed surface hands its cargo down')
Base.Done(S)   -- the ruin cleared later: nothing twice
assert(stock(U2,'Concrete')==u2c+3)
urig.bld=U2; D.InvalidatePair()
z, moving = D.FollowTarget(urig)
assert(z==urig.base:z() and moving==false, 'the orphan underground cabin rests at its landing')

-- 9 an old save: halves without any field; the load handler resets runtime state
local S3 = depot(surface_map); S3.handle=1   -- lowest handle on the surface: pairs with U2
S.valid=false
OnMsg.LoadGame(); logs={}
now=now+500; D.Tick(3)
assert(has_log('pair formed: surface 1 underground '..U2.handle), 're-formed after load')
assert(S3.reconnects==1 and U2.reconnects>=2, 'every half re-registers once after a load')
assert(D.State(S3,'Metals')=='to_underground', 'the old surface half adopts the underground rows')
local t3, set3 = D.Target(S3,'Metals'); assert(t3==64 and set3 and rawget(S3,'SMROptIn_depot_targets').Metals==64, 'and its targets copy')

-- 10 the panel button sits after Shuttle Access
local host = {window_state='open'}
local function win(id) local w={Id=id, ZOrder=1, parent=host}; function w:SetZOrder(z) self.ZOrder=z end; host[#host+1]=w; return w end
local prio, onoff, lrt, salvage = win('prio'), win('onoff'), win('ToggleLRTServiceButton'), win('idSalvage')
local dlg = {kinds={ipBuilding=true}, context=S3, host}
function ResolvePropObj(c) return c end
function IsMassUIModifierPressed() return false end
function RebuildInfopanel() end
InfopanelButton = {new=function(self, args, parent, context)
  local b = win(args.Id); for k,v in pairs(args) do b[k]=v end; b.context=context
  function b:Open() self.window_state='open' end
  function b:OnContextUpdate(c) c[self.OnPressParam..'_Update'](c, self) end
  function b:SetIcon(i) self.icon=i end
  function b:SetRolloverImageColor(c) self.color=c end
  function b:SetRolloverText(t) self.text=t end
  return b
end}
dlg[1]=host
D.AttachDroneButton(dlg)
local b = host[5]
assert(b and b.Id=='idSMRDepotDroneAccess' and b.window_state=='open', 'button created and opened')
assert(b.ZOrder==2 and salvage.ZOrder==3 and lrt.ZOrder==1 and prio.ZOrder==1, 'ordered right after Shuttle Access')
assert(b.color=='red' and b.text:find('OFF') and b.icon=='UI/IconsRemaster/IPButtons/drone_balacing_off.tga',
  'off by default: the red-filled vanilla icon, red rollover (StorageDepot.lua:306-314 shape)')
assert(b.Icon==b.icon, 'created with the off icon, no plain-hex flash')
b:OnPress(false); b:OnContextUpdate(S3)
assert(rawget(S3,'SMROptIn_depot_drones')==true and b.color=='green' and b.icon=='UI/IconsRemaster/IPButtons/drone_balacing_on.tga',
  'pressed: the green-filled vanilla icon, green rollover')
D.AttachDroneButton(dlg); assert(host[6]==nil, 'never twice')
-- the hub's panel-scale floor, copied (45_TrainDistributionUI.lua:239-269): a depot panel's scale is clamped
local scaler = {kinds={XSizeConstrainedWindow=true}}
scaler.AdjustConstrainedScale = function(self, x, y) return x, y end
function scaler:InvalidateMeasure() self.invalid=true end
local dlg2 = {kinds={ipBuilding=true}, context=S3, scaler}
OnMsg.DialogOpen(dlg2)
local sx, sy = scaler:AdjustConstrainedScale(500, 900)
assert(scaler.depot_scale and scaler.invalid and sx==800 and sy==900, 'the floor clamps a depot panel to 800')
local wrapped = scaler.AdjustConstrainedScale; OnMsg.DialogOpen(dlg2); assert(scaler.AdjustConstrainedScale==wrapped, 'wrapped once')
local other = {kinds={XSizeConstrainedWindow=true}}; other.AdjustConstrainedScale = function(self, x, y) return x, y end
OnMsg.DialogOpen({kinds={ipBuilding=true}, context={kinds={}}, other}); assert(not other.depot_scale, 'a non-depot panel is untouched')
''')
# 10b: both title helpers now use the same integer ceiling and slack (b551930).
# Check both with engine integer arithmetic and native per-value pixel scaling.
HUB_UI = ROOT / 'tools/devmods/train_hub/Code/45_TrainDistributionUI.lua'
hub_text = HUB_UI.read_text(encoding='utf-8')
start = hub_text.index('local FIT_SLACK = 2')
end = hub_text.index('\nend\n', hub_text.index('local function fit_title(title)', start)) + len('\nend\n')
hub_fit = hub_text[start:end].replace('local function fit_title(title)', 'hub_fit_title = function(title)')
assert ' / ' not in hub_fit, 'the hub title fit uses integer helpers'
lua.execute(hub_fit)
lua.execute(r"""
local D = SMRElevatorDepotDev
local PAD = 3
local function title(text, sx, sy)
  local t = {text=text, font_height=(36 * sy) // 1000, scale={xy=function() return sx, sy end}}
  function t:GetFontId() return 1 end
  function t:GetPadding() return {minx=function() return PAD end, maxx=function() return PAD end, miny=function() return PAD end, maxy=function() return PAD end} end
  function t:SetMinWidth(v) self.minw=v end
  function t:SetMaxWidth(v) self.maxw=v end
  function t:SetMaxHeight(v) self.maxh=v end
  return t
end
local cur_sx = 1000
UIL = {MeasureText=function(word) return (#word * 17 * cur_sx) // 1000 + 3 end}
local function px(units, sc) return (units * sc) // 1000 end   -- ScaleXY, truncating
local function fits(t, sx, sy)
  local h = px(t.maxh, sy) - 2 * px(PAD, sy) >= 2 * t.font_height
  local w = true
  for word in t.text:gmatch('%S+') do
    if px(t.maxw, sx) - 2 * px(PAD, sx) < UIL.MeasureText(word) + 1 then w = false end
  end
  return h and w
end
local n, hub_short, hub_1000_ok = 0, 0, true
for _, text in ipairs{'Exotic Minerals · Not accepted', 'Rare Metals · Balanced', 'Metals · Import', 'Machine Parts · Export'} do
  for sc = 800, 2200, 50 do
    cur_sx = sc
    local a, b = title(text, sc, sc), title(text, sc, sc)
    hub_fit_title(a); D.FitTitle(b)
    assert(fits(b, sc, sc), ('the depot box loses a line or a word at scale %d: %s (maxh %d)'):format(sc, text, b.maxh))
    assert(b.maxh >= a.maxh and b.maxw >= a.maxw and b.maxh < a.maxh + 36, 'never smaller than the hub, never a third line')
    assert(math.type(b.maxw)=='integer' and math.type(b.maxh)=='integer')
    if not fits(a, sc, sc) then hub_short = hub_short + 1 end
    if sc == 1000 and not fits(a, sc, sc) then hub_1000_ok = false end
    n = n + 1
  end
end
fit_cases, hub_short_cases, hub_1000 = n, hub_short, hub_1000_ok
""")
assert lua.eval('fit_cases') == 116
assert lua.eval('hub_1000'), "the hub's box fits at scale 1000, as the hub station showed"
assert lua.eval('hub_short_cases') == 0, 'the repaired hub title fit must hold at every sampled scale'
print('fit_title: depot and hub fit in all', lua.eval('fit_cases'), 'cases across scale 800..2200')

# 11 the staged sitting slots run against the same world (the kit itself is mocked)
SLOTS = ROOT / 'tools/devmods/elevator_station/tests/80_AgentSlots_depot.lua.txt'
lua.execute(r'''
slots, triggers, armed_runs = {}, {}, {}
SMRTK = {armed={}, error_count=0,
  Bind=function(n,label,fn,opts) slots[n]={label=label,fn=fn,opts=opts} return true end,
  BindScratch=function(label,fn,opts) slots.scratch={label=label,fn=fn,opts=opts} return true end,
  Trigger=function(spec) triggers[spec.id]=spec return spec end,
  Arm=function(id, ...) local st={}; local r,why=triggers[id].prepare({state=st}, ...); if r==false then return false,{reason=why} end
    SMRTK.armed[id]={state=st}; return true, r end,
  Disarm=function(id) SMRTK.armed[id]=nil end,
  Run=function(id) armed_runs[#armed_runs+1]=id return true, {} end}
function GetTimeFactor() return 0 end
const.HourDuration=30000
marks=0
function ctx_for(sel) return {sel=sel, mark=function(l) marks=marks+1 return marks end, log=function() end, state={}} end
''')
lua.execute(SLOTS.read_text(encoding='utf-8'))
lua.execute(r'''
local D = SMRElevatorDepotDev
local s, u = D.PairOf()
assert(s and u, 'a pair for the slots')
local r = slots.scratch.fn(ctx_for(nil)); assert(r.surface==tostring(s.handle) and r.underground==tostring(u.handle), 'scratch read')
local before = u.supply.Metals:GetActualAmount()
r = slots[1].fn(ctx_for(u)); assert(r.added_tenths==200 and u.supply.Metals:GetActualAmount()==before+20000, 'slot 1 stocks 20')
assert(select(1, slots[1].fn(ctx_for({kinds={}})))==false, 'slot 1 refuses a non-depot')
r = slots[3].fn(ctx_for(u)); assert(r.word==D.RowWord(u,'Metals') and r.word==D.RowWord(s,'Metals') and r.twin_word==nil and r.twin==tostring(s.handle), 'slot 3 read: one word, no inverted twin word')
assert(r.panel_shows==r.surface_says and r.infotip_ok=='true' and r.copy_current=='true' and r.title_ok=='true' and r.title_word==D.RowWord(u,'Metals'), 'slot 3 proves the underground panel')
r = slots[3].fn(ctx_for(s)); assert(r.target_percent==D.Target(s,'Metals') and r.title_word==D.RowWord(s,'Metals'), 'slot 3 reads the surface row and target')
r = slots.scratch.fn(ctx_for(nil)); assert(r.underground_panel=='matches' and r.copy=='current', 'scratch carries the witness')
r = slots[5].fn(ctx_for(nil)); assert(r.halves==2, 'slot 5 read')
-- slot 6 then slot 2 on a real leg: the departure read shows the cargo aboard and on neither half
D.SetRow(s,'Metals','export')                 -- surface Export: carried up
local rec = rawget(s,'SMROptIn_depot_cabin'); rec.phase, rec.ends, rec.started = 'at_bottom', now, true
r = slots[6].fn(ctx_for(nil)); assert(r.trigger=='depot_next_departure' and armed_runs[#armed_runs]=='speed_ultra')
local st = SMRTK.armed.depot_next_departure.state
local fired, f = triggers.depot_next_departure.when({state=st}); assert(not fired, 'not yet')
minute_tick(1)
fired, f = triggers.depot_next_departure.when({state=st})
assert(fired and f.verdict=='departed' and f.cabin=='up' and f.aboard_Metals>=200 and f.u_Metals==0, 'departure witness')
SMRTK.Disarm('depot_next_departure')   -- the kit disarms a once-trigger after it fires
r = slots[2].fn(ctx_for(nil)); st = SMRTK.armed.depot_next_arrival.state
minute_tick(60)
fired, f = triggers.depot_next_arrival.when({state=st})
assert(fired and f.verdict=='arrived' and f.aboard_Metals==0, 'arrival witness')
SMRTK.Disarm('depot_next_arrival')
r = slots[4].fn(ctx_for(s)); st = SMRTK.armed.depot_drone_hour.state
assert(r.drone_access=='on' and r.half==tostring(s.handle))
minute_tick(60); fired, f = triggers.depot_drone_hour.when({state=st})
assert(fired and f.verdict=='hour_done' and f.samples>=2, 'drone hour')
''')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
print(f'wiring_smoke: PASS; HEAD={head} + working tree; {lua.eval("_VERSION")}')
print('Covered: pair/limits/lock, Drone Access filter and per-half toggles, surface-owned rows and the '
      'read-only underground panel (marks, infotip, row hook, witness) in both vocabularies, station-shaped rows (title, slider, targets, one word for the pair, no Balanced, scale floor), hourly cabin legs/capacity/room/hold, cabin art positions, Pair() read, '
      'half demolished/destroyed/re-placed, extra depot, old-save load, panel button order, both actual twinless row tooltips, the staged slots, both title helpers hold two lines at every scale; no bare /.')
