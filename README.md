# Spotify Merge Playlists

Simple tool to merge multiple playlist to one

## Installation
```pip install -r pip_requirements.txt```

## Usage
Create an app in https://developer.spotify.com/dashboard/applications \
You can use any valid url for the redirect uri "http://example.com" for example \
Create `secrets.json` file \
```json
{
	"spotfiy-api-clientid": "",
	"spotfiy-api-secret": "",
	"spotfiy-api-redirect_uri": ""
}
```

Create `inputs.json` file
```json
{
	"playlists": [
		{
			"name": "",
			"merged_playlist": "",
			"child_playlists": [
				""
			]
		}
	]
}
```