# FOMOD Validator
[![Build status](https://ci.appveyor.com/api/projects/status/3p22luum2qhnoc54?svg=true)](https://ci.appveyor.com/project/GandaG/fomod-validator)

*Validate your FOMOD installers.*

This little app allows you validate and check for common errors in your FOMOD installers.
Simply place the path to your package (the source files) and press `Validate` and,
according to your selections, it will provide with your results. Simple, easy and effective.


## Download and Install

On Windows, grab the [executable](https://github.com/GandaG/fomod-validator/releases/latest),
unzip to a location of your choosing and run `FOMOD Validator.exe`.

For all other operating systems, the *Validator* is available as a python package:

```
pip install fomod-validator
```

In all systems the *Validator* is also available as a command-line interface. In Windows
use the executable while the python package installs the cli system-wide. For more
information run the cli with the `--help` argument.


## For Developers

It is recommended to use a virtualenv to develop this package.
The development environment's requirements are listed in `requirements.txt`:

```
pip install -r requirements.txt
```

`tox` is used for everything else. The `check` env lints the code, `clean` and `build`
prepare everything for building the package on Windows.

Appveyor is used to auto build and deploy on tags.


## License

***FOMOD Validator*** is licensed under the Apache 2.0 license.
