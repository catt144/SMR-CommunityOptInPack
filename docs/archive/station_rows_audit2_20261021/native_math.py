"""Second independent audit: native route witnesses and exact rational allocation oracle.

Run from repository root. Reuse only the archived first audit's runtime/fixture
setup, without executing its old counterexample assertions. No shipping edits.
"""
from pathlib import Path
import hashlib
import random
from fractions import Fraction

prior=Path('docs/archive/station_rows_audit_20261021/adversarial.py').read_text(encoding='utf8')
prefix,chunk=prior.split("lua.execute(r'''",1)
exec(compile(prefix,'audit1_runtime_setup','exec'),globals())
setup=chunk.split('-- Junction topology:',1)[0]
print('FIXTURE SOURCE: audit1 adversarial.py normalized-UTF8 SHA256',hashlib.sha256(prior.encode()).hexdigest(),flush=True)
lua.execute(setup)
lua.execute(r'''
local exercised=0
for _,kind in ipairs({'all','people','construction','nonworking'}) do
    for _,tailstock in ipairs({0,60}) do
        local ns,ts,vs=network({60,0,tailstock},{60,60,60},{{1,2,3}})
        local tail=ts[1].members.edges[2].tracks[1]
        if kind=='people' then tail.transport_mode='people' end
        if kind=='construction' then tail.elements_under_construction={true} end
        if kind=='nonworking' then ns[3].working=false end
        assert(D.Set(ns[1],'Metals','export',0))
        if kind=='all' then
            for i=1,3 do move(vs[1],ns[1],ns[2]); move(vs[1],ns[1],ns[3]) end
            assert(stock(ns[1])==0 and stock(ns[2])+stock(ns[3])==(60+tailstock)*1000)
            assert(stock(ns[2])>0)
        else
            for i=1,3 do move(vs[1],ns[1],ns[2]) end
            assert(stock(ns[1])==0 and stock(ns[2])==60000 and stock(ns[3])==tailstock*1000)
        end
        print('PASS A1 Export0 native '..kind..' tailstock='..tailstock..' final='..stock(ns[1])..','..stock(ns[2])..','..stock(ns[3]))
        exercised=exercised+1
        ns,ts,vs=network({60,0,tailstock},{60,60,60},{{1,2,3}})
        tail=ts[1].members.edges[2].tracks[1]
        if kind=='people' then tail.transport_mode='people' end
        if kind=='construction' then tail.elements_under_construction={true} end
        if kind=='nonworking' then ns[3].working=false end
        assert(D.Set(ns[2],'Metals','import',100))
        move(vs[1],ns[1],ns[2])
        if kind~='all' then assert(stock(ns[1])==30000 and stock(ns[2])==30000 and stock(ns[3])==tailstock*1000) end
        print('PASS A1 Default-to-Import native '..kind..' tailstock='..tailstock..' receiver='..stock(ns[2]))
        exercised=exercised+1
    end
end
print('RECONCILED native A1 matrix='..exercised..' (4 modes x 2 tail stocks x 2 source/row cases)')

-- Opposite travel direction; construction/mode filtering is not a list-order double.
for _,kind in ipairs({'people','construction'}) do
    local ns,ts,vs=network({60,0,60},{60,60,60},{{1,2,3}})
    if kind=='people' then ts[1].transport_mode='people' else ts[1].elements_under_construction={true} end
    vs[1].track=ts[1].members.edges[2].tracks[1]
    assert(D.Set(ns[3],'Metals','export',0))
    for i=1,3 do move(vs[1],ns[3],ns[2]) end
    assert(stock(ns[1])==60000 and stock(ns[2])==60000 and stock(ns[3])==0)
    print('PASS native reverse direction '..kind..':60000,60000,0')
end
local ns,ts,vs=network({60,60,0},{60,60,60},{{1,2,3}})
ns[2].working=false
assert(D.Set(ns[3],'Metals','import',100)); move(vs[1],ns[1],ns[3])
assert(stock(ns[1])==30000 and stock(ns[2])==60000 and stock(ns[3])==30000)
print('PASS nonworking middle excluded while reachable farther station retains share30')

-- flags0 excludes self, but the current working station retains its stock and weight.
ns,ts,vs=network({60,0},{60,60},{{1,2}})
assert(D.Set(ns[2],'Metals','import',100))
local answers,claims=local_view(vs[1],ts[1])
assert(claims[1][1]==ns[1].supply.Metals and claims[1][2]==30000)
assert(answers[ns[2]].Metals.capacity==30000)
print('PASS current station balance: source floor30000 and receiver order30000 from pool60000')

-- An unreachable saved row still opts this resource into the R7 view.
ns,ts,vs=network({60,0,60},{60,60,60},{{1,2,3}})
ts[1].members.edges[2].tracks[1].transport_mode='people'
assert(D.Set(ns[3],'Metals','balanced',50))
assert(local_view(vs[1],ts[1])); move(vs[1],ns[1],ns[2])
assert(stock(ns[1])==30000 and stock(ns[2])==30000 and stock(ns[3])==60000)
print('PASS unreachable saved row still configures resource; reachable pair shares30; tail unchanged')

-- Integration of the rounded splitter, including caller handle sorting.
ns,ts,vs=network({0.002,0,0,0},{60,60,60,60},{{1,2,3,4}})
assert(D.Set(ns[4],'Metals','export',0))
answers,claims=local_view(vs[1],ts[1])
local orders={}
for _,c in ipairs(claims) do for i=2,3 do if c[1]==ns[i].demand.Metals then orders[i]=ns[i].demand.Metals.target-c[2] end end end
assert(claims[1][2]==1 and orders[2]==1 and orders[3]==0)
ns[1].handle=3; ns[3].handle=1
answers,claims=local_view(vs[1],ts[1])
for _,c in ipairs(claims) do for i=2,3 do if c[1]==ns[i].demand.Metals then orders[i]=ns[i].demand.Metals.target-c[2] end end end
assert(claims[1][2]==0 and orders[2]==1 and orders[3]==1)
print('PASS A2 integrated pool2: handle order1,2,3 ->1,1,0; swapping source/far handles ->0,1,1')
''')

