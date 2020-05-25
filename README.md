# Keypirinha SDK

This is [Keypirinha](http://keypirinha.com) launcher's official Software
Development Kit (SDK).


## Features

* Create an add-on skeleton to start developing your plugin
* Build a redistributable package that is ready-to-use by Keypirinha users
* Test some features with the bundled standalone Python3 interpreter, which is a
  replicate of Keypirinha's embedded one


## Download

The recommended way is to clone the official git repository as the `master`
branch is meant to be *stable*:

    git clone https://github.com/Keypirinha/SDK.git keypirinha-sdk

Otherwise, GitHub conveniently allows to [download an archive][current] of the
current revision.

[current]: https://github.com/Keypirinha/SDK/archive/master.zip


## Install

No particular configuration is required to use the SDK.


## Usage

For convenience, high-level features of the SDK are accessible via the `cmd`
directory, which you can safely add to your `PATH` since it has been made
specifically to be as non-intrusive as possible.


### Environment Setup

Once you have opened a console, you may want to setup SDK's environment by
running the `cmd/kpenv` script.

Particularly, it defines `KEYPIRINHA_SDK`, that is the path to the directory of
the SDK.

It also prepends the `cmd` directory to the `PATH` of the current console
session.


### Create a Package

This SDK allows to create the skeleton (i.e. the file and code structure) of
your package by running a single command.

Example:

    kptmpl package <MyPackName> [dest_dir]

Usage:

    kptmpl help

Note that the file structure created is not suitable to be copied as-is under
Keypirinha's `Packages` directory and is meant to be more flexible for the
developer, not the user. May you wish to redistribute your package, the
recommended way is to build it first.


### Where to start

Besides from its [documentation](http://keypirinha.com/api.html), the best
practical way to know how to use Keypirinha's API is to dig into the code of the
[official packages](https://github.com/Keypirinha/Packages.git), as well as the
`examples` directory provided by this SDK.

Also, the exposed part of Keypirinha's Python API, on which packages rely on,
has its own [repository](https://github.com/Keypirinha/PythonLib).


### Build a Package

To build a package means all the files required for Keypirinha to load your
plugin(s) will be encapsulated in a single zip archive that has got the
`*.keypirinha-package` extension so users of your package can easily download
and install it under the `profile/InstalledPackage` directory. This is the
recommended form of redistribution.

Once you have developed and tested your package, you can build its final
redistributable archive (i.e. `*.keypirinha-package`) by using the `make.cmd`
script located in your package directory.

Note that SDK's environment must be setup by running the `cmd/kpenv` script
first.

Then, from your package's directory:

    make.cmd build

Usage:

    make.cmd help


### Python Interpreter

The bootstrap script `cmd/kpy` allows to execute any Python3 script using the
bundled and standalone interpreter, which is a replicate of the one that is
embedded into Keypirinha.

You can also start the interpreter in *interactive mode*, as you would do with
the `python.exe` executable of the standard Python distribution (i.e. with no
file argument).


## License

The SDK is distributed under the terms of the `zlib` license unless stated
otherwise in files from third-party projects. See the `LICENSE` file located in
this directory for more information.


## Contribute

1. Check for open issues or open a fresh issue to start a discussion around a
   feature idea or a bug.
2. Fork [the repository][repo] on GitHub to start making your changes.
3. Send a pull request.
   Please stick to **one feature per PR**.


[repo]: https://github.com/Keypirinha/SDK.git
