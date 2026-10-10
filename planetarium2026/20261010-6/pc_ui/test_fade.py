"""Non-hardware checks for configurable fade transmission."""
import ast
from pathlib import Path
from types import SimpleNamespace

source = Path(__file__).with_name('app.py').read_text(encoding='utf-8')
tree = ast.parse(source)
method = next(n for c in tree.body if isinstance(c, ast.ClassDef)
              for n in c.body if isinstance(n, ast.FunctionDef) and n.name == 'send')
scope = {}
exec(compile(ast.Module(body=[method], type_ignores=[]), 'send', 'exec'), scope)
print('SEND_METHOD_PARSED_OK')
packets=[]
d={'angle':0.,'speed':0.,'first':True,'stars':False,
   **{f'p{i}':False for i in range(1,9)}}
app=SimpleNamespace(emergency_stop=False,effective=lambda:d,last_sent=None,
                    cfg={'fade_seconds':5.0},
                    write=lambda packet:packets.append(packet) or True,
                    update_values=lambda:None)
for seconds in (5.,2.5,0.):
    app.cfg['fade_seconds']=seconds
    scope['send'](app,True,True)
    assert packets[-1]['light']['fade_duration_ms']==round(seconds*1000)
    assert packets[-1]['light']['fade'] is True
print('UI_DURATION_TRANSMISSION_OK')
for t in (0, .25, .5, .75, 1):
    rise = t*t; rise *= rise
    fall = 1-t; fall *= fall; fall *= fall
    assert abs(rise - t**4) < 1e-12
    assert abs(fall - (1-t)**4) < 1e-12
assert .5**4 == .0625
protocol = Path(__file__).parents[1]/'firmware/common/protocol.h'
assert 'VERSION = 5' in protocol.read_text(encoding='utf-8')
assert 'fadeDurationMs' in protocol.read_text(encoding='utf-8')
assert '"fade_duration_ms":round(self.cfg["fade_seconds"]*1000)' in source
print('QUARTIC_CURVES_AND_DURATION_FIELD_OK')
