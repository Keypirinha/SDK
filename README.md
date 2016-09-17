# Keypirinha SDK

This is [Keypirinha](http://keypirinha.com) launcher's official Software
Development Kit (SDK).


## Features

* Create an add-on skeleton to start developing your plugin
* Build a redistributable package that is ready-to-use by Keypirinha users
* Test some features with its bundled standalone Python3 interpreter that is a
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

The `cmd` directory has been made specifically to be as non-intrusive as
possible by adding only the minimum required to access SDK's high-level
features.


## Usage

High-level features of the SDK are accessible via the `cmd` directory.


### Environment Setup

Once you have opened a terminal, you may want to setup SDK's environment by
running the `kpenv` script.

Particularly it defines `KEYPIRINHA_SDK`, that is the path to the directory of
the SDK.

It also prepends the `cmd` directory to the current `PATH`.


### Create a Package

Example:

    kptmpl package <MyPackName> [dest_dir]

Usage:

    kptmpl --help


### Build a Package

Once you have developed and tested your package, you can build its final
redistributable archive. Among other things, the `make.cmd` script located in
your package directory allows you to do that.

Note that the SDK's environment must be setup by running the `kpenv` script
first.

Then, from your package's directory:

    make.cmd build

Usage:

    make.cmd help


### Python Interpreter

The bootstrap script `kpy` allows to execute any Python3 script, or, if called
without argument, to start the interpreter in *interactive mode*.

It works exactly the same way than the `python.exe` executable of the standard
Python distribution.


## License

The SDK is distributed under the terms of the `zlib` license, which you can find
in the `LICENSE` file located in this directory.


## Contribute

1. Check for open issues or open a fresh issue to start a discussion around a
   feature idea or a bug.
2. Fork [the repository][repo] on GitHub to start making your changes to the
   **master** branch (or branch off of it).
3. Send a pull request.


[repo]: https://github.com/Keypirinha/SDK.git
