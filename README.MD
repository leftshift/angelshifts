# Angelshifts app for the SHA2017 badge

## Adding your API key
To get your engelsystem api key:
* go to https://volunteer.sha2017.org/?p=users&action=view
* click on 'JSON Export'
* copy the part in the url behind 'key='

To write it to the badge:
* Connect to the python console on the badge 
* run 'badge.nvs_set_str("engel", "key", API_KEY)' and replace API_KEY with your key

## Customizing for other events:
Just replace the `engelsystem_url` in `service.py` with the url of the engelsystem of the current event.
