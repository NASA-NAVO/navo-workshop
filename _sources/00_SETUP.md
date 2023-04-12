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
operating system: https://docs.conda.io/en/latest/miniconda.html

On Windows, you might also need
[additional compilers](https://github.com/conda/conda-build/wiki/Windows-Compilers).

## 2. Open the conda command prompt

*Miniconda includes an environment manager called conda. Environments
allow you to have multiple sets of Python packages installed at the same
time, making reproducibility and upgrades easier. You can create,
export, list, remove, and update environments that have different versions of
Python and/or packages installed in them. For this workshop, we will configure the environment using the conda command prompt.*

On Mac or Linux, the `bash` shell will handle the conda commands.  Open your terminal and verify your shell environment:

```console
echo $SHELL
```

If the output text does not contain `bash`, switch to the bash shell before
being able to run anything related to conda.

On Windows, open the `Anaconda Prompt` terminal app.

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

And finally, on any platform, to install and activate the conda environment for the workshop, type:

```console
conda env create --file environment.yml
conda activate navo-env
```

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
## Additional Resources

- [Set up git](https://help.github.com/articles/set-up-git/)
- [Conda Users Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/)
