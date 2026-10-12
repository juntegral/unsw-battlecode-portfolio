from pathlib import Path
import subprocess
root=Path(__file__).resolve().parents[2]
task=root/'exp/freecost'
for variant in ['on','off']:
 bot=task/('bot-'+variant)
 sources=sorted(p for p in bot.glob('*.cpp') if p.name!='main.cpp')
 binary=task/('fixtures-'+variant)
 subprocess.run(['/usr/bin/clang++','-std=c++20','-O2','-I',str(bot),str(task/'fixtures.cpp'),*[str(p) for p in sources],'-o',str(binary)],check=True)
 result=subprocess.check_output([str(binary)],text=True)
 (task/('fixtures-'+variant+'.txt')).write_text(result)
 print(result,end='')
