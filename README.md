<h1 align="center">mouseTube_APIv0.5</h1>

![Build Passing](https://img.shields.io/github/actions/workflow/status/mouseTube/mousetube_APIv0.5/ci.yml?branch=ci_readme)
[![Made with Django](https://img.shields.io/badge/Made%20with-Django-blue)](https://www.djangoproject.com/)
[![Made with Django REST framework](https://img.shields.io/badge/Made%20with-Django%20REST%20framework-blue)](https://www.django-rest-framework.org/)

A temporary version of mouseTube API

<p align="center">
  <img src="https://mousetube.pasteur.fr/images/logo_mousetube_big.png" alt="Mousetube" width="50%">
</p>

## What is mouseTube?

Rodents communicate with each other through their various sensory modalities: olfaction (scent marking, glands), vision (postures), touch (contacts), and hearing (vocalizations). In the latter case, vocalizations are mainly emitted in the ultrasonic range, beyond human perception capabilities ([Anderson, 1954](https://doi.org/10.1126/science.119.3101.808); [Brudzynski, 2005](https://doi.org/10.1007/s10519-004-0858-3), [2021](https://doi.org/10.3390/brainsci11050605); [Portfors, 2007](https://www.metris.nl/media/documents/TypesandFunctionsofUSVinLabRatsandMice.pdf); [Schweinfurth, 2020](https://doi.org/10.7554/eLife.54020)).
Ultrasonic vocalizations are emitted in various contexts: by isolated pups during the first two weeks of life, by juveniles and adults during same-sex social interactions, by males in the presence of females, and by individuals in aversive or appetitive situations (restraint stress, anticipation of pain, social play, food rewards) and exploring an unfamiliar environment. These ultrasonic vocalizations are used as markers of motivation and social communication ([Fischer and Hammerschmidt, 2010](https://doi.org/10.1111/j.1601-183X.2010.00610.x); [Schweinfurth, 2020](https://doi.org/10.7554/eLife.54020)), or of susceptibility to stress or anxiety, depending on the type of signal examined ([Brudzynski, 2005](https://doi.org/10.1007/s10519-004-0858-3)).
Ultrasonic vocalizations are therefore routinely measured in rodent models of neuropsychiatric conditions ([Premoli et al., 2023](https://doi.org/10.1111/ejn.15957)).

The mechanisms of production, the temporal organization into sequences, the significance of the acoustic features, and the effect on the recipient are far from elucidated. Understanding the complexity of this communication system requires a vast amount of data to explore with high-performance analysis methods. For that purpose, we developed **mouseTube**, a database designed to facilitate sharing, archiving, and analyzing raw recording files of rodent ultrasonic vocalizations following the FAIR (Findable, Accessible, Interoperable, Reusable) principles ([Wilkinson et al., 2016](https://doi.org/10.1038/sdata.2016.18)).


## Installation

### 1. Create a Python environment

Create and activate a Python virtual environment for the project.

### 2. Create a `.env` file

Create a `.env` file at the root of the project and fill in the following variables:

```env
DEBUG=
ALLOWED_HOSTS=
DB_ENGINE=django.db.backends.mysql
DB_ROOT_PASS=
DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=127.0.0.1
DB_PORT=3306
DB_SSL=True
```

### 3. Install and start MariaDB

Before proceeding, ensure that MariaDB is installed and running. If it's not installed, use the following commands:

```bash
# Install MariaDB (if not already done)
sudo apt-get update
sudo apt-get install mariadb-server

# Start the MariaDB service
sudo systemctl start mariadb

# Verify MariaDB is running
sudo systemctl status mariadb
```

### 4. Install system dependencies

You will need to install some system dependencies before installing **mousetube_api**:

```bash
# Install necessary dependencies for MariaDB integration
sudo apt-get install pkg-config
sudo apt-get install libmariadb-dev
```

### 5. Install Python dependencies

Once the system dependencies are installed, install **mousetube_api** and its Python dependencies:

```bash
pip install -e .
```

### 6. Run the server in development mode

Finally, start the Django development server:

```bash
mousetube_api runserver
```

## Check out mouseTube's publications:

- Torquet N., de Chaumont F., Faure P., Bourgeron T., Ey E. mouseTube – a database to collaboratively unravel mouse ultrasonic communication [version 1; peer review: 2 approved]. F1000Research 2016, 5:2332 ([F1000Research Link](https://doi.org/10.12688/f1000research.9439.1)) (2016).

> **Info:**  
> This is a temporary version of **mouseTube**.  
> This version uses the same database as the initial version but with more recent and safer technologies. The main improvement is that data are now accessible without authentication.  
> If you want to share vocalization files, please contact us. This version does not allow to share files, but we can do it manually.  
> We are currently developing a new version with more functionalities.
