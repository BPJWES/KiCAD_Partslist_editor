Changelog for the KiCad Partslist Editor
========================================


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
* fixed major bug, which limited the number of fields to 9 or less (parsing error)
* changed separator for CSV from ',' to ';'
