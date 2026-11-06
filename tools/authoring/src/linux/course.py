# Shared settings for every Linux lesson (read by tools/authoring/shlesson.py)
# Characters, speech bubbles, callouts, Beginner/Intermediate/Advanced tabs and body() macros are the
# same as the Hive course; they are loaded from ../hive/course.py so both courses stay identical.
import os as _os, runpy as _rp
_h = _rp.run_path(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'hive', 'course.py'))
for _k in ('ARJUN', 'RIYA', 'KABIR', 'EXAM_ICON', 'TIP_ICON', 'WARN_ICON', 'LEVEL_NAMES', 'say', 'exam', 'levels', 'body', 'mix'):
    globals()[_k] = _h[_k]

COURSE = dict(id='linux', title='Linux', track='DevOps and Tools', track_anchor='devops', color='#0F766E')
