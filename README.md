# NASA-NAVO Notebooks

These notebooks demonstrate how to access NASA data through
python. Under the hood, they use Virtual Observatory protocols so that
the user does not need to know where the data are hosted but can
discover what is available and access it in standard ways.

They depend on the Astropy-affiliated Python package PyVO.

## Setup

To create a suitable Python environment for these notebooks, please follow the [installation and setup instructions](https://nasa-navo.github.io/navo-workshop/00_SETUP.html).

## Static Rendering of Notebooks

To view the executed notebooks without running them yourself, please see [this page for static renderings of the content](https://nasa-navo.github.io/navo-workshop/).

## Demo in Binder

This badge opens Jupyterlab session on Binder which can be used to run the workshop notebooks.

**Note** that method of running the notebooks is transient, and the session will disappear after
being left unattended for several minutes.

[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/NASA-NAVO/notebooks/main?urlpath=lab)


## Running on Sciserver

The workshop notebooks can also be run on [Sciserver](https://sciserver.org/), which offer an online jypyter platform. To use it for the workshop, follow these steps:

- Create an account on sciserver, if you do not already have one.

- Once logged in, select the *Compute* app.

- Create a container, give it name, select the *'NAVO-workshop'* image, and click *Create*. Click on the container name to launch the jupyterlab interface.

- The conda environment `navo-env` contains all the packages required to run the notebooks. The notebooks themselves are available under `/home/idies/workspace/navo-workshop`.
