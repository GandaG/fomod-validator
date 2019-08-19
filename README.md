# FOMOD Validator
[![Windows Build](https://img.shields.io/appveyor/ci/GandaG/fomod-validator/master.svg?style=flat-square&label=Windows%20Build)](https://ci.appveyor.com/project/GandaG/fomod-validator)

*Validate your FOMOD installers.*

> :warning: **Note**: This is a mature application with all planned features added and no known bugs - do not be alarmed by the lack of commits.

This little app allows you validate and check for common errors in your FOMOD installers.
Simply place the path to your package (the source files) and press `Validate` and,
according to your selections, it will provide with your results. Simple, easy and effective.


## Download and Install

On Windows, grab the [executable](https://github.com/GandaG/fomod-validator/releases/latest),
unzip to a location of your choosing and run `FOMOD Validator.exe`.


## For Developers

This application is developed with `pipenv`:

```
pip install pipenv
pipenv sync --dev
```

`Invoke` is used for all miscellaneous tasks.
`pipenv run inv check` runs the checks and code formatters.
`pipenv run inv build` builds the application locally.
Be sure to run both of these before every commit.

Appveyor is used to auto build and deploy on tags.


## License

***FOMOD Validator*** is licensed under the Apache 2.0 license.
