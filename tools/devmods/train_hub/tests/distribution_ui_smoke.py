"""Station section wiring against native grouping and UI doubles, not a render test."""
import hashlib
import subprocess
import sys
from distribution_smoke import ROOT, MOD, runtime, source_parts


def main():
    print('command:', subprocess.list2cmdline([sys.executable, *sys.argv]), flush=True)
    print('HEAD:', subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), flush=True)
    lua = runtime()
    source_parts(lua, "Resources.lua", [
        ("function GroupResourcesForSelector(", "function FormatResourceGroupStorageAmount("),
    ])
    lua.execute(r'''
Untranslated=function(s) return s end
RGB=function(...) return 1 end
RGBA=function(r,g,b,a) return r*1000000+g*1000+b end
box=function(...) return {...} end
point=function(...) return {...} end
ResolvePropObj=function(ctx) return ctx.object or ctx end
table.remove_entry=function(t,v) for i,x in ipairs(t) do if x==v then table.remove(t,i);return end end end
ResourcesInfopanelGroups={'BasicResources','AdvancedResources','MealIngredients','OtherResources'}
Resources={};ResourceInGroupIds={}
ResourceCmp=function(a,b) return a<b end
GetPresetLockStateAndText=function(res) return res.hidden and 'hidden' or 'unlocked' end
local widget={}
function widget:new(args,parent,context)
    local o=args or {};o.context=context;o.parent=parent;o.visible=o.Visible~=false;o.window_state='new'
    o.class=o.class or self.class
    setmetatable(o,{__index=self})
    if parent then
        parent[#parent+1]=o
        if o.Id then
            local node=parent
            while node do
                node[o.Id]=o
                if node.IdNode then break end
                node=node.parent
            end
        end
    end
    if self==InfopanelSlider then
        o.idBar=XWindow:new({},o)
        XWindow:new({MinWidth=320},o.idBar)
    elseif self==InfopanelSection then
        -- Native section's title is in its own window inside idContent.
        XWindow:new({Id='idContent'},o,context)
        local title=XWindow:new({},o.idContent,context)
        XText:new({Id='idSectionTitle'},title,context)
    end
    return o
end
function widget:SetMinWidth(n) self.MinWidth=n end
function widget:SetCheck(v) self.Check=v end
function widget:SetScroll(v) self.Scroll=v end
function widget:GetScroll() return self.Scroll end
function widget:SetEnabled(v) self.enabled=v end
function widget:SetText(v) self.Text=v end
function widget:SetVisible(v) self.visible=v end
function widget:SetBackground(v) self.Background=v end
function widget:UpdateProgress() self.progress_updates=(self.progress_updates or 0)+1 end
function widget:Open()
    self.window_state='open'
    for _,child in ipairs(self) do child:Open() end
    if self.OnContextUpdate then self:OnContextUpdate(self.context) end
end
function widget:DeleteChildren()
    for _,child in ipairs(self) do child.window_state='destroying' end
    for i=#self,1,-1 do table.remove(self,i) end
end
function widget:ResolveId(id)
    if self[id] then return self[id] end
    return self.parent and self.parent:ResolveId(id)
end
local function class(name) return setmetatable({class=name},{__index=widget}) end
XWindow=class('XWindow');XText=class('XText');XCheckButton=class('XCheckButton')
XTextButton=class('XTextButton');XScrollArea=class('XScrollArea');XSleekScroll=class('XSleekScroll')
XSection={OnShortcut=function() end}
function XScrollArea:ScrollTo(x,y) self.scroll_x=x;self.scroll_y=y end
native_row_update=function(self) self.native_updates=(self.native_updates or 0)+1 end
function build_xdef_classes()
    InfopanelSlider=class('InfopanelSlider');InfopanelSection=class('InfopanelSection')
    function InfopanelSlider:ScrollTo(v) self:SetScroll(v);self:UpdateProgress() end
    function InfopanelSlider:OnShortcut() end
    sectionStorageRow={OnContextUpdate=native_row_update}
end
local native_print=print
local ui_messages={}
print=function(message,...)
    ui_messages[#ui_messages+1]=tostring(message)
    return native_print(message,...)
end
function message_count(message)
    local n=0
    for _,text in ipairs(ui_messages) do if text==message then n=n+1 end end
    return n
end
function dialog(st)
    local dlg=XWindow:new({class='ipBuilding',IdNode=true},nil,{object=st})
    local host=XWindow:new({Id='idContent'},dlg)
    local before=XWindow:new({Id='before'},host)
    local storage=XWindow:new({class='sectionMultiResourceStorage'},host)
    local row=XWindow:new({Id='nativeRow',stored_max='native stored/max'},storage)
    local after=XWindow:new({Id='after'},host)
    return dlg,host,storage,row,before,after
end
function add_resource(st,res,group,hidden)
    Resources[res]={display_name=res,hidden=hidden}
    ResourceInGroupIds[res]=group and {[group]=true} or {}
    if not st.storable_resources[res] then
        table.insert(st.storable_resources,res);st.storable_resources[res]=true
        st.supply[res]=request(0,10000);st.demand[res]=request(st:GetMaxStorage(res),10000)
    end
end
''')
    path = MOD/'Code/45_TrainDistributionUI.lua'
    lua.execute('assert(InfopanelSection==nil and InfopanelSlider==nil and sectionStorageRow==nil)')
    lua.execute(path.read_text(encoding='utf8'))
    print(path.name, 'sha256:', hashlib.sha256(path.read_bytes()).hexdigest(), flush=True)
    lua.execute(r'''
local D=SMROptInTrainDistribution
assert(type(D.AttachStationSection)=='function' and type(OnMsg.DialogOpen)=='function',
    'UI module must register before XDef classes exist')
assert(not D.ui_error)
assert(message_count('[TrainDistribution] station import/export section loaded')==1)
build_xdef_classes() -- The engine builds XDefs after mod code, before the station card opens.
local t,s,h=fixture(60,0,60,240)
add_resource(s,'Metals','BasicResources')
add_resource(s,'Food','BasicResources')
add_resource(s,'Electronics','AdvancedResources')
add_resource(s,'Cherries','MealIngredients')
add_resource(s,'WasteRock','OtherResources')
add_resource(s,'Ungrouped',nil)
add_resource(s,'Locked','AdvancedResources',true)
g_LastExpandedResourceGroup='vanilla unchanged'
local dlg,host,storage,native,before,after=dialog(s)
OnMsg.DialogOpen(dlg)
local p=D.AttachStationSection(dlg)
assert(p and #host==4 and host[1]==before and host[2]==storage and host[3]==p and host[4]==after)
assert(storage[1]==native and #storage==1 and native.stored_max=='native stored/max')
assert(sectionStorageRow.OnContextUpdate==native_row_update)
assert(not D.Get(s,'Metals') and rawget(s,D.FIELD)==nil)
assert(p.coverage.visible and p.idContent[2]==p.coverage)
assert(p.coverage.Text:find('No drones in range',1,true))
assert(p.help.Text=='?' and p.help.parent==p.idSectionTitle.parent)
assert(p.help.HandleMouse and p.help.RolloverOnFocus==false and not p.help.OnPress)
local help_count=0
local function check_help(win)
    if win.RolloverTemplate and win.RolloverTemplate~='' then
        help_count=help_count+1;assert(win==p.help)
    end
    for _,child in ipairs(win) do check_help(child) end
end
check_help(p);assert(help_count==1 and p.RolloverOnFocus==false)
assert(not p.rows.Locked)
assert(p.rows.Electronics.parent==p.pages.AdvancedResources) -- singleton stays Advanced
assert(p.rows.Cherries.parent==p.pages.MealIngredients)
assert(p.rows.WasteRock.parent==p.pages.OtherResources and p.rows.Ungrouped.parent==p.pages.OtherResources)
for _,id in ipairs({'BasicResources','AdvancedResources','MealIngredients','OtherResources'}) do
    p.tabs[id]:OnPress()
    assert(p.tab==id)
    assert(p.rows_host.scroll_x==0 and p.rows_host.scroll_y==0)
    for key,page in pairs(p.pages) do assert(page.visible==(key==id)) end
end
assert(g_LastExpandedResourceGroup=='vanilla unchanged')
p:OnShortcut('RightShoulder');assert(not D.Get(s,'Metals'))
p.tabs.BasicResources:OnPress()
print('PASS one contained station section, untouched native rows, independent four tabs, singleton/hidden groups, top coverage and header-only hover help')
local row=p.rows.Metals
assert(not row.import.Check and not row.export.Check)
row.import:OnChange(true)
assert(row.import.Check and not row.export.Check and D.Get(s,'Metals').mode=='import')
row.export:OnChange(true)
assert(not row.import.Check and row.export.Check and D.Get(s,'Metals').mode=='export')
row.slider:ScrollTo(20)
assert(row.value.Text=='Keep 12 (20%)' and row.stock.Text=='60/60')
s.max_storage_per_resource=120000;h.max_storage_per_resource=480000
s:OnModifiableValueChanged('max_storage_per_resource');h:OnModifiableValueChanged('max_storage_per_resource')
p:OnContextUpdate(p.context)
assert(p.rows.Metals==row and row.value.Text=='Keep 24 (20%)' and row.stock.Text=='60/120')
assert(row.slider.progress_updates>0 and D.Get(s,'Metals').percent==20)
s:AddResource(-36000,'Metals');p:OnContextUpdate(p.context)
assert(row.stock.Text=='24/120')
row.slider:OnShortcut('RightShoulder')
assert(D.Get(s,'Metals').percent==21 and row.value.Text=='Keep 25.2 (21%)')
row.export:OnChange(false)
assert(not row.import.Check and not row.export.Check and D.Get(s,'Metals').mode=='balanced')
assert(row.value.Text=='Hold 25.2 (21%)')
row.import:OnChange(true)
assert(row.value.Text=='Fill to 25.2 (21%)')
h:AddResource(480000,'Metals')
row.export:OnChange(true)
assert(row.note.visible and row.note.Text=='Hub full')
s:SetAcceptResourceState('Metals','disabled');p:OnContextUpdate(p.context)
assert(not row.slider.enabled and not row.import.enabled and not row.export.enabled)
assert(row.note.Text=='Resource disabled in storage')
s:SetAcceptResourceState('Metals','store');p:OnContextUpdate(p.context)
assert(row.slider.enabled and D.Get(s,'Metals').mode=='export')
s.command_centers={{CanCommandDrones=function() return true end,IsInWorkRange=function() return true end}}
p:OnContextUpdate(p.context);assert(not p.coverage.visible)
s.command_centers={{CanCommandDrones=function() return true end,IsInWorkRange=function() return false end}}
p:OnContextUpdate(p.context);assert(p.coverage.visible)
print('PASS toggle exclusion/balanced, visible live slider amount/percent and stored/max, capacity 120 floor 24, stock refresh, disabled/full/coverage states')
Resources.Locked.hidden=false;p:OnContextUpdate(p.context)
assert(p.rows.Locked and p.rows.Locked.slider.window_state=='open')
assert(D.Get(s,'Metals').percent==21 and p.tab=='BasicResources')
local hubdlg=dialog(h);OnMsg.DialogOpen(hubdlg)
assert(not hubdlg:ResolveId('idTrainDistribution'))
local otherdlg=dialog({class='OtherBuilding'});OnMsg.DialogOpen(otherdlg)
assert(not otherdlg:ResolveId('idTrainDistribution'))
h.nodes={[h]=true};D.Refresh();p:OnContextUpdate(p.context);assert(not p.visible)
h.nodes[s]=true;D.Refresh();p:OnContextUpdate(p.context);assert(p.visible)
local bad=XWindow:new({class='ipBuilding',idContent=host},nil,{object=s})
assert(not D.AttachStationSection(bad) and D.ui_error:find('contained idContent',1,true))
assert(not D.AttachStationSection(bad))
assert(message_count('[TrainDistribution] station ipBuilding has no contained idContent')==1)
assert(D.AttachStationSection(dlg)==p and not D.ui_error)
local available=InfopanelSection
local late=dialog(s)
InfopanelSection=nil
OnMsg.DialogOpen(late);OnMsg.DialogOpen(late)
assert(not late:ResolveId('idTrainDistribution') and D.ui_error=='InfopanelSection unavailable')
InfopanelSection={new=false};OnMsg.DialogOpen(late)
assert(message_count('[TrainDistribution] InfopanelSection unavailable')==1)
InfopanelSection=available
OnMsg.DialogOpen(late)
assert(late:ResolveId('idTrainDistribution') and not D.ui_error)
assert(not D.error and not SMROptInTrainFloor.stats.last_error)
print('PASS live resource unlock, disconnected/reconnected section, hub/non-station exclusion, foreign-host rejection; no saved UI state')
print('PASS mod loads before XDefs; runtime missing-class/host failures print once each; attachment recovers when the class is available')
''')
    print('NOT TESTED: native rendering, mouse hit boxes, hover dismissal, scrolling and gamepad focus', flush=True)


if __name__ == '__main__':
    main()
