"""Native compiled row/slider/tooltip constructors and callbacks; engine window doubles.

Checks structure and data flow, not engine pixels, font metrics or hit testing.
"""
import hashlib
import subprocess
import sys
from distribution_smoke import ROOT, MOD, ARCHIVE, runtime, source_parts


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
local rect={minx=function(s) return s[1] end,miny=function(s) return s[2] end,
    sizex=function(s) return s[3]-s[1] end,sizey=function(s) return s[4]-s[2] end}
box=function(...) return setmetatable({...},{__index=rect,__add=function(a,b) return a end}) end
point=function(x,y) return {xy=function() return x,y end,x=function() return x end,y=function() return y end} end
ResolvePropObj=function(ctx) return ctx.object or ctx end
g_UINoTransparencyReasons={}
mass=false;IsMassUIModifierPressed=function() return mass end
Sleep=function(ms) coroutine.yield(ms) end
local widget={IdNode=false,Dock=false,MaxWidth=1000000,Shorten=false,Visible=true,
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
function widget:CreateThread(name,fn,...)
    self.threads=self.threads or {};local co=coroutine.create(fn);self.threads[name]=co
    local ok,delay=coroutine.resume(co,...);assert(ok,delay);self.delay=delay
end
function widget:Expire(name) local ok,why=coroutine.resume(self.threads[name]);assert(ok,why) end
function widget:UpdateRolloverContent() self.idContent:OnContextUpdate(self.idContent.context) end
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
    path = MOD/'Code/45_TrainDistributionUI.lua'
    lua.execute('assert(InfopanelSection==nil and sectionStorageRow==nil and InfopanelSlider==nil)')
    lua.execute(path.read_text(encoding='utf8'))
    print(path.name, 'sha256:', hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    lua.execute('assert(type(OnMsg.DialogOpen)=="function" and not SMROptInTrainDistribution.ui_error)')
    # These are the archived constructors, not a handwritten approximation of their children.
    for name in ['InfopanelSectionTitle', 'InfopanelActiveSection', 'sectionStorageRow',
                 'InfopanelSlider', 'RolloverTitleSection', 'MarsRollover']:
        path = ARCHIVE/f'XDef/{name}.generated.lua'
        lua.execute(path.read_text(encoding='utf8'))
        print('native XDef:', name, 'sha256:', hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    source_parts(lua, '../CommonLua/X/XRollover.lua', [
        ('function XRolloverWindow:Init(', 'function XRolloverWindow:ControlMove('),
    ])
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
assert(row.RolloverOnFocus==false and row.RolloverTemplate=='InfopanelSectionRollover')
assert(s:ResourceRolloverText('Metals'):find('No drones in range',1,true))
local x,y=scale:AdjustConstrainedScale(450,450);assert(x==800 and y==800)
x,y=scale:AdjustConstrainedScale(950,950);assert(x==950 and y==950)
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
local b=slider.distribution_bubble
assert(b and b.class=='MarsRollover' and b.FadeOutTime==200 and b.delay==450)
assert(b.idContent.idText.Text=='24 (20%)' and b.idContent.idText.Translate)
assert(b.idContent.idText.TextStyle=='RolloverDescriptionStyle' and b.idContent.idText.MinWidth==0)
assert(b.idBackgroundFrame.Image=='UI/CommonRemaster/rollover_background_s.png')
slider:ScrollTo(21);assert(slider.distribution_bubble==b and b.idContent.idText.Text=='25.2 (21%)')
b:Expire('distribution_fade');assert(b.closed and not slider.distribution_bubble)
slider:OnMouseButtonDown(20,'L');assert(slider.distribution_bubble)
row:OnActivate(row.context);row:OnContextUpdate(row.context)
assert(D.Get(s,'Metals').mode=='export' and s.supply.Metals.desired==120000 and s.demand.Metals.desired==0)
checked_transfer(t);assert(stock(s)==24000);deliver(t,h);t.current_station=s;checked_transfer(t);assert(stock(s)==24000)
s.max_storage_per_resource=240000;s:OnModifiableValueChanged('max_storage_per_resource')
row:OnContextUpdate(row.context);assert(D.Get(s,'Metals').percent==20)
slider:OnMouseButtonDown(20,'L');assert(slider.distribution_bubble.idContent.idText.Text=='48 (20%)')
s.command_centers={{CanCommandDrones=function() return true end,IsInWorkRange=function() return true end}}
assert(not s:ResourceRolloverText('Metals'):find('No drones in range',1,true))
print('PASS four distinct native icons/titles; native disabled flags; Balanced slider; native tooltip content/update/idle fade; UI-configured capacity-120 floor 24 and return; live capacity/coverage refresh')

local outside=station(0,60);outside.city=s.city;outside.task_requests={outside.demand.Metals}
table.insert(s.city.labels.Station,outside)
local peer=station(0,60);peer.city=s.city;peer.handle=3;h.nodes[peer]=true
table.insert(s.city.labels.Station,peer);D.Refresh()
assert(D.Set(peer,'Metals','balanced',50))
mass=true;row:OnActivate(row.context);mass=false -- Export -> Import applied city-wide.
assert(D.Get(s,'Metals').mode=='import' and D.Get(peer,'Metals').mode=='import')
assert(D.Get(peer,'Metals').percent==50 and not D.Get(outside,'Metals') and outside:IsResourceEnabled('Metals'))
mass=true;row:OnActivate(row.context);mass=false
assert(not outside:IsResourceEnabled('Metals') and not peer:IsResourceEnabled('Metals') and not h:IsResourceEnabled('Metals'))
outside:ToggleAcceptResource('Metals',false);assert(outside:IsResourceEnabled('Metals') and not D.Get(outside,'Metals'))
local vanilla,vr,vs=dialog(outside);OnMsg.DialogOpen(vanilla)
assert(not vr.distribution_slider and vr:GetTitle()==native_title and vr:GetTitleRight()==native_right)
x,y=vs:AdjustConstrainedScale(450,450);assert(x==450 and y==450)
assert(outside:GetResAcceptIcon('Metals')=='UI/IconsRemaster/Sections/resource_storing.tga')
assert(outside:ResourceRolloverText('Metals'):find('Trains will balance',1,true))
local hubdlg,hr=dialog(h);OnMsg.DialogOpen(hubdlg);assert(not hr.distribution_slider)
local other=XControl:new({},nil,{class='OtherBuilding'});other.class='ipBuilding';OnMsg.DialogOpen(other)
assert(not D.ui_error)
h.nodes[s]=nil;D.Refresh();row:OnContextUpdate(row.context)
assert(not row.distribution_slider and row:GetTitle()==native_title and #row.idSectionTitles==2)
x,y=scale:AdjustConstrainedScale(450,450);assert(x==450 and y==450)
h.nodes[s]=true;D.Refresh();row:OnContextUpdate(row.context);assert(row.distribution_slider)
assert(rawget(s,D.FIELD)==nil and not D.error)
print('PASS Ctrl applies chosen state to city stations, preserves per-station percentages; non-network station/hub native rows and scale; disconnect restores row, reconnect extends it')
''')
    print('NOT TESTED: engine pixel layout/font metrics, native tooltip positioning/fade animation, mouse hit boxes and controller focus', flush=True)


if __name__ == '__main__':
    main()