# Re-run the unaffected first-audit native topology, reservations and relay controls.
first=chunk.split('-- Junction topology:',1)[1].split('-- Sub-resource rounding:',1)[0]
lua.execute('-- Junction topology:'+first)
relay=chunk.split('-- Continued relay under explicit service schedules, with capacity and conservation guards.',1)[1].split("''')",1)[0]
lua.execute(relay)

# Direct D.WaterFill calls; independent rational oracle using sorted room/weight
# thresholds, not the production held/rest loop. All expected sums exclude zero weight.
lua.execute(r'''
function fill_audit(pool,spec)
    local slots={}; for i,s in ipairs(spec) do slots[i]={w=s[1],c=s[2],alloc=1234567} end
    local ticks=0
    debug.sethook(function() ticks=ticks+1; assert(ticks<10000,'instruction limit') end,'',1000)
    D.WaterFill(pool,slots); debug.sethook()
    local out={}; for i,s in ipairs(slots) do out[i]=s.alloc end
    return out
end
''')
def oracle(pool,spec):
    active=sorted((i for i,(w,c) in enumerate(spec) if w>0 and c>0),key=lambda i: Fraction(spec[i][1],spec[i][0]))
    result=[Fraction(0) for _ in spec]
    left=pool; weight=sum(spec[i][0] for i in active)
    for pos,i in enumerate(active):
        w,c=spec[i]
        if Fraction(left*w,weight)>=c:
            result[i]=Fraction(c); left-=c; weight-=w
        else:
            for j in active[pos:]: result[j]=Fraction(left*spec[j][0],weight)
            break
    return result
cases=[]
# Original seed and capacity/percent domain from the first audit.
rng=random.Random(20261021)
for _ in range(1200):
    n=rng.randrange(3,9); caps=[rng.randrange(1,101) for _ in range(n)]
    percentages=[rng.choice([0,1,20,50,80,99,100]) for _ in range(n)]
    pool=rng.randrange(0,301)*1000
    cases.append((pool,[(c*1000,c*10*p) for c,p in zip(caps,percentages)]))
original=len(cases)
# Broader weight/room ranges including sparse slots, no slots and excess pool.
rng=random.Random(720261021)
for _ in range(4000):
    spec=[(rng.choice([0,1,rng.randrange(1,250001)]),rng.choice([0,1,rng.randrange(1,250001)])) for _ in range(rng.randrange(0,17))]
    rooms=sum(c for w,c in spec if w>0)
    pool=rng.choice([0,1,2,max(0,rooms-1),rooms,rooms+1,rng.randrange(0,2000001)])
    cases.append((pool,spec))
worst=Fraction(0); error=0
for pool,spec in cases:
    arg=lua.table_from([lua.table_from(pair) for pair in spec])
    first=lua.globals().fill_audit(pool,arg); second=lua.globals().fill_audit(pool,arg)
    got=[int(first[i+1]) for i in range(len(spec))]
    assert got==[int(second[i+1]) for i in range(len(spec))]
    want=oracle(pool,spec)
    for v,e,(w,c) in zip(got,want,spec):
        assert 0<=v<=c and (w>0 or v==0)
        worst=max(worst,abs(v-e)); assert abs(v-e)<=1,(pool,spec,got,want)
    delta=abs(sum(got)-min(pool,sum(c for w,c in spec if w>0)))
    error=max(error,delta); assert delta==0
print(f'PASS A2 rational oracle: original={original}, broader={len(cases)-original}, total={len(cases)}; max pool-sum error={error}; max exact deviation={worst} (<=1); deterministic repeat, room bounds, zero slots/weights/rooms and instruction guard hold',flush=True)
print('NOT RUN: engine scheduling, actual route rebuilding, saves, cabin/drones, pixels, player saves.',flush=True)
