# Alma_portfolio_URL_cleanup

Scripts to perform various cleanup tasks with Alma portfolio URLs
- **change_parser_params_to_static_url.py**: Turns an identifier from the Parser Parameters field into a Static URL for EBSCO items; for example, ```ID=1000445``` becomes ```https://search.ebscohost.com/login.aspx?direct=true&scope=site&db=nlebk&db=nlabk&AN=1000445```. To modify for other use cases, replace the identifier prefix and base URL in lines 58 and 59.
- **move_static_override_to_static_url.py**: Moves URLs from the Static URL (Override) field to the Static URL field
- **remove_OpenAthens_prefix.py**: Removes JMU's OpenAthens prefix (```https://go.openathens.net/redirector/jmu.edu?url=```) from the Static URL field
- **replace_text_in_url.py**: Replaces specified text within the Static URL field with new text. Use for URL updates where part of the base URL is changing but identifiers are staying the same.


## Requirements
Created and tested with Python 3.6; see ```environment.yml``` for complete requirements.

Requires an Alma Bibs API key with read/write permissions. A config file (local_settings.ini) with this key should be located in the same directory as the script and input file. Example of local_settings.ini:

```
[Alma Bibs R/W]
key:apikey
```


## Usage
```python scriptname.py input.xlsx```
where ```input.xlsx``` is a spreadsheet listing Portfolio IDs in the second column and MMS IDs in the third column.


## Contact
Rebecca B. French - <https://github.com/frenchrb>
