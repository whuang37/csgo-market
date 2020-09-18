# Analysis on the Counter Strike: Global Offensive Economy
*Investigating market trends and potential trading techniques*

## What is Counter Strike: Global Offensive?

Counter Strike: Global Offensive (CSGO) is a multiplayer first-person shooter game and the latest entry in the Counter Strike series developed by Valve and Hidden Path Entertainment. CSGO matches feature 10 players split into two teams called Counter-Terrorists and Terrorists played over a series of rounds. Teams attempt to complete objectives (destroying a bombsite/rescuing a hostage) or eliminate the enemy team in order to win the round. Despite the games age and past slumps in popularity, CSGO has seen a recent surge in popularity attributed partly to the increased Chinese interest, the free to play model, and the skin market, the subject of this project.

<br />

## The Skin Market

As has become standard in many Valve games, CSGO has a virtual economy where players can exchange real world money for weapon skins and other items. Skins and other items have no effect on the gameplay of CSGO and simply **change the cosmetic design** of weapons, character models, and end-of-round messages. These items are primarily implemented into the game through cases, loot boxes opened with a $2.49 key that contains one of a collection of skins with different rarities, that can be randomly dropped as the player levels up in-game. Players can also earn skins at the end of every match, through battle pass like events called operations, the in-game store, trading with other players, and websites, both first and third party, that specialize in selling different virtual items. 

One of these sites is the [Steam Community Market](https://steamcommunity.com/market/), the source of all data used in this project, is a first party community market where users can list their skins and items for steam credit. The Steam Community Market has become one of the go-to sites to measure a skins price, which can fluctuate and vary from item to item. Scarcity and demand can drive item prices into the thousands of dollars! How does this market react to different changes and major events? How do prices change over time? And, of course, how can we be better CSGO traders and investors? Let's find out!

<br />

## About the Data

For this project, I collected the market history data for 15,961 items with 10,328 of these items being weapon skins, knives, or gloves, 3,600 being stickers, and 2,036 being other items like cases, keys, agents, and music kits. This is a comprehensive list of all items on csgostash.com, a website listing all CSGO skins, as of September 13, 2020. I may have missed some items either due to human error or the item being too rare to be listed on the Market or csgostash.com. This sampling is, however, large enough to paint a relatively accurate picture of the CSGO skin market and make conjectures on market trends and potential trading strategies. 

All data points are taken directly from Steam's market history json request, which returns a median **listed** (15% Steam share already added) price and volume sold for each day an item was listed on the Steam Community Market. I gathered day-by-day data on all 15,961 items queried from **August 1, 2020 - September 13, 2020** (more on this later). You can get more recent data by using the included Jupyter Notebooks I created to pull a list of all skins and query the Steam Community Market using that list.