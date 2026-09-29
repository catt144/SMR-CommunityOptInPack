"""Distribution desk smoke using archived vanilla bodies, with native request doubles.

No engine/drone/UI/save serialization claim. No fenced hub file is loaded.
"""
from pathlib import Path
import hashlib
import re
import subprocess
import sys
from lupa import LuaRuntime

ROOT = Path(__file__).resolve().parents[4]
MOD = ROOT / "tools/devmods/train_hub"
ARCHIVE = ROOT.parent / "SMR-Shared/SMR-SrcArchive/1.1.1.405907/Src/Lua"


def source_parts(lua, name, sections):
    path = ARCHIVE / name
    text = path.read_text(encoding="utf8")
    print("source:", name, "sha256:", hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    chunks = [text[text.index(start):text.index(end, text.index(start))]
              for start, end in sections]
    if name == "Units/Train.lua":
        # Engine integer resource arithmetic (EF-116). All divisions in these
        # pinned bodies are nonnegative resource amounts / scale. Fail closed
        # if an archive change introduces another shape. Never edit the archive.
        body = "\n".join(chunks)
        assert body.count("/ scale") == 12
        assert body.count("/") == 12
        chunks = [body.replace("/ scale", "// scale")]
        print("arithmetic: Train.lua resource divisions use // scale (12 sites)", flush=True)
    lua.execute("local ResourceScale=const.ResourceScale\n"
                "local rfSuspended=const.rfSuspended\n"
                "local rfPostInQueue=const.rfPostInQueue\n"
                "local rfStorageDepot=const.rfStorageDepot\n" + "\n".join(chunks))


def runtime(before_mods=None):
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(r'''
Min=function(a,b) if a==nil then return b end if b==nil then return a end return math.min(a,b) end
Max=math.max
Clamp=function(n,a,b) return math.min(math.max(n,a),b) end
MulDivRound=function(a,b,c)
    assert(c~=0,'Division by zero')
    return math.floor(a*b/c+0.5)
end
const={ResourceScale=1000,trfInclusive=1,trfBidirectional=2,rfSuspended=1,rfPostInQueue=2,rfStorageDepot=4}
empty_table={}; Train={}; MultiResourceCubeVisuals={}; MultiResourceDepotBase={}
Station=setmetatable({}, {__index=MultiResourceDepotBase})
SavegameFixups={}; g_Classes={Station={desired_amount=10000}}
OnMsg={}; ObjModified=function() end; GameTime=function() return 0 end
IsValid=function(o) return type(o)=='table' and not o.invalid end
IsKindOf=function(o,c) return o and (o.class==c or (c=='Station' and o.hub) or (c=='SMROptInTrainHubBase' and o.hub)) end
table.find=function(t,v) for i,x in ipairs(t) do if x==v then return i end end end
table.copy=function(t) local r={} for k,v in pairs(t) do r[k]=v end return r end
-- Engine table.keys accepts nil (1.1.1.405907 CommonLua/LuaExportedDocs/Global/table.lua:215-226).
table.keys=function(t) local r={} for k in pairs(t or empty_table) do r[#r+1]=k end return r end
ripairs=function(t) local i=#t+1 return function() i=i-1 if i>0 then return i,t[i] end end end
bor=function(a,b) return a|b end
GetLRManager=function() end
GetNextConnectedStation=function(st) return st end
ForEachTrainInRoute=function(track,fn) for _,t in ipairs(track.trains) do fn(t) end end
GetRouteDist=function() return 1 end
ForEachStationAlongTrack=function(st,track,flags,fn,...)
    for _,s in ipairs(track.members) do
        if flags~=0 or s~=st then fn(s,'cargo',...) end
    end
end
AllMapsForEach=function(_,_,fn) for _,s in ipairs(UIColony.labels.Station) do fn(s) end end
GroupResourcesForIP=function() return {} end
function request(actual,desired)
    return {actual=actual,target=actual,desired=desired,flags=4,
        GetActualAmount=function(r) return r.actual end,
        GetTargetAmount=function(r) return r.target end,
        GetDesiredAmount=function(r) return r.desired end,
        SetDesiredAmount=function(r,n) r.desired=n end,
        SetAmount=function(r,n) r.actual=n r.target=n end,
        CanAssignUnit=function(r,n) return n>0 and n<=r.target end,
        AssignUnit=function(r,n)
            if r.reject or not r:CanAssignUnit(n) then return false end
            r.target=r.target-n return true
        end,
        UnassignUnit=function(r,n,f) assert(not f) r.target=r.target+n end,
        IsAnyFlagSet=function(r,f) return r.flags&f~=0 end,
        AddFlags=function(r,f) r.flags=r.flags|f end,
        ClearFlags=function(r,f) r.flags=r.flags&~f end,
        SetReciprocalRequest=function() end,
    }
end
RequestAssignUnit=function(r,_,n) return r:AssignUnit(n) end
RequestUnassignUnit=function(r,_,n,f) r:UnassignUnit(n,f) end
function Station:BuildingUpdate() end
function station(stock,cap,hub)
    local st=setmetatable({class='Station',hub=hub,handle=hub and 1 or 2,
        max_storage_per_resource=cap*1000,desired_amount=10000,desire_slider_max=cap,
        storable_resources={'Metals','Food',Metals=true,Food=true},
        waiting_for_train={},transport_policy={},stockpiled_amount={},visual_cubes={},
        has_demand_request=true,command_centers={},
        supply={Metals=request(stock*1000,10000),Food=request(0,10000)},
        demand={Metals=request((cap-stock)*1000,cap*1000-10000),Food=request(cap*1000,cap*1000-10000)}}, {__index=Station})
    function st:ResourceRequestsEnabled() return true end
    function st:RecalculateCapacityColumns() end
    function st:RecalculateDerivedMaxZ() end
    function st:ReallocateVisualColumns() end
    function st:RebuildInfopanel() end
    function st:RebuildResourceGroupsForIP() end
    function st:InterruptDrones() end
    function st:DisconnectFromCommandCenters() end
    function st:ConnectToCommandCenters() end
    function st:AddSupplyRequest(res,n,flags,_,want) return request(n,want) end
    function st:AddDemandRequest(res,n,flags,_,want) return request(n,want) end
    function st:AddResource(n,res)
        for _,p in ipairs({{self.supply[res],n},{self.demand[res],-n}}) do
            p[1].actual=p[1].actual+p[2]; p[1].target=p[1].target+p[2]
        end
    end
    if hub then
        function st:GetTrainExportFloor() return self.reserve or 0,true end
        function st:HubTrackGraph() return self.nodes end
    end
    return st
end
function fixture(stock,hubstock,cap,hubcap)
    local s,h=station(stock,cap),station(hubstock,hubcap,true)
    local track={members={s,h},trains={}}
    function track:GetDestStation(st) return st==s and h or s end
    local city={train_track_routes={[track]=track.members},labels={Station=track.members}}
    s.city=city;h.city=city;h.nodes={[s]=true,[h]=true}
    -- Colony holds aggregate labels; routes belong to the map's City.
    UIColony={labels=city.labels}
    local t=setmetatable({current_station=s,track=track,city=city,
        stockpiled_amount={},assigned_resources={},units={},is_stopping=false}, {__index=Train})
    function t:GetEmptyStorage() local n=0 for _,v in pairs(self.stockpiled_amount) do n=n+v end return 1000000-n end
    function t:AddResource(n,r) self.stockpiled_amount[r]=(self.stockpiled_amount[r] or 0)+n end
    function t:LogCargo() end
    function t:PushDestructor() end
    function t:PopDestructor() end
    track.trains={t}
    if SMROptInTrainDistribution then SMROptInTrainDistribution.Refresh() end
    return t,s,h
end
function stock(st,res) return st.supply[res or 'Metals']:GetActualAmount() end
function deliver(t,dest) t.current_station=dest; t:UnloadAll() end
function checked_transfer(t)
    t:TransferCargo(nil,true)
    assert(not SMROptInTrainFloor.stats.last_error,SMROptInTrainFloor.stats.last_error)
    assert(not SMROptInTrainDistribution.error,SMROptInTrainDistribution.error)
end
''')
    source_parts(lua, "Buildings/MultiResourceCubeVisuals.lua", [
        ("function MultiResourceCubeVisuals:SetCount(", "function MultiResourceCubeVisuals:SetCountSharedPool("),
        ("function MultiResourceCubeVisuals:GetMaxStorage(", "MultiResourceCubeVisuals.AddDepotResource ="),
        ("function MultiResourceCubeVisuals:RegisterResourceRequest(", "function MultiResourceCubeVisuals:FinalizePendingRemoval("),
    ])
    lua.execute('''
MultiResourceDepotBase.GetMaxStorage=MultiResourceCubeVisuals.GetMaxStorage
MultiResourceDepotBase.SetCount=MultiResourceCubeVisuals.SetCount
MultiResourceDepotBase.GetMaxStorageForAnyOneResource=MultiResourceCubeVisuals.GetMaxStorageForAnyOneResource
MultiResourceDepotBase.RegisterResourceRequest=MultiResourceCubeVisuals.RegisterResourceRequest
''')
    source_parts(lua, "Buildings/MultiResourceDepot.lua", [
        ("function MultiResourceDepotBase:UpdateRequestCapacity(", "function MultiResourceDepotBase:ToggleAcceptResource("),
        ("function MultiResourceDepotBase:RecalculateAfterResourceListChange(", "function MultiResourceDepotBase:ResourceRequestsEnabled("),
    ])
    source_parts(lua, "Buildings/Station.lua", [
        ("function Station:SetDesiredAmount(", "function Station:SetAcceptResourceState("),
        ("function Station:SetAcceptResourceState(", "function Station:TrainTraverse("),
    ])
    # The fixup is the final function in this archived file.
    station_source=(ARCHIVE/'Buildings/Station.lua').read_text(encoding='utf8')
    lua.execute(station_source[station_source.index('function SavegameFixups.RevertStationDesiredAmount()'):])
    source_parts(lua, "Units/Train.lua", [
        ("local ttPrioBalance =", "function Train:LogCargo"),
        ("function Train:TransferCargo(", "function Train:OnContinuousTaskTick("),
    ])
    lua.execute("vanilla_transfer=Train.TransferCargo")
    if before_mods:
        before_mods(lua)
    for name in ["10_TrainFloor.lua", "40_TrainDistribution.lua"]:
        path = MOD / "Code" / name
        lua.execute(path.read_text(encoding="utf8"))
        print(name, "sha256:", hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    lua.execute("assert(SMROptInTrainDistribution.active,SMROptInTrainDistribution.error)")
    return lua


def main():
    print("command:", subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print("HEAD:", subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(), flush=True)
    items=(MOD/'items.lua').read_text(encoding='utf8')
    metadata=(MOD/'metadata.lua').read_text(encoding='utf8')
    explicit=re.findall(r"'CodeFileName', \"([^\"]+)\"",items)
    code=re.search(r"'code', \{(.*?)\n\t\},",metadata,re.S)[1]
    registered=re.findall(r'"([^\"]+)"',code)
    assert [p for p in registered if not p.endswith('.generated.lua')]==explicit
    assert explicit.count('Code/45_TrainDistributionUI.lua')==1
    parser=LuaRuntime()
    for name in ['Code/10_TrainFloor.lua','Code/40_TrainDistribution.lua','Code/45_TrainDistributionUI.lua','metadata.lua','items.lua']:
        parser.compile((MOD/name).read_text(encoding='utf8'),name=name)
    print('PASS owned dev Lua parses; code registration agrees with ModItemCode source',flush=True)
    lua=runtime()
    lua.execute(r'''
local D,F=SMROptInTrainDistribution,SMROptInTrainFloor
assert(ResourceScale==nil)
-- Untouched spokes use their live absolute dial without creating settings.
do
    local train,spoke,hub=fixture(48,177,120,480)
    checked_transfer(train)
    assert(stock(spoke)==10000,'untouched Balanced must retain 10, got '..stock(spoke))
    deliver(train,hub)
    local other=station(0,120);other.handle=3;other.city=spoke.city
    table.insert(train.track.members,other);hub.nodes[other]=true;D.Refresh()
    checked_transfer(train);deliver(train,other)
    assert(stock(other)==10000 and stock(hub)==205000)
    spoke:SetDesiredAmount(25000)
    train.current_station=hub;checked_transfer(train);deliver(train,spoke)
    assert(stock(spoke)==25000 and stock(hub)==190000)
    spoke:SetDesiredAmount(5000)
    checked_transfer(train);deliver(train,hub)
    assert(stock(spoke)==5000 and stock(hub)==210000)
    for _,st in ipairs(train.track.members) do
        st.max_storage_per_resource=st.max_storage_per_resource*2
        st:OnModifiableValueChanged('max_storage_per_resource')
    end
    checked_transfer(train)
    assert((train.stockpiled_amount.Metals or 0)==0)
    assert(stock(spoke)==5000 and stock(other)==10000 and stock(hub)==210000)
    assert(spoke.supply.Metals.desired==5000 and other.supply.Metals.desired==10000)
    OnMsg.SaveGameStart();OnMsg.SaveGameDone();OnMsg.LoadGame()
    for _,st in ipairs(train.track.members) do
        assert(rawget(st,D.FIELD)==nil)
        assert(st.supply.Metals.target==stock(st))
        assert(st.demand.Metals.target==st.demand.Metals.actual)
    end
    print('PASS untouched spokes: 10 each, remainder at hub; dial 25 then 5; doubling keeps absolute 5/10; no saved settings or claims')
end
-- Disconnected lines and disabled rows still follow vanilla.
for _,kind in ipairs({'outside','disabled'}) do
    local function run(native)
        local train,spoke,hub=fixture(48,177,120,480)
        if kind=='outside' then hub.nodes[spoke]=nil;D.Refresh() end
        if kind=='disabled' then spoke:SetAcceptResourceState('Metals','disabled') end
        if native then vanilla_transfer(train,nil,true) else checked_transfer(train) end
        assert(rawget(hub,D.FIELD)==nil and rawget(spoke,D.FIELD)==nil)
        return stock(spoke),train.stockpiled_amount.Metals or 0,spoke.supply.Metals.target
    end
    local a,b,c=run(true);local x,y,z=run(false)
    assert(a==x and b==y and c==z,kind..' differs from vanilla')
end
-- Existing cargo respects the default on a hub line. A disconnected train
-- retains vanilla unloading.
for _,on_line in ipairs({true,false}) do
    local train,spoke,hub=fixture(9,0,120,480)
    train.stockpiled_amount.Metals=2000;train.assigned_resources[spoke]={Metals=2000}
    assert(spoke.demand.Metals:AssignUnit(2000))
    if not on_line then train.track.members={spoke} end
    deliver(train,spoke)
    assert(stock(spoke)==(on_line and 9000 or 11000))
    assert(train.stockpiled_amount.Metals==(on_line and 2000 or 0))
    if on_line then deliver(train,hub);assert(stock(hub)==2000) end
    assert(rawget(hub,D.FIELD)==nil)
end
do
    local train,spoke,hub=fixture(0,30,120,480)
    assert(spoke.demand.Metals:AssignUnit(4000))
    train.current_station=hub;checked_transfer(train)
    assert(train.stockpiled_amount.Metals==6000)
    deliver(train,spoke);assert(stock(spoke)==6000 and spoke.demand.Metals.target==110000)
    assert(rawget(hub,D.FIELD)==nil)
end
print('PASS untouched scope: disconnected/disabled vanilla controls; old cargo capped only on hub lines; reservations reduce orders')
local function chain(child_stock,middle_stock,hub_stock)
    local trunk,middle,hub=fixture(middle_stock,hub_stock,120,480)
    local child=station(child_stock,120);child.handle=6243;child.city=middle.city
    middle.handle=2012;hub.handle=1000
    middle.city.labels.Station={middle,hub,child};hub.nodes[child]=true
    local spur={members={child,middle},trains={}}
    function spur:GetDestStation(st) return st==child and middle or child end
    middle.city.train_track_routes[spur]=spur.members
    local train=setmetatable({current_station=child,track=spur,city=middle.city,
        stockpiled_amount={},assigned_resources={},units={},is_stopping=false,
        GetEmptyStorage=trunk.GetEmptyStorage,AddResource=trunk.AddResource,
        LogCargo=trunk.LogCargo,PushDestructor=trunk.PushDestructor,
        PopDestructor=trunk.PopDestructor},{__index=Train})
    spur.trains={train};D.Refresh()
    assert(D.Parent(child)==middle and D.Parent(middle)==hub)
    return train,trunk,child,middle,hub
end
for _,mode in ipairs({'export','balanced','untouched'}) do
    local spur,trunk,child,middle,hub=chain(60,10,0)
    if mode~='untouched' then assert(D.Set(child,'Metals',mode,20)) end
    checked_transfer(spur)
    assert(stock(child)==(mode=='untouched' and 10000 or 24000),mode..' child='..stock(child))
    deliver(spur,middle)
    assert(stock(middle)==(mode=='untouched' and 60000 or 46000),mode..' middle='..stock(middle))
    if mode=='balanced' then
        OnMsg.SaveGameStart();OnMsg.SaveGameDone();OnMsg.LoadGame()
        assert(stock(middle)==46000 and D.Parent(child)==middle)
    end
    checked_transfer(trunk);deliver(trunk,hub)
    assert(stock(middle)==10000 and stock(hub)==(mode=='untouched' and 50000 or 36000))
    assert(D.CallsFor(child)>0 and D.CallsFor(middle)>0)
end
do
    local spur,trunk,child,middle,hub=chain(0,10,100)
    assert(D.Set(child,'Metals','import',25))
    trunk.current_station=hub;checked_transfer(trunk);deliver(trunk,middle)
    assert(stock(middle)==40000,'import middle='..stock(middle))
    spur.current_station=middle;checked_transfer(spur);deliver(spur,child)
    assert(stock(child)==30000 and stock(middle)==10000 and stock(hub)==70000,
        'import child='..stock(child)..' middle='..stock(middle)..' hub='..stock(hub))
end
do
    local spur,trunk,child,middle,hub=chain(60,10,480)
    assert(D.Set(child,'Metals','export',20))
    checked_transfer(spur)
    assert(stock(child)==60000 and stock(middle)==10000 and stock(hub)==480000)
end
do
    local spur,trunk,small,big,hub=chain(10,50,0)
    big.handle=2009
    local direct={members={small,hub},trains={}}
    big.city.train_track_routes[direct]=direct.members
    D.Refresh()
    assert(D.Parent(small)==hub and D.Parent(big)==hub)
    assert(D.Set(big,'Metals','balanced',20))
    checked_transfer(spur)
    assert(stock(big)==50000 and stock(small)==10000,
        'the sideways line must not erase either row')
    checked_transfer(trunk);deliver(trunk,hub)
    assert(stock(big)==24000 and stock(hub)==26000)
end
do
    local spur,trunk,child,middle,hub=chain(0,24,100)
    assert(D.Set(middle,'Metals','import',20))
    assert(D.Set(child,'Metals','import',25))
    trunk.current_station=hub;checked_transfer(trunk);deliver(trunk,middle)
    assert(stock(middle)==54000)
    spur.current_station=middle;checked_transfer(spur);deliver(spur,child)
    assert(stock(middle)==24000 and stock(child)==30000)
end
print('PASS one-hop chain: Export/Balanced/untouched forward excess, Import fills through 2012, full hub refuses')
print('PASS dual-line 2009 uses direct hub route; sideways line keeps both pins; Import intermediate passes transit')
-- Covered drones leave milliresource stock. With an order of 400, the old
-- view contributes desire=1 and storage=0 to the archived train allocator.
do
    local train,spoke,hub=fixture(60,114,120,480)
    spoke:AddResource(-400,'Metals');hub:AddResource(-500,'Metals')
    spoke.command_centers={{CanCommandDrones=function() return true end,IsInWorkRange=function() return true end}}
    assert(D.Set(spoke,'Metals','import',50) and D.HasDroneCoverage(spoke))
    train.current_station=hub
    checked_transfer(train)
    assert(stock(spoke)==59600 and stock(hub)==113500)
    assert((train.stockpiled_amount.Metals or 0)==0)
    assert(spoke.demand.Metals.target==60400 and hub.supply.Metals.target==113500)
    print('PASS covered sub-unit order: desire/storage safe, order=400, spoke=59600, hub=113500, claims released')
end
-- Both directions and the whole-unit boundary: rounding capacity up must not
-- create cargo, overfill an order, or retain a temporary request reservation.
for _,order in ipairs({0,1,400,999,1000,1400}) do
    for _,mode in ipairs({'import','balanced','export'}) do
        local train,spoke,hub=fixture(60,114,120,480)
        local dest,source
        if mode=='export' then
            hub:AddResource(366000-order,'Metals');dest=hub;source=spoke
        else
            spoke:AddResource(-order,'Metals');dest=spoke;source=hub
            train.current_station=hub
        end
        assert(D.Set(spoke,'Metals',mode,50))
        -- Export needs source stock above its floor.
        if mode=='export' then spoke:AddResource(10000,'Metals') end
        local before,from=stock(dest),stock(source)
        local load=(order//1000)*1000
        checked_transfer(train)
        assert((train.stockpiled_amount.Metals or 0)==load)
        assert(stock(source)==from-load and stock(dest)==before)
        deliver(train,dest)
        assert(not D.error and stock(dest)==before+load)
        assert(dest.demand.Metals.target==dest.demand.Metals.actual)
        assert(source.supply.Metals.target==stock(source))
        train.current_station=source;checked_transfer(train)
        assert((train.stockpiled_amount.Metals or 0)==0)
    end
end
print('PASS order boundaries 0/1/400/999/1000/1400: import, balanced, export; exact demand cap and return stop')
-- Native UnloadAll uses unscaled demand, not the allocator's divided capacity.
-- Fractional old cargo still unloads whole when it fits; otherwise it stays aboard.
for _,mode in ipairs({'import','balanced','export'}) do
    for _,room in ipairs({100,400}) do
        local train,spoke,hub=fixture(60,0,120,480)
        spoke:AddResource(-room,'Metals')
        assert(D.Set(spoke,'Metals',mode,50))
        train.stockpiled_amount.Metals=400;train.assigned_resources[spoke]={Metals=400}
        assert(spoke.demand.Metals:AssignUnit(400))
        deliver(train,spoke)
        local fits=mode~='export' and room==400
        assert(not D.error)
        assert(stock(spoke)==60000-room+(fits and 400 or 0))
        assert(train.stockpiled_amount.Metals==(fits and 0 or 400))
        assert(spoke.demand.Metals.actual-spoke.demand.Metals.target==(fits and 0 or 400))
        assert(spoke:GetMaxStorage('Metals')==120000 and spoke:IsResourceEnabled('Metals'))
        if not fits then deliver(train,hub);assert(stock(hub)==400) end
    end
end
print('PASS fractional old-cargo unload: exact-fit import/balanced, over-target/export refused, native capacities restored')
-- First arrival of a newly placed train: vanilla initializes assigned_resources
-- inside UnloadAll, after our configured-row inspection. Match the sitting's Concrete row.
do
    local train,spoke,hub=fixture(0,0,120,480)
    for _,st in ipairs({spoke,hub}) do
        table.insert(st.storable_resources,'Concrete');st.storable_resources.Concrete=true
        local cap=st:GetMaxStorage('Concrete')
        local initial=st==spoke and cap or 0
        st.supply.Concrete=request(initial,10000)
        st.demand.Concrete=request(cap-initial,cap-10000)
    end
    train.assigned_resources=nil
    assert(D.Set(spoke,'Concrete','export',20))
    checked_transfer(train)
    assert(type(train.assigned_resources)=='table')
    assert(stock(spoke,'Concrete')==24000 and train.stockpiled_amount.Concrete==96000)
    assert(spoke.supply.Concrete.target==24000 and spoke.demand.Concrete.target==96000)
    deliver(train,hub)
    train.current_station=spoke;checked_transfer(train)
    assert(stock(spoke,'Concrete')==24000 and train.stockpiled_amount.Concrete==0)
    print('PASS new train with nil assigned_resources: configured Concrete, capacity 120, floor 24, return stops')
end
local r=request(80000,50000)
local returns=table.pack(F.WithTransientClaims({{r,20000}},function(a)
    assert(a==7 and r.target==60000 and r.actual==80000)
    return true,nil,7,nil
end,7))
assert(returns.n==4 and returns[1] and returns[3]==7 and r.target==80000)
r.reject=true
F.WithTransientClaims({{r,20000}},function() assert(r.target==80000) end)
r.reject=false
F.WithTransientClaims({{r,20000}},function() local absent; return absent.field end)
assert(r.target==80000 and F.stats.last_error);F.stats.last_error=nil
F.WithTransientClaims({{r,20000}},function() assert(r:AssignUnit(30000)) end)
assert(r.target==50000)
print('PASS claim cleanup on rejection/error, nil returns, independent reservations')
-- Pass-1 control: the archived body, one supply claim, no enabled/capacity lies.
for _,c in ipairs({{100,60},{400,36}}) do
    local t,s,h=fixture(80,0,100,c[1])
    F.WithTransientClaims({{s.supply.Metals,20000}},vanilla_transfer,t,nil,true)
    assert(stock(s)==c[2]*1000)
    print('CONTROL floor=20 sink='..c[1]..' retained='..stock(s)/1000)
end
-- Native import ceiling: equal capacity shares only 40 of the available 80.
local t,s,h=fixture(0,80,100,100)
t.current_station=h
vanilla_transfer(t,nil,true)
assert(t.stockpiled_amount.Metals==40000)
print('CONTROL import: available=80 requested=80 allocated=40')
-- Live hub shape and equal twins; slider endpoints and fractional unit floor.
for _,caps in ipairs({{60,240},{60,480},{100,100},{120,480}}) do
  for _,percent in ipairs({0,1,20,50,99,100}) do
    t,s,h=fixture(caps[1],0,caps[1],caps[2])
    assert(D.Set(s,'Metals','export',percent))
    local n=math.floor(caps[1]*1000*percent/100+0.5)
    checked_transfer(t)
    -- Vanilla's positive-desire lane loads whole resource units. A fractional
    -- slider can leave less than one unit above its floor, never below it.
    local retained=caps[1]*1000-((caps[1]*1000-n)//1000)*1000
    assert(stock(s)==retained,stock(s)..' != '..retained)
    deliver(t,h);t.current_station=s;checked_transfer(t)
    assert(stock(s)==retained and (t.stockpiled_amount.Metals or 0)==0)
    assert(s:IsResourceEnabled('Metals') and s:GetMaxStorage('Metals')==caps[1]*1000)
    assert(s.supply.Metals.target==stock(s))
    assert(s.supply.Metals.desired==caps[1]*1000 and s.demand.Metals.desired==0)
    assert(rawget(s,D.FIELD)==nil and rawget(h,D.FIELD)[s].Metals.percent==percent)
  end
end
print('PASS export: whole-unit allocation at floors 0/1/20/50/99/100 percent; 60/240, 60/480, 100/100, 120/480; return stops, fractional residue <1000')
for _,mode in ipairs({'import','balanced'}) do
    t,s,h=fixture(0,80,100,100)
    assert(D.Set(s,'Metals',mode,80))
    t.current_station=h;checked_transfer(t)
    assert(t.stockpiled_amount.Metals==80000)
    assert(s.demand.Metals.target==20000)
    deliver(t,s);checked_transfer(t)
    assert(stock(s)==80000 and t.stockpiled_amount.Metals==0)
    assert(s.supply.Metals.target==stock(s))
    assert(s.supply.Metals.desired==(mode=='import' and 0 or 80000))
end
print('PASS import ceiling lifted: 80 allocated and retained; balanced fills to 80')
-- Several receivers, plus other resources: real requests bound each order.
t,s,h=fixture(0,240,60,240)
local other=station(5,60);other.handle=3;other.city=s.city
table.insert(t.track.members,other);h.nodes[other]=true;D.Refresh()
assert(D.Set(s,'Metals','import',50));assert(D.Set(other,'Metals','balanced',25))
t.current_station=h;checked_transfer(t)
assert(t.assigned_resources[s].Metals==30000 and t.assigned_resources[other].Metals==10000)
assert(t.stockpiled_amount.Metals==40000)
assert(s.supply.Food.desired==10000 and s:IsResourceEnabled('Food'))
print('PASS several receivers get separate bounded orders; untouched resource keeps vanilla drone baseline')
t,s,h=fixture(80,0,100,400)
assert(D.Set(s,'Metals','balanced',20));checked_transfer(t)
assert(stock(s)==20000)
print('PASS balanced export excess leaves 20')
-- The hub's existing maintenance reserve still limits what an import can take.
t,s,h=fixture(0,80,100,100);h.reserve=4000
F.Reconcile(h);assert(F.Held(h,'Metals')==4000)
assert(D.Set(s,'Metals','import',100));t.current_station=h;checked_transfer(t)
assert(stock(h)==4000 and t.stockpiled_amount.Metals==76000)
assert(F.Held(h,'Metals')==4000)
print('PASS existing standing hub reserve is retained')
t,s,h=fixture(60,240,60,240)
assert(D.Set(s,'Metals','export',20));checked_transfer(t)
assert(stock(s)==60000 and (t.stockpiled_amount.Metals or 0)==0)
t.current_station=h;checked_transfer(t)
assert(stock(h)==240000 and stock(s)==60000)
assert(D.Status(s,'Metals').full)
print('PASS full hub refuses, does not bounce stock to exporter')
-- A real outstanding incoming reservation must not be allocated twice.
t,s,h=fixture(0,240,60,240)
assert(D.Set(s,'Metals','import',50))
assert(s.demand.Metals:AssignUnit(10000))
t.current_station=h;checked_transfer(t)
assert(t.stockpiled_amount.Metals==20000 and s.demand.Metals.target==30000)
deliver(t,s);assert(stock(s)==20000 and s.demand.Metals.target==30000)
-- Old inbound cargo after changing to export remains assigned, then unloads at hub.
t,s,h=fixture(10,0,60,240)
t.stockpiled_amount.Metals=10000;t.assigned_resources[s]={Metals=10000}
assert(s.demand.Metals:AssignUnit(10000))
assert(D.Set(s,'Metals','export',20));checked_transfer(t)
assert(stock(s)==10000 and t.stockpiled_amount.Metals==10000)
deliver(t,h)
assert(stock(h)==10000 and stock(s)==10000 and s.demand.Metals.target==50000)
print('PASS existing inbound reservations; export does not unload old cargo')
-- Drone coverage excludes a remote hub even though it services maintenance.
t,s,h=fixture(60,0,60,240)
function h:CanCommandDrones() return true end
function h:IsInWorkRange() return false end
s.command_centers={h}
assert(D.Set(s,'Metals','export',20))
assert(not D.HasDroneCoverage(s));checked_transfer(t);assert(stock(s)==12000)
s.command_centers={{CanCommandDrones=function() return true end,IsInWorkRange=function() return true end}}
assert(D.HasDroneCoverage(s))
print('PASS uncovered spoke gets train behavior; remote hub is not local drone coverage')
-- Rewrite paths use archived vanilla writers, including the request alias.
assert(D.Set(s,'Food','balanced',35))
local function baselines(cap)
    assert(s.supply.Metals.desired==cap and s.demand.Metals.desired==0)
    assert(s.supply.Food.desired==cap*35/100 and s.demand.Food.desired==cap*65/100)
end
baselines(60000)
s:SetDesiredAmount(3000);baselines(60000)
s:SetAcceptResourceState('Metals','disabled');assert(not s:IsResourceEnabled('Metals'))
s:SetAcceptResourceState('Metals','store');baselines(60000)
s:UpdateRequestCapacity('Food');baselines(60000)
s:OnModifiableValueChanged('max_storage_per_resource');baselines(60000)
local old=s.supply.Food
s.supply.Food=nil;s.demand.Food=nil
s:RecalculateAfterResourceListChange();baselines(60000);assert(s.supply.Food~=old)
assert(MultiResourceDepotBase.RegisterResourceRequest==MultiResourceCubeVisuals.RegisterResourceRequest)
SavegameFixups.RevertStationDesiredAmount();baselines(60000)
for _,st in ipairs(UIColony.labels.Station) do
    st.max_storage_per_resource=st.max_storage_per_resource*2
    st:OnModifiableValueChanged('max_storage_per_resource')
end
baselines(120000)
assert(D.Status(s,'Metals').slider==24000 and h:GetMaxStorage('Metals')==480000)
print('PASS six rewrite paths, captured request alias, network-wide capacity doubling')
-- Simulated load keeps only the hub table plus vanilla-written baseline/ledger.
OnMsg.SaveGameStart()
assert(s:IsResourceEnabled('Metals') and s.supply.Metals.target==stock(s))
OnMsg.SaveGameDone()
s.supply.Metals.desired=0;s.supply.Food.desired=0
OnMsg.LoadGame();baselines(120000)
-- Fire SaveGameStart synchronously from inside vanilla's evaluation.
t,s,h=fixture(60,0,60,240);assert(D.Set(s,'Metals','export',20))
local old_actual=s.supply.Metals.GetActualAmount
local fired=false
s.supply.Metals.GetActualAmount=function(req)
    if not fired and not s:IsResourceEnabled('Metals') then
        fired=true;OnMsg.SaveGameStart()
        assert(s:IsResourceEnabled('Metals') and s:GetMaxStorage('Metals')==60000)
        assert(req.target==req.actual and h.supply.Metals.target==h.supply.Metals.actual)
    end
    return old_actual(req)
end
checked_transfer(t);assert(fired);OnMsg.SaveGameDone()
assert(s.supply.Metals.target==stock(s))
print('PASS save hook removes in-call lies/claims; load rebuilds baselines from hub table')
-- Invalid edits and reset leave the vanilla dial/resource toggles intact.
assert(not D.Set(s,'Metals','export',101))
assert(not D.Set(s,'Metals','export',0/0))
assert(not D.Set(h,'Metals','export',20))
D.Reset(s);assert(not D.Get(s,'Metals'))
assert(s.supply.Metals.desired==s.desired_amount)
assert(not F.stats.last_error and not D.error)
print('PASS invalid controls and reset; no outstanding test errors')
''')
    print("PASS desk only: native requests, drone scheduling, UI and engine serialization remain attended", flush=True)


if __name__ == '__main__':
    main()
