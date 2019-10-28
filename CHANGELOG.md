## Changelog

#### 2.3.0 (2019-09-30)

* Added validation icons.

#### 2.2.2 (2019-03-07)

* Updated outdated dependencies.

#### 2.2.1 (2019-03-07)

* Fixed validation methods' return values.

#### 2.2.0 (2019-02-01)

* Fixed file check bug.
* Added warning for missing images.
* Added warning for omitted destination attributes.
* Added progress dialog for downloading updates.

#### 2.1.0 (2019-01-19)

* Added group/option type warnings:
  * SelectAtMostOne/SelectExactlyOne group with multiple required options;
  * SelectAtLeastOne/SelectExactlyOne group with no selectable options.
* Main window is no longer fixed in size.
* Improved update dialog's message.

#### 2.0.0 (2019-01-09)

* Reworked UI.
* More serious warnings or errors are now displayed on top and in red.
* More flexible backend allows for more control over produced warnings.
* New experimental feature: auto-update.
* New experimental feature: `Fix` button allows for fixing the most serious errors.

#### 1.5.3 (2016-07-11)

* Fixed issue with warnings.
* Updated schema to be in line with the latest versions of mod managers.

#### 1.5.2 (2016-06-29)

* Fixed version lookup in remote.

#### 1.5.1 (2016-06-29)

* Fixed CI server builds.

#### 1.5.0 (2016-06-29)

* Warnings should now report empty "source" fields.
* Startup should now be faster.
* Update check should now be substantially faster.

#### 1.4.1 (2016-06-13)

* Fixed incorrect flag warnings when flag value is an empty string.

#### 1.4.0 (2016-06-11)

* Warnings should now report mismatches flag labels and values as well.

#### 1.3.0 (2016-06-08)

* Warnings should now report empty installers.
* Updated application and file icon.
* The app now checks for updates at startup.
* The settings file should now be incorruptible.

#### 1.2.0 (2016-05-08)

* Warnings should now report missing images as well.

#### 1.1.1 (2016-04-25)

* Canceling the path selecting dialog should no longer clear the text field.
* The current path in the text field is now used as the base directory for the path selecting dialog.

#### 1.1.0 (2016-04-22)

* Syntax errors are now properly handled.
* All dialogs now have icons.
* Added icon to windows executable.
* Last used package path is now saved for next usage.

#### 1.0.0 (2016-04-21)

* Initial stable release.
