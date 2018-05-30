Changelog for the KiCad Partslist Editor
========================================

## TODOs
* support correct double quote escaping.
  Kicad uses `\"` within a fields value, but pythons csv reader/writer
  uses `""` to represent a `"` within a field.

# V18.0.4:
* support for negative coordinates (fixed regex)
* fixed major bug in read_settings()
* fixed major bug in exportCsvFile(), with non existing multiple properties
  first property was set always to ""


# V18.0.3:
2018-05-03
* use pythons csv module for CSV IO
  --> supports quoted fields in CSV, KiCad field values can now contain the separator
* add index column, so a modified CSV file can be sorted again before saving it (great
  if used with Git for version control and Git diff).
* minor refactoring: use a dict instead of a list with 2 entries for
  `CsvComponent.propertyList` which is now called `propertyDict`

# V18.0.2:
2018-05-01
* support for schematic version 4 (KiCad 5)
* automatic override of the L record's reference, by the 'F 0' value
* fixed: components on the root sheet didn't get updated in all cases


# V18.0.1
2018-03-27
* add class ComponentField with regex parser using regex101.com
* replaced getComponents() with .components
* implement and use class ComponentField
* fixed duplicate field entries for multi-unit parts
* update default fields Part, Value, Footprint and Datasheet on Import
* fixed bug with missing field properties on newly inserted fields
* set visibility of new fields to 0001 (invisible)
* tested reexport, which produced identical ple.csv
* add error and warnings handling, show a summary to the user
* update readme and cleaned up project directory
* add version string to the window title
* modified copyright

# V18.0.0
2018-03-26
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

# Before Oct. 2017
* add value capability i.e. reading in the value field from a csv file
* add multi_file capability for reading in data
* add exception handling to file operations
* add relative paths
* add annotation checking - done
* add delete functionality -done
* make sure the links will be hidden
* fix schematic name
* remember paths for saving and opening files during a session
* auto add .csv extension for filename
* remember paths between sessions
