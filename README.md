# jss-assettag-importer
JSS Asset Tag Importer - Get those asset tags into your Casper JSS. For Mobile Devices and Computers!
## JSS Asset Tag importer - v.2
## Authored by Brad Schmidt @bradschm on 12/29/2015

### DISCLAIMER
I am not providing any kind of warranty. This has been thoroughly tested in my environments but I cannot guarantee that this script is not without bugs.
Thank you

### TODOS
- Add more logging (Actual logging instead of print)
- Add gui? Prompt for values and file location
- Once bug in the API for large advanced searches is fixes, switch to advanced searches from smart groups.

### HOW TO USE
1. Make an API user and give it these rights:
  * Create/Read Computer Smart Groups
  * Create/Read Mobile Device Smart Groups
  * Update Computer records
  * Update Mobile Device records

2. Save a csv file of your serial numbers and asset tags. Format is assettag,serialnumber. In other words, the first column is the asset tag and the second is the serialnumber.
3. Run the python script - be patient, this could take a while. Creating the groups can take a long time in large environments. Touching each record isn't blazing fast either but I did put in a progress counter ;)
4. Profit?
