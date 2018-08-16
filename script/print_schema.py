# Add root project dir to the python path
import os
import sys

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from eralchemy import render_er
from atst.models import Base

output = sys.argv[1] if len(sys.argv) > 1 else 'schema.png'

## Draw from SQLAlchemy base
render_er(Base, output)
