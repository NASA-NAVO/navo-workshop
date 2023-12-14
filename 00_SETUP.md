# Configuring the Workshop Environment
These directions walk through installing miniconda, a lightweight distribution of the python package installer conda, downloading the NAVO workshop material, then creating and testing the custom environment for the  workshop.

## 1. Install Miniconda (if needed)

*Miniconda is a free minimal installer for conda. It is a small, bootstrap
version of Anaconda that includes only conda, Python, the packages they depend
on, and a small number of other useful packages, including pip, zlib and a few
others. Note, though, that if you have either Miniconda or the full Anaconda
already installed, you can skip to the next step.*

Check if Miniconda is already installed:

```console
conda info
```

If Miniconda is not already installed, follow these instructions for your
operating system: [https://docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)

On Windows, you might also need
[additional compilers](https://github.com/conda/conda-build/wiki/Windows-Compilers).

## 2. Update conda version

*Miniconda includes an environment manager called conda. Environments
allow you to have multiple sets of Python packages installed at the same
time, making reproducibility and upgrades easier. You can create,
export, list, remove, and update environments that have different versions of
Python and/or packages installed in them. For this workshop, we will configure the environment using the conda command prompt.*

Open a terminal window and verify that conda is working:

    % conda info

If you are having trouble, check your shell in a terminal window:

    % echo $SHELL

then run the initialization if needed, in that same terminal window:

    % conda init `basename $SHELL`

You should open a new terminal window after `conda init` is run.

It is advisable to update your conda to the latest version. We recommend a minimum
version of 23.10.0. Check your conda version with:

    % conda --version

Update it with:

    % conda update conda

or

    % conda update -n base conda


## 3. Install git (if needed)

At the prompt opened in the previous step, enter this command to see whether git is already installed and accessible to this shell:

```console
git --version
```

If the output shows a git version, proceed to the next step.  Otherwise install git by entering the following command and following the prompts:

```console
conda install git
```

## 4. Clone This Repository

Download the workshop folder using
[git](https://help.github.com/articles/set-up-git/):

```console
git clone https://github.com/NASA-NAVO/navo-workshop
```

## 5. Create a conda environment for the workshop

*For this workshop, the python version and all needed packages are listed in the
[environment.yml](https://github.com/NASA-NAVO/navo-workshop/blob/main/environment.yml) file.*

Navigate to the workshop directory in the terminal. For example, if you installed
the navo-workshop directory in your home directory, you could type the
following:

```console
cd navo-workshop
```

To install and activate the conda environment for the workshop, type:

```console
conda env create --file environment.yml
conda activate navo-env
```

The creation of the environment can take some time to run.

## 6. Check Installation

The name of the new conda environment created above should be displayed next
to the terminal prompt:

```console
(navo-env)
```

Run the `check_env.py` script to check the Python environment and some of the
required dependencies:

```console
python check_env.py
```

## 7. Starting Jupyterlab
From the directory containing the notebooks:

```console
jupyter lab
```

## 8. Handling Notebooks in MyST-Markdown format

The Jupyter notebooks in this repository are in
[MyST-Markdown format](https://myst-nb.readthedocs.io/en/v0.13.2/use/markdown.html).
The [jupytext](https://jupytext.readthedocs.io/en/latest/index.html) package is
included in your `navo-env` environment to work with these notebooks. Note that
the `jupytext` package has to be installed before your Jupyterlab session starts.

To open one of these notebooks (in the `content/reference_notebooks` and the
`content/use_case_notebooks` subdirectories), in the Jupyterlab file panel,
right-click on the notebook, choose "Open With", and select "Notebook" or
"Jupytext Notebook" from the drop-down menu. See the screenshot below.

![Right-click on Markdown notebook](_static/jupytext_rightclick.png "Open With Notebook")

It is possible to change your Jupyterlab settings to allow double-clicking on a
Markdown notebook to open automatically as a Jupytext Notebook. In Jupyterlab,
navigate from the top-level menu item "Settings" and select "Settings Editor"
in the drop-down. In the left sidebar of the Setting Editor tab, select
"Document Manager". The display should look like the image included below. In
the "Default Viewers" section, add a `newKey` of `markdown` and a `New Value`
of `Jupytext Notebook`. This will allow a double-click to open the Markdown
notebooks appropriately.

![Jupyterlab Document Manager settings](_static/jupytext_settings.png "Open Notebooks with Jupytext")

## Additional Resources

- [Set up git](https://help.github.com/articles/set-up-git/)
- [Conda Users Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/)
