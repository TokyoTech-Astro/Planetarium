"""Hardware-free regression check for playback motor stopping."""
import ast
from pathlib import Path
from types import SimpleNamespace
import time

tree = ast.parse(Path('app.py').read_text(encoding='utf-8'))
methods = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == 'App')
selected = [n for n in methods.body if isinstance(n, ast.FunctionDef) and n.name in ('effective', 'pause')]
ns = dict(time=time, pygame=SimpleNamespace(mixer=SimpleNamespace(music=SimpleNamespace(stop=lambda:None))), GREEN='green', UNCONNECTED_FIELDS=set(), FIELDS=['angle','speed','first','stars']+[f'p{i}' for i in range(1,9)], as_bool=lambda s:s=='ON')
exec(compile(ast.fix_missing_locations(ast.Module(body=[ast.ClassDef(name='TestApp',bases=[],keywords=[],body=selected,decorator_list=[])],type_ignores=[])),'test','exec'), ns)
a = ns['TestApp']()
a.desired=dict(angle=-999.,speed=3.,first=True,stars=True,**{f'p{i}':False for i in range(1,9)})
a.override={k:SimpleNamespace(get=lambda:False) for k in ns['FIELDS']}
a.manual={};a.actual=dict(a.desired,angle=123.);a.last_sent=dict(a.desired)
a.playing=True;a.motor_playback_stopped=False;a.position=lambda:10.
a.play_btn=SimpleNamespace(config=lambda **k:None);a.update_values=lambda:None
sent=[];a.write=lambda d:sent.append(d) or True
a.pause()
assert not a.playing and a.motor_playback_stopped
assert sent[-1]['motor']==dict(angle=123.,speed=0.)
assert sent[-1]['light']['first'] and sent[-1]['light']['stars']
assert a.effective()['speed']==0.
a.desired['angle']=999.;a.desired['speed']=8.
assert a.effective()['speed']==0., 'periodic/reconnect sends must remain stopped'
a.motor_playback_stopped=False
assert a.effective()['speed']==8., 'resume restores the requested speed'
print('PAUSE_CONTINUOUS_CW_CCW_AND_RESUME_OK')
