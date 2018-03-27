Changelog for the KiCad Partslist Editor
========================================

# Missing Features
## Extract Field Names from Schematics and CSV
* obsolete FieldKeywords.conf
* type of fields are managed by project data without metadata
* new fields can be defined by the CSV
* redundant field names can easily be merged within CSV-spreadsheet with 'auto-filter'

## Index Column
* index column 'Index' with a line counting number
* gives ability to sort the list and do a proper file comparison with diff after manipulations


# 2018-03-27
* add class ComponentField with regex parser using regex101.com
* replaced getComponents() with .components
* implement and use class ComponentField
* fixed duplicate field entries for multi-unit parts
* update default fields Part, Value, Footprint and Datasheet on Import
* fixed bug with missing field properties on newly inserted fields
* set visibility of new fields to 0001 (invisible)
* tested reexport, which produced identical ple.csv
* add error and warnings handling, show a summary to the user

# 2018-03-26
* allways export KiCad's default fields
  * Part
  * Reference
  * Unit
  * Value
  * Footprint
  * Datasheet
* Changed config-version for FieldKeywords.conf from 1.0 to 1.1
* remove duplicate listings of parts which are in multiple subsheet instances
* fixed major bugs, which limited the number of fields to 9 or less (parsing error)
* make CSV separator configurable with config.ini
* using os module for file name and path manipulations

