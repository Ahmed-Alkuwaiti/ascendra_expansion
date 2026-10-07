"""Shared paths so the generators run from any checkout."""
import os

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RES = os.path.join(PROJECT, 'src/main/resources')
JAVA = os.path.join(PROJECT, 'src/main/java/com/aurelia')
VANILLA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '_cache/vanilla')
