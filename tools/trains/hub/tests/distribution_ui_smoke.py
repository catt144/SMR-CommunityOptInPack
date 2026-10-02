"""Native compiled row/slider constructors and word-wrap helper and callbacks; engine window doubles.

Checks structure and data flow, not engine pixels, font metrics or hit testing.
"""
import hashlib
import subprocess
import sys
from distribution_smoke import ROOT, MOD, ARCHIVE, runtime, source_parts
from lupa import LuaRuntime


def ui_runtime():
    lua = runtime()
    lua.execute(r'''
Untranslated=function(s) return s end
T=function(id,text)
    if type(id)=='table' then
        local s=id[1];local ctx=id[2]
        if type(s)=='string' and ctx and ctx.res then s=s:gsub('<resource%(res%)>',ctx.res) end
        return s or ''
    end
    return text or id
end
RGB=function(...) return 1 end; RGBA=RGB
local rect={maxx=function(s) return s[3] end,maxy=function(s) return s[4] end,minx=function(s) return s[1] end,miny=function(s) return s[2] end,
    sizex=function(s) return s[3]-s[1] end,sizey=function(s) return s[4]-s[2] end}
box=function(...) return setmetatable({...},{__index=rect,__add=function(a,b) return a end}) end
point=function(x,y) return {xy=function() return x,y end,x=function() return x end,y=function() return y end} end
ResolvePropObj=function(ctx) return ctx.object or ctx end
g_UINoTransparencyReasons={}
mass=false;IsMassUIModifierPressed=function() return mass end
Sleep=function(ms) coroutine.yield(ms) end
local widget={IdNode=false,Dock=false,MinWidth=0,MaxWidth=1000000,MaxHeight=1000000,Padding=box(2,2,2,2),Shorten=false,Visible=true,
    RolloverText='',RolloverTitle='',RolloverHint='',RolloverHintGamepad='',
    RolloverDisabledText='',RolloverDisabledTitle='',RolloverDisabledHint='',RolloverDisabledHintGamepad='',
    RolloverWarning='',RolloverOffset=box(0,0,0,0),Margins=box(0,0,0,0),
    RolloverOnFocus=false,ContextUpdateOnOpen=true,Text='',TextStyle='',BindTo=''}
for _,key in ipairs({'MinWidth','MaxWidth','MinHeight','MaxHeight','Dock','Shorten','HAlign','TextHAlign',
    'TextStyle','Visible','Image','Margins','Anchor','AnchorType','Transparency','MaxProgress','Progress',
    'RolloverText','RolloverTitle','RolloverOnFocus','RolloverHint','RolloverHintGamepad','ContextUpdateOnOpen'}) do
    widget['Set'..key]=function(self,v) self[key]=v end
    widget['Get'..key]=function(self) return self[key] end
end
for _,key in ipairs({'RolloverOffset','RolloverDisabledHint','RolloverDisabledHintGamepad','RolloverWarning'}) do
    widget['Get'..key]=function(self) return self[key] end
end
function widget:SetText(v) self.Text=v or '';self.text=self.Text end
function widget:GetText() return self.Text end
function widget:GetPadding() return self.Padding end
function widget:GetFontId() self.font_height=22*self.scale:y()/1000;return self.scale:y()/1000 end
XFontControl={GetFontId=widget.GetFontId}
char_width=9
UIL={MeasureText=function(text,font,first,last)
    return utf8.len(text:sub(first or 1,last or #text))*char_width*font
end}
utf8.Advance=function(text,idx,n) return utf8.offset(text,n+1,idx) or #text+1 end
utf8.FindNextLineBreakCandidate=function(text,idx)
    if idx>#text then return end
    if text:sub(idx,idx)==' ' then idx=idx+1 end
    return text:find(' ',idx,true) or #text+1
end
function widget:SetEnabled(v) self.enabled=v end
function widget:GetEnabled() return self.enabled end
function widget:SetScroll(v) local old=self.Scroll;self.Scroll=v;return old~=v end
function widget:GetScroll() return self.Scroll end
function widget:GetThumbRange() return self.Scroll or 0,(self.Scroll or 0)+8 end
function widget:ResolveRolloverAnchor() return self.content_box end
function widget:GetRolloverAnchor() return 'top' end
function widget:InvalidateMeasure() self.invalidated=true end
function widget:GetEffectiveMargins() return table.unpack(self.Margins) end
function widget:SetBox(x,y,w,h) self.box=box(x,y,x+w,y+h) end
function widget:ResolveId(id)
    if rawget(self,id) then return rawget(self,id) end
    local node=self.parent
    while node and not node.IdNode do node=node.parent end
    return node and node[id]
end
function widget:InitProperty(key,default)
    local v=self[key];if v==nil then v=default end
    if self['Set'..key] then self['Set'..key](self,v) end
end
function widget:new(args,parent,context)
    local o=args or {};o.parent=parent;o.context=context;o.class=self.class;o.window_state='new';o.enabled=true
    o.content_box=box(0,0,100,26);o.scale=point(1000,1000)
    setmetatable(o,{__index=self})
    if parent then
        table.insert(parent,o)
        if o.Id then
            local node=parent
            while node and not node.IdNode do node=node.parent end
            if node then node[o.Id]=o end
        end
    end
    local function init(c)
        for _,name in ipairs(rawget(c,'__parents') or {}) do init(_G[name]) end
        local fn=rawget(c,'Init');if fn then fn(o,parent,context) end
    end
    init(self)
    return o
end
function widget:Open()
    self.window_state='open'
    for _,child in ipairs(self) do child:Open() end
    if self.OnContextUpdate and self.ContextUpdateOnOpen then self:OnContextUpdate(self.context) end
end
function widget:delete()
    self.window_state='destroying';self.threads={}
    for i=#self,1,-1 do self[i]:delete() end
    if self.parent then for i,w in ipairs(self.parent) do if w==self then table.remove(self.parent,i);break end end end
end
function widget:Close() self.closed=true;self:delete() end
function widget:OnShortcut() end
function widget:DeleteThread(name) if self.threads then self.threads[name]=nil end end
function widget:CreateThread() error('UI must not start a timer') end
local function define(name,c)
    c.class=name
    for _,p in ipairs(c.properties or {}) do c[p.id]=p.default end
    setmetatable(c,{__index=function(_,k)
        for _,p in ipairs(rawget(c,'__parents') or {}) do local v=_G[p][k];if v~=nil then return v end end
        return widget[k]
    end})
    _G[name]=c
end
DefineClass=setmetatable({},{__newindex=function(_,k,c) define(k,c) end})
UndefineClass=function() end
for _,name in ipairs({'XWindow','XImage','XFrame','XSeparatedBlurRect'}) do define(name,{}) end
for _,name in ipairs({'XControl','XContextControl','XSection','XScrollThumb','XRolloverWindow','XFrameProgress'}) do
    define(name,{IdNode=true})
end
define('XText',{IdNode=false})
XScroll={ScrollTo=function(self,v)
    if self:SetScroll(Clamp(math.floor(v+0.5),self.Min,self.Max)) then
        if self.OnScroll then self:OnScroll(self.Scroll) end
        return true
    end
end}
XScrollControl={OnMouseButtonDown=function(self,pt,button)
    if button=='L' and self.enabled then self:ScrollTo(pt);return 'break' end
end}
local native_print=print
messages={}
print=function(s,...) messages[#messages+1]=s;native_print(s,...) end
function message_count(s) local n=0;for _,v in ipairs(messages) do if v==s then n=n+1 end end;return n end
function Station:DoesAcceptResource(res) return self.storable_resources[res] end
function Station:GetStoredAmount(res) return self.supply[res].actual end
''')
    path = MOD/'Code/StationRows_45_TrainDistributionUI.lua'
    lua.execute('assert(InfopanelSection==nil and sectionStorageRow==nil and InfopanelSlider==nil)')
    lua.execute(path.read_text(encoding='utf8'))
    print(path.name, 'sha256:', hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    lua.execute('assert(type(OnMsg.DialogOpen)=="function" and not SMROptInTrainDistribution.ui_error)')
    # These are the archived constructors, not a handwritten approximation of their children.
    for name in ['InfopanelSectionTitle', 'InfopanelActiveSection', 'sectionStorageRow',
                 'InfopanelSlider']:
        path = ARCHIVE/f'XDef/{name}.generated.lua'
        lua.execute(path.read_text(encoding='utf8'))
        print('native XDef:', name, 'sha256:', hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    parser_path = ARCHIVE/'../CommonLua/X/XTextParser.lua'
    parser = parser_path.read_text(encoding='utf8')
    start = parser.index('local MeasureText = UIL.MeasureText')
    end = parser.index('function BlockLayouter:FinalizeLine()', start)
    lua.execute('local FindNextLineBreakCandidate=utf8.FindNextLineBreakCandidate\n' +
                parser[start:end] + '\nnative_fit=FindTextThatFitsIn')
    print('native word wrapper sha256:', hashlib.sha256(parser_path.read_bytes()).hexdigest(), flush=True)
    source_parts(lua, '../CommonLua/X/XWindow.lua', [
        ('function XWindow:SetLayoutSpace(', 'function XWindow:SetScaleModifier('),
    ])
    # Exact per-instance callback emitted by the Infopanel template.
    source = (ARCHIVE/'XDef/Infopanel.generated.lua').read_text(encoding='utf8')
    start = source.index('AdjustConstrainedScale = function')
    end = source.index('\n\t\tend,', start) + len('\n\t\tend')
    lua.execute('native_scale = ' + source[start:end].split(' = ', 1)[1])
    lua.execute(r'''
function GetFirstChildOfKind() return nil end -- zero-overlap branch of native scale callback
function dialog(st)
    local dlg=XControl:new({class='ipBuilding'},nil,st);dlg.class='ipBuilding'
    local scale=XWindow:new({AdjustConstrainedScale=native_scale},dlg,st);scale.class='XSizeConstrainedWindow'
    local host=XWindow:new({Id='idContent'},scale,st)
    local row=sectionStorageRow:new({},host,{st,res='Metals'})
    dlg:Open()
    return dlg,row,scale,host
end
''')
    return lua


def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), flush=True)
    lua = ui_runtime()
    lua.execute(r'''
local D=SMROptInTrainDistribution
local t,s,h=fixture(120,0,120,480)
local dlg,row,scale,host=dialog(s)
local native_title=row:GetTitle();local native_right=row:GetTitleRight()
local native_row_constructor=sectionStorageRow.new
local native_activate=sectionStorageRow.OnActivate
local old_class=sectionStorageRow
sectionStorageRow=nil
OnMsg.DialogOpen(dlg);OnMsg.DialogOpen(dlg)
assert(D.ui_error=='sectionStorageRow.OnContextUpdate unavailable')
assert(message_count('[TrainDistribution] sectionStorageRow.OnContextUpdate unavailable')==1)
sectionStorageRow=old_class
OnMsg.DialogOpen(dlg);OnMsg.DialogOpen(dlg)
assert(not D.ui_error and #host==1 and not dlg.idTrainDistribution)
assert(sectionStorageRow.new==native_row_constructor and sectionStorageRow.OnActivate==native_activate)
assert(row.idSectionTitle.Text=='Metals · Balanced' and row.idSectionTitle.Translate)
assert(row:GetTitleRight()==native_right and row.idSectionTitleRight.HAlign=='right')
local slider=row.distribution_slider
assert(slider and slider.parent==row.idSectionTitle.parent and #slider.parent==3)
assert(slider.Dock=='box' and slider.Margins[2]==0 and slider.Margins[4]==0)
assert(slider.MinHeight==0 and slider.MaxHeight==0 and slider.VAlign=='stretch')
-- Native layout must use the existing line's height despite a zero measured height.
slider.measure_height=0;slider.HAlign='stretch';slider.box=box(0,0,0,0)
for _,height in ipairs({18,22,26,32}) do
    XWindow.SetLayoutSpace(slider,0,0,100,height)
    assert(slider.box:sizey()==height and slider.box:sizex()==88)
end
assert(slider.idBar.MinWidth==0 and slider.idBar[1].MinWidth==0)
assert(slider.idBar.ProgressImage=='UI/CommonRemaster/in_bar.png')
assert(row.idContent[1]==slider.parent and #row.idContent==1)
assert(row.idSectionTitleRight.TextStyle=='InfopanelResourceAccept')
assert(not D.Get(s,'Metals') and rawget(s,D.FIELD)==nil)
assert(s:ResourceRolloverText('Metals'):find('8% of current capacity (10',1,true))
assert(select(4,D.RowState(s,'Metals'))==10000 and rawget(h,D.FIELD)==nil)
assert(row.RolloverOnFocus==false and row.RolloverTemplate=='InfopanelSectionRollover')
assert(s:ResourceRolloverText('Metals'):find('No drones in range',1,true))
local x,y=scale:AdjustConstrainedScale(450,450);assert(x==800 and y==800)
x,y=scale:AdjustConstrainedScale(950,950);assert(x==950 and y==950)
-- Native fallback control: a narrow line splits Balanced into Balance / d.
local w=UIL.MeasureText('Balanced',1)
assert(native_fit('Balanced',1,1,w-1,0,w-1)=='Balance')
for _,cw in ipairs({9,18}) do
    char_width=cw
    for _,scale in ipairs({800,1000,1200}) do
        row.idSectionTitle.scale=point(scale,scale)
        for _,name in ipairs({'Electronics','Machine Parts','Rare Metals'}) do
            s.supply[name]=request(0,0);s.demand[name]=request(120000,0)
            row.context.res=name;row:OnContextUpdate(row.context)
            local title=row.idSectionTitle
            local available=(title.MinWidth-4)*scale/1000
            for word in title.text:gmatch('%S+') do
                assert(native_fit(word,1,scale/1000,available,0,available)==word, title.text..' word='..word..' available='..available..' fit='..native_fit(word,1,scale/1000,available,0,available))
            end
            assert(title.MaxHeight==50 and title.MinWidth==title.MaxWidth) -- 44 + FIT_SLACK 2 + padding 4
        end
    end
end
char_width=9;row.idSectionTitle.scale=point(1000,1000)
row.context.res='Metals';row:OnContextUpdate(row.context)
print('PASS native narrow-line Balance/d reproduction; whole Electronics/Machine Parts/Rare Metals/mode words fit reserved width across font/scale doubles; title capped at two font lines')
print('PASS late XDef load/retry/log-once; original native constructor/click/right-title retained; slider in original title line; 80% panel floor')

local seen={}
for _,mode in ipairs({'export','import','disabled','balanced'}) do
    row:OnActivate(row.context);row:OnContextUpdate(row.context)
    assert(D.RowState(s,'Metals')==mode)
    assert(row.idSectionTitle.Text=='Metals · '..({export='Export',import='Import',disabled='Not accepted',balanced='Balanced'})[mode])
    local icon=row.idIcon.Image;assert(not seen[icon]);seen[icon]=true
    assert(s:IsResourceEnabled('Metals')==(mode~='disabled'))
    assert(slider.enabled==(mode~='disabled'))
    if mode=='disabled' then
        assert(icon=='UI/IconsRemaster/Sections/resource_no_accept.png')
        assert(s.demand.Metals:IsAnyFlagSet(const.rfSuspended))
        assert(s.supply.Metals:IsAnyFlagSet(const.rfPostInQueue))
        assert(row.idSectionTitle.TextStyle=='InfopanelResourceNoAccept')
        local before=D.Get(s,'Metals').percent
        assert(slider:OnShortcut('RightShoulder')=='break' and D.Get(s,'Metals').percent==before)
    end
end
slider:ScrollTo(20) -- Balanced must configure its pinned amount too.
assert(D.Get(s,'Metals').mode=='balanced' and D.Get(s,'Metals').percent==20)
assert(s.supply.Metals.desired==24000 and s.demand.Metals.desired==96000)
assert(s:ResourceRolloverText('Metals'):find('20% of current capacity (24',1,true))
local children=#slider
slider:ScrollTo(21)
assert(s:ResourceRolloverText('Metals'):find('21% of current capacity (25.2',1,true))
XScrollControl.OnMouseButtonDown(slider,20,'L')
assert(#slider==children and not slider.distribution_bubble and not slider.threads)
row:OnActivate(row.context);row:OnContextUpdate(row.context)
assert(D.Get(s,'Metals').mode=='export' and s.supply.Metals.desired==120000 and s.demand.Metals.desired==0)
checked_transfer(t);assert(stock(s)==24000);deliver(t,h);t.current_station=s;checked_transfer(t);assert(stock(s)==24000)
s.max_storage_per_resource=240000;s:OnModifiableValueChanged('max_storage_per_resource')
row:OnContextUpdate(row.context);assert(D.Get(s,'Metals').percent==20)
assert(s:ResourceRolloverText('Metals'):find('20% of current capacity (48',1,true))
s.command_centers={{CanCommandDrones=function() return true end,IsInWorkRange=function() return true end}}
assert(not s:ResourceRolloverText('Metals'):find('No drones in range',1,true))
print('PASS four distinct native icons/titles; native disabled flags; Balanced slider; row-tooltip amount/percent readout without bubble/timer; UI-configured capacity-120 floor 24 and return; live capacity/coverage refresh')

local outside=station(0,60);outside.city=s.city;outside.task_requests={outside.demand.Metals}
table.insert(s.city.labels.Station,outside)
local peer=station(0,60);peer.city=s.city;peer.handle=3;h.nodes[peer]=true
table.insert(s.city.labels.Station,peer);D.Refresh()
assert(D.Set(peer,'Metals','balanced',50))
local source_entry=D.Get(s,'Metals')
mass=true;row:OnActivate(row.context);mass=false -- Copy Export, without advancing it.
assert(D.Get(s,'Metals')==source_entry and D.Get(s,'Metals').mode=='export' and D.Get(peer,'Metals').mode=='export')
assert(D.Get(s,'Metals').percent==20 and D.Get(peer,'Metals').percent==20)
assert(peer.supply.Metals:GetDesiredAmount()==60000 and peer.demand.Metals:GetDesiredAmount()==0)
assert(D.Get(outside,'Metals').mode=='export' and D.Get(outside,'Metals').percent==20)
assert(outside:IsResourceEnabled('Metals') and rawget(outside,D.LOCAL_FIELD))
assert(D.Set(peer,'Metals','balanced',50))
row:OnActivate(row.context) -- Import.
assert(D.Get(s,'Metals').percent==20 and D.Get(peer,'Metals').percent==50) -- Plain click stays local.
mass=true;row:OnActivate(row.context);mass=false
assert(D.Get(s,'Metals').mode=='import' and D.Get(peer,'Metals').mode=='import')
assert(D.Get(peer,'Metals').percent==20)
assert(D.Set(peer,'Metals','balanced',50))
peer:SetAcceptResourceState('Metals','disabled') -- An already-disabled destination also gets the percent.
row:OnActivate(row.context) -- Not accepted.
source_entry=D.Get(s,'Metals')
mass=true;row:OnActivate(row.context);mass=false
assert(not outside:IsResourceEnabled('Metals') and not peer:IsResourceEnabled('Metals') and not h:IsResourceEnabled('Metals'))
assert(not s:IsResourceEnabled('Metals'))
assert(D.Get(s,'Metals')==source_entry and D.Get(peer,'Metals').percent==20)
assert(peer.demand.Metals:IsAnyFlagSet(const.rfSuspended))
row:OnActivate(row.context) -- Balanced.
mass=true;row:OnActivate(row.context);mass=false
assert(D.Get(s,'Metals').mode=='balanced' and D.Get(peer,'Metals').mode=='balanced')
assert(D.Get(peer,'Metals').percent==20 and peer.supply.Metals:GetDesiredAmount()==12000)
assert(peer.demand.Metals:GetDesiredAmount()==48000) -- Same percent, destination's own capacity.
outside:ToggleAcceptResource('Metals',false);assert(D.Get(outside,'Metals').mode=='export')
outside:ToggleAcceptResource('Metals',false);assert(D.Get(outside,'Metals').mode=='import')
local vanilla,vr,vs=dialog(outside);OnMsg.DialogOpen(vanilla)
assert(vr.distribution_slider and vr:GetTitle()=='Metals · Import' and vr:GetTitleRight()==native_right)
x,y=vs:AdjustConstrainedScale(450,450);assert(x==800 and y==800)
assert(outside:GetResAcceptIcon('Metals')=='UI/IconsRemaster/Sections/elevator_resource_down.png')
assert(outside:ResourceRolloverText('Metals'):find('No hub:',1,true))
assert(outside:ResourceRolloverText('Metals'):find('from other stations',1,true))
vr.distribution_slider:ScrollTo(40)
assert(D.Get(outside,'Metals').percent==40 and outside.supply.Metals.desired==0)
outside:ToggleAcceptResource('Metals',false);vr:OnContextUpdate(vr.context)
assert(not outside:IsResourceEnabled('Metals') and not vr.distribution_slider.enabled)
outside:ToggleAcceptResource('Metals',false);vr:OnContextUpdate(vr.context)
assert(D.Get(outside,'Metals').mode=='balanced' and D.Get(outside,'Metals').percent==40)
local hubdlg,hr=dialog(h);OnMsg.DialogOpen(hubdlg);assert(not hr.distribution_slider)
local other=XControl:new({},nil,{class='OtherBuilding'});other.class='ipBuilding';OnMsg.DialogOpen(other)
assert(not D.ui_error)
h.nodes[s]=nil;D.Refresh();row:OnContextUpdate(row.context)
assert(row.distribution_slider and row:GetTitle()=='Metals · Balanced' and #row.idSectionTitles==3)
x,y=scale:AdjustConstrainedScale(450,450);assert(x==800 and y==800)
h.nodes[s]=true;D.Refresh();row:OnContextUpdate(row.context);assert(row.distribution_slider)
local chained=station(0,60);chained.handle=6243;chained.city=s.city
s.city.labels.Station={s,h,outside,peer,chained};h.nodes[chained]=true
local chainline={members={peer,chained}}
s.city.train_track_routes[chainline]=chainline.members
D.Refresh();assert(D.Parent(chained)==peer)
assert(chained:ResourceRolloverText('Metals'):find('through station 3',1,true))
assert(rawget(s,D.FIELD)==nil and not D.error)
print('PASS Ctrl copies state/percent to hub and hubless stations without advancing source; hubless four-state cycle, slider and tooltip; hub excluded; disconnect/reconnect retain row layout')
''')
    long_title_fit()
    print('NOT TESTED: engine pixel layout/font metrics, mouse hit boxes and controller focus', flush=True)


