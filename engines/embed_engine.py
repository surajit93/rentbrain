from pathlib import Path
from .common import ROOT

class EmbedEngine:
    def run(self):
        widget="""<div id='rent-widget'></div><script>window.rentWidget={version:'1.0',mode:'affordability'};</script>"""
        (ROOT/"embeds"/"rent-affordability-widget.html").write_text(widget)
        return ["rent-affordability-widget.html"]
