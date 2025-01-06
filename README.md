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

The workshop notebooks can also be run on [Sciserver](https://sciserver.org/), which offers an online Jupyter platform. To use it for the workshop, follow these steps:

- Create an account on Sciserver, if you do not already have one.

- Once logged in, select the *Compute* app.

- Create a container, give it name, select the *'NAVO-workshop'* image, and click *Create*. Click on the container name to launch the jupyterlab interface.

- The conda environment `navo-env` contains all the packages required to run the notebooks. On the file system, the notebooks are available under `/home/idies/workspace/navo-workshop`.

- You can use the Jupyterlab file browser to navigate to the `navo_workshop` then `content` directory, then either the `reference_notebooks` or `use_case_notebooks` subdirectories that contain the notebooks.
  - **Note** that each time a notebook is opened for the first time, the kernel needs to be switched to `navo-env`.  Without this step, running the notebook will result in a `ModuleNotFoundError` since the default kernel does not contain the necessary dependencies.
    - In the upper right corner of the notebook tab click on `Python 3 (ipykernel)`.
    - Choose `navo-env` from the kernel choices.
    - Click `Select`.
    - Save the notebook via `File->Save Markdown File`.

- To ensure you get the latest version of the tutorials, open the terminal (click the blue icon with + in the top left, then select Terminal), and navigate to `/home/idies/workspace/navo-workshop`, then use `git` to download the latest updates. Note that the following will remove any changes you made to the notebooks:
```sh
cd /home/idies/workspace/navo-workshop
git fetch --all
git reset --hard origin/main
```