def fit_slice(path):
    text = path.read_text(encoding='utf-8')
    start = text.index('local FIT_SLACK = 2')
    fit = text.index('local function fit_title(title)', start)
    end = text.index('\nend\n', fit) + len('\nend\n')
    code = text[start:end]
    body = '\n'.join(line.split('--', 1)[0] for line in code.splitlines())
    assert ' / ' not in body and '//' not in body, f'{path.name} fit_title has a bare division (EF-116)'
    return code + '\nreturn fit_title\n'


def long_title_fit():
    # The hub's fit_title and the Elevator Depot's (read-only) on the same mock titles, with integer-only
    # Max/MulDivRound as the engine's are (EF-116); both boxes scaled to pixels the way XWindow does
    # (ScaleXY per value, truncating; CommonLua/X/XWindow.lua:766-784, archived build 25579348). The hub
    # must give the depot's answers and hold two lines and the widest word at every scale 800..2200.
    depot = ROOT / 'Code/ElevatorDepot_10_ElevatorDepot.lua'
    lua = LuaRuntime(unpack_returned_tuples=True)
    lua.execute(r'''
local function int(v) assert(math.type(v)=='integer', 'integer expected: '..tostring(v)) return v end
fit_env = {math=math, ipairs=ipairs,
    Max=function(a, b) int(a); int(b) return a > b and a or b end,
    MulDivRound=function(a, b, c) int(a); int(b); int(c) return (a * b + c // 2) // c end,
    UIL={}}
function load_fit(code, name) return assert(load(code, name, 't', fit_env))() end
''')
    hub_fit = lua.eval('load_fit')(fit_slice(MOD / 'Code/StationRows_45_TrainDistributionUI.lua'), '45_TrainDistributionUI')
    depot_fit = lua.eval('load_fit')(fit_slice(depot), '10_ElevatorDepotDev')
    lua.globals().hub_fit, lua.globals().depot_fit = hub_fit, depot_fit
    lua.execute(r'''
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
fit_env.UIL.MeasureText = function(word) return (#word * 17 * cur_sx) // 1000 + 3 end
local function px(units, sc) return (units * sc) // 1000 end
local function fits(t, sx, sy)
  if px(t.maxh, sy) - 2 * px(PAD, sy) < 2 * t.font_height then return false end
  for word in t.text:gmatch('%S+') do
    if px(t.maxw, sx) - 2 * px(PAD, sx) < fit_env.UIL.MeasureText(word) + 1 then return false end
  end
  return true
end
fit_cases = 0
for _, text in ipairs{'Exotic Minerals · Not accepted', 'Rare Metals · Balanced', 'Metals · Import', 'Machine Parts · Export'} do
  for sc = 800, 2200, 50 do
    cur_sx = sc
    local a, b = title(text, sc, sc), title(text, sc, sc)
    hub_fit(a); depot_fit(b)
    assert(a.minw == b.minw and a.maxw == b.maxw and a.maxh == b.maxh,
      ('hub and depot differ at scale %d: %s (hub %d/%d, depot %d/%d)'):format(sc, text, a.maxw, a.maxh, b.maxw, b.maxh))
    assert(math.type(a.maxw)=='integer' and math.type(a.maxh)=='integer')
    assert(fits(a, sc, sc), ('the hub box loses a line or a word at scale %d: %s (maxh %d)'):format(sc, text, a.maxh))
    fit_cases = fit_cases + 1
  end
end
''')
    assert lua.eval('fit_cases') == 116
    print('PASS long titles: the hub fit_title gives the Elevator Depot answers and holds two lines and the widest word at every scale 800..2200 (', lua.eval('fit_cases'), 'cases, integer-only helpers, no bare /)', flush=True)


if __name__ == '__main__':
    main()
