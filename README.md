# Table of Contents
- [Table of Contents](#table-of-contents)
- [Analysis on CSGO Skins in the Steam Community Market](#analysis-on-csgo-skins-in-the-steam-community-market)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
# Analysis on CSGO Skins in the Steam Community Market

A series of Jupyter Notebooks and python scripts used to query data from the Steam community market and analyze the collected data. Read more [here](https://whuang37.github.io/csgo_market/)

# Installation

- clone the github repository in your local system `git clone https://github.com/whuang37/csgo_market.git`
- move into the repository with `cd csgo_market`
- install all libraries mentioned in [requirements.txt](https://github.com/whuang37/csgo_market/blob/master/requirements.txt) using `pip install -r requirements.txt`
- Run the .ipynb and .py files

# Usage

All jupyter notebooks in this repository are setup so that you can run all cells together to query all necessary data. Run all cells in pull_skin_names.ipynb to get a series of .xlsx files with all CSGO items from csgostash.com. Then run get_market_history.ipynb to query the market history itself. NOTE a .py version of get_market_history.ipynb is included in case Jupyter servers crash. Full querying time will take **10+ hours**.

# Contributing

Any contributions are free to make pull requests. I will review and merge accordingly.