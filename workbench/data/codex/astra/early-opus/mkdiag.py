import re,os
src=os.path.expanduser('~/meow-redteam/solo/src/w-early/main.cpp');dst=os.path.expanduser('~/meow-redteam/solo/src/w-early/diag.cpp')
s=open(src).read()
a=s.index('    int split_child_size() {');b=s.index('    bool tail_threatened() const {')
body=s[a:b];n=[0]
def sub(m):
    n[0]+=1;return 'return (split_why = %d, 0);'%n[0]
body=re.sub(r'return 0;',sub,body)
s=s[:a]+'    int split_why = 0;\n'+body+s[b:]
call='        int const child = split_child_size();\n        if (child > 0) {\n            split_off(child);\n            return;\n        }\n'
assert s.count(call)==1
s=s.replace(call,'        split_why = 0;\n        int const child = split_child_size();\n        if (child == 0 && length >= SPLIT_MIN_LENGTH && round <= 100) {\n            ct.output_log("NOSPLIT", round, ct.get_id(), length, split_why, harvesting_now ? 1 : 0, tail_index >= 0 ? tail_room() : -1.0);\n        }\n        if (child > 0) {\n            split_off(child);\n            return;\n        }\n')
open(dst,'w').write(s);print('returns',n[0])
