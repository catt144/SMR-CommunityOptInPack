"""Check row wiring with UI doubles. Pixel fit/readability require the attended smoke."""
import subprocess
import sys
from distribution_smoke import ROOT, MOD, runtime


def main():
    print('command:',subprocess.list2cmdline([sys.executable,*sys.argv]),flush=True)
    print('HEAD:',subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),flush=True)
    lua=runtime()
    lua.execute(r'''
Untranslated=function(s) return s end
RGB=function(...) return 1 end
box=function(...) return {...} end
point=function(...) return {...} end
local widget={}
function widget:new(args,parent,context)
    local o=args or {};o.context=context;o.visible=true
    setmetatable(o,{__index=self})
    if parent then parent[#parent+1]=o end
    if self==InfopanelSlider then o.idBar=setmetatable({}, {__index=widget}) end
    return o
end
function widget:SetMinWidth(n) self.MinWidth=n end
function widget:SetCheck(v) self.Check=v end
function widget:SetScroll(v) self.Scroll=v end
function widget:GetScroll() return self.Scroll end
function widget:SetEnabled(v) self.enabled=v end
function widget:SetText(v) self.Text=v end
function widget:SetVisible(v) self.visible=v end
function widget:Open() self.window_state='open' end
XWindow=widget;XText=widget;XCheckButton=widget
InfopanelSlider=setmetatable({}, {__index=widget})
function InfopanelSlider:ScrollTo(v) self:SetScroll(v) end
function InfopanelSlider:OnShortcut() end
sectionStorageRow={OnContextUpdate=function(self)
    self.native_updates=(self.native_updates or 0)+1
    self.stored_max='native stored/max'
end}
''')
    lua.execute((MOD/'Code/45_TrainDistributionUI.lua').read_text(encoding='utf8'))
    lua.execute(r'''
local D=SMROptInTrainDistribution
local t,s,h=fixture(60,0,60,240)
local row=setmetatable({context={s,res='Metals'},idContent={},window_state='open'}, {__index=sectionStorageRow})
row:OnContextUpdate(row.context)
local p=row.distribution_controls
assert(p and not p.import.Check and not p.export.Check)
assert(p.note.Text:find('No drones in range',1,true))
p.import.OnChange(p.import,true);row:OnContextUpdate(row.context)
assert(p.import.Check and not p.export.Check and D.Get(s,'Metals').mode=='import')
p.export.OnChange(p.export,true);row:OnContextUpdate(row.context)
assert(not p.import.Check and p.export.Check and D.Get(s,'Metals').mode=='export')
p.slider:ScrollTo(35);row:OnContextUpdate(row.context)
assert(D.Get(s,'Metals').percent==35)
p.export.OnChange(p.export,false);row:OnContextUpdate(row.context)
assert(not p.import.Check and not p.export.Check and D.Get(s,'Metals').mode=='balanced')
assert(row.stored_max=='native stored/max' and #row.idContent==1)
local hubrow=setmetatable({context={h,res='Metals'},idContent={}}, {__index=sectionStorageRow})
hubrow:OnContextUpdate(hubrow.context);assert(not hubrow.distribution_controls)
s:SetAcceptResourceState('Metals','disabled');row:OnContextUpdate(row.context)
assert(not p.slider.enabled and not p.import.enabled and not p.export.enabled)
print('PASS row wiring: mutual exclusion, unchecked balanced, slider, coverage note, native readout, disabled resource, no hub controls')
''')
    print('NOT TESTED: native widgets, hit testing, pixels and gamepad focus',flush=True)


if __name__=='__main__':
    main()
