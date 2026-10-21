"""Check owner-imported Arboretum assets; --activate switches only the model-related data.

Does not create ArtSpec, import art, change production, or run the game. Default is read-only.
Run after the owner saves both imports and closes the editor. The template remains on the
Large Garden until the import exists, so preparing this prototype does not break the editor.
"""
import argparse
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
STAGE = HERE.parents[1]
REPO = STAGE.parent
BODY, GLASS = 'SMROptInArboretumPavilion', 'SMROptInArboretumGlass'
OVERRIDES = dict(entity=BODY, consumption_resource_stockpile_spot_name='Resourcepile',
                 prg_class='GardenNatural_Large')


def check():
    sys.path.insert(0, str(REPO/'tools'))
    from workbench import array, metadata
    mod=metadata(STAGE)
    entities=array(mod['entities'])
    assert all(name in entities for name in [BODY,GLASS]), 'Both entities must be registered by the Mod Editor'
    required_spots={'Top','Workdrone','Resourcepile','Yard','Door','Visitwarmup','Glazing'}
    for name in [BODY,GLASS]:
        path=STAGE/'Entities'/f'{name}.entjson'
        data=json.loads(path.read_text(encoding='utf-8'))['$value']
        assert data['strName']==name
        mesh=data['meshDescriptions'][0]
        assert any(s['name']=='idle' for s in data['states'])
        for lod in mesh['lods']:
            for leaf in lod['meshes_data']:
                for key in ['mesh','material']:
                    prefix='Mod/SMR_CommunityOptInPack_Workbench/'
                    assert leaf[key].startswith(prefix),'Imported asset refers outside workbench'
                    assert (STAGE/leaf[key][len(prefix):]).is_file(),leaf[key]
        if name==BODY:
            spots=mesh.get('attaches',[])
            assert required_spots <= {s['name'] for s in spots}, 'Required spots absent after import'
            assert sum(s['name']=='Visitwarmup' for s in spots)==10
            # Both filename and annotation are checked again in the runtime menu probe.
            assert GLASS in path.read_text(encoding='utf-8'),'Glazing annotation did not survive import'
    return {'result':'import files present','overrides':OVERRIDES}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--activate',action='store_true')
    args=p.parse_args()
    result=check()
    if args.activate:
        tasks=subprocess.check_output(['tasklist','/FI','IMAGENAME eq Mars.exe','/FO','CSV'],text=True)
        assert 'Mars.exe' not in tasks,'Close the editor/game before activation'
        manifest=STAGE/'modules.json'
        value=json.loads(manifest.read_text(encoding='utf-8'))
        assert set(value['modules'])=={'Arboretum'},'Review shared entity ownership before proceeding'
        source=HERE/'template.json'
        data=json.loads(source.read_text(encoding='utf-8'))
        data['properties'].update(OVERRIDES)
        source.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8',newline='\n')
        subprocess.run([sys.executable,str(HERE/'generate.py')],check=True)
        # This workbench has one resident. Fail rather than adopting another module's files.
        infra={'README.md','metadata.lua','items.lua','modules.json','Code/00_Workbench.lua'}
        value['modules']['Arboretum']['files']=sorted(p.relative_to(STAGE).as_posix() for p in STAGE.rglob('*')
            if p.is_file() and '__pycache__' not in p.parts and p.suffix!='.pyc' and p.relative_to(STAGE).as_posix() not in infra)
        # The editor's entity table is code the workbench loads; with one resident it is that module's.
        entity_data='Code/_EntityData.generated.lua'
        if entity_data not in value['modules']['Arboretum']['code']:
            value['modules']['Arboretum']['code'].append(entity_data)
        manifest.write_text(json.dumps(value,indent=2)+'\n',encoding='utf-8',newline='\n')
        result['activated']=True
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
