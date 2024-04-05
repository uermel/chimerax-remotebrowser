# ChimeraX Remote File Browser

This is a simple browser for remote files. Remote sources are treated as a filesystem and files
can be cached locally for fast access or streamed directly from the remote source if the format permits.

## Installation

1. Install [ChimeraX](https://www.cgl.ucsf.edu/chimerax/download.html)
2. Optional: install [ChimeraX-OME-Zarr](https://github.com/uermel/chimerax-ome-zarr) for the best experience.
3. Download the most recent build from the [releases page.](https://github.com/uermel/chimerax-remotebrowser/releases)
4. Run the following command in the ChimeraX command prompt to install the plugin:
```
toolshed install /path/to/ChimeraX_RemoteBrowser-0.3-py3-none-any.whl
```
4. Restart ChimeraX
5. Open the Remote Browser from the Tools menu or by running:
```
ui tool show RemoteBrowser
```

## Usage

Currently the following data sources are supported:
- AWS S3 (via s3fs)

Planned support for:
- SFTP (via sshfs)

Support for additional data sources can be added by implementing the `AbstractFileSystem` interface.

## Demo

Short demo using the public cryoet-data-portal bucket:

https://github.com/uermel/chimerax-remotebrowser/assets/6641113/804ee590-ebbb-4928-98bc-414a5a57e894



