# vim: set expandtab shiftwidth=4 softtabstop=4:

from chimerax.core.toolshed import BundleAPI

class _MyAPI(BundleAPI):

    api_version = 1

    @staticmethod
    def start_tool(session, bi, ti):

        if ti.name == "RemoteBrowser":
            from . import tool
            return tool.RemoteBrowserTool(session, ti.name)


# Create the ``bundle_api`` object that ChimeraX expects.
bundle_api = _MyAPI()