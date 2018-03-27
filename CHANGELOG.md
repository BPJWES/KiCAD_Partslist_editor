Changelog for the KiCad Partslist Editor
========================================


# current dev
* add class ComponentField with regex parser using regex101.com
* replaced getComponents() with .components
* implement and use class ComponentField
* fixed duplicate field entries for multi-unit parts
* update default fields Part, Value, Footprint and Datasheet on Import
* fixed bug with missing field properties on newly inserted fields

## TODO
* set visibility to 0001 (invisible)
* extract field names from the schematics and CSV --> obsolete FieldKeywords.conf

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

