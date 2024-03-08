# ChimeraX Remote File Browser

This is a simple browser for remote files. Remote sources are treated as a filesystem and files 
can be cached locally for fast access or streamed directly from the remote source if the format permits.

## Installation

1. Install [ChimeraX](https://www.cgl.ucsf.edu/chimerax/download.html)
2. Download the most recent build from the [releases page.]()
3. Run the following command in the ChimeraX command prompt to install the plugin:
```
toolshed install /path/to/ChimeraX_RemoteBrowser-0.1-py3-none-any.whl
```
4. Restart ChimeraX
5. Open the Remote Browser from the Tools menu or by running:
```
ui tool show RemoteBrowser
```

## Usage

Currently the following data sources are supported:
- AWS S3 (via s3fs) 
- SFTP (via sshfs)

Support for additional data sources can be added by implementing the `AbstractFileSystem` interface.