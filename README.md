# SlicerDICOMWeb

This is an experimental [3D Slicer](slicer.org) extension to interact with servers supporting the [DICOMWeb standard](http://dicomweb.hcintegrations.ca/#/home).

It is a *very* incomplete start, developed during the hackathon at the [2015 DICOMWeb meeting](http://www.dicomconference.org/dicomweb-2015/).

## Goals
* use the restful API to implement the same features supported by the DCMTK/ctkDICOM used in [Slicer 4.x](http://www.slicer.org/slicerWiki/index.php/Documentation/Nightly/Modules/DICOM)
** Query, retrieve, store...
* experiment with building core functionality in javascript for use in both slicer on the desktop and in webbrowsers

## Code organization
* StudyBrowser is a web page that
 * uses jquery and datatables to present a simple user interface
 * interacts with the DICOMWeb server to pull down a list of studies
 * allows the user to select a study
* DICOMWebInterface is a slicer scripted module that
 * creates a QWebView
 * loads StudyBrowser/index.html
 * listens for signals to indicate study selection
 * uses DICOMWeb rest API to pull down selected instances

## Current status:
* Able to query a list of studies at a hard-coded dcm4chee installation (experimental installation at siim.org)
* Results stored in a clickable [datatable](http://datatables.net/)
* Slicer is notified of the click and iniiates download of the instances in the selected study

## Issues
* dcm4chee provides instances in zip format, each containing one instance file, so it's not yet possible to directly load the download (ran out of time in the hackathon to finish that, but it should be easy).
* there are not yet any stable public DICOMWeb endpoints for testing.  The siim server went away at the end of the hackathon and the medicalconnections one was supposed to be working but was not available
* the standard is very new, so there's a chicken and egg issue with building an interface to it (the zipfile issue noted above with dcm4chee is an example of a non-standard behavior that makes it hard to test)

## Longer term
* The use of javascript for the datatable was very suited to the needs of DICOMWeb, since many of the key elements (json, async access...) are good in javascript.  Also lots of tools are likely to be available, like [cornerstone](https://github.com/OHIF) in javascript to leverage.
* Overall DICOMWeb is much easier than DIMSE, so the issues should all get sorted out.
