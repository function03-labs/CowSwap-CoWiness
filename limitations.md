# Limitations of the CoW Extraction Algorithm

We compute CoWs from auctions by creating a Directed Graph (DiGraph) using the networkx library and mapping the different transfer events that occur. Every transfer represents an edge between the settlement node and the external contract. We then check for the presence of cycles after every transfer process (relying on interactions put out some edge cases).

## Outline:
- Successful Cases
  - ✅ External DEX Swap + Routing to Different Pools
  - ✅ Simple Swaps with Partially Internalized Trades
  - ✅ One Main Intermediary Address
  - ✅ Multi-hop Swaps
- Unsuccessful Cases
  - ❌ Complex Batch Auctions with One Main Intermediary Address
  - ❌ Complex Multi-Hop Swaps (> 2 intermediary tokens)
- Possible Solutions and Future Work

## Successful Cases

The CoW extraction algorithm can handle various situations, such as multi-hop swaps and external DEX swaps accurately.

### ✅ Batch auction with external DEX swap + routing to different pools

![Batch Auction with External DEX Swap](https://i.imgur.com/YcMAhuZ.png)

Using a DiGraph to map transfers and detecting cycles is very efficient at detecting trades that take multiple routes through different pools and can extract CoWs precisely from such auctions.

### ✅ Batch auctions with total / partially internalized trades

![Batch Auction with Simple Swaps](https://i.imgur.com/iSExbg1.png)

We can extract the volume for trades swapped externally and extract internalized trades to compute CoW.

### ✅ Batch auctions with one main intermediary address

![Batch Auction with One Main Intermediary Address](https://i.imgur.com/R06Zhh8.png)

These cases are trickier but work as long as there are cycles that form with that address. For example, the number of tokens sent is equal to the number of tokens received (such as the example above).

### ✅ Multi-hop swaps

![Multi-hop Swaps](https://i.imgur.com/S7Dfshc.png)

Our algorithm can detect simple multi-hop trades and cancel detected intermediary trades (e.g., USDT -> WETH -> USDC; we simplify the trade to USDT -> USDC).

## Unsuccessful Cases

The algorithm may encounter difficulties when processing complex batch auctions or those with intermediary addresses.

### ❌ Complex Batch auctions with one main intermediary address (> 30 logs emitted or uneven cycles)

![Complex Batch Auction](https://i.imgur.com/GeJOmc8.png)

Such trades are not detectable yet by the algorithm.

### ❌ Batch auctions with multiple hop swaps (e.g., > 2 intermediary token swaps)

![Multiple Hop Swaps](https://i.imgur.com/pqOUmx3.png)

These include trades where more than one token are swapped before swapping back to the needed token (e.g., USDT -> WETH -> OHM -> BTRFLY).

## Conclusion

Our current algorithm can handle various situations but encounters difficulties when processing complex batch auctions or those with intermediary addresses. Checking the majority of cases that fail, we found that most of them do not feature any coincidence of wants between orders. As such, we think the current implementation will not impact the calculations for CoW volumes / leaderboard stats. However, it's still important to resolve them and build an exhaustive framework to cover most CoWs.

## Possible Solutions and Future Work

- Developing a more advanced algorithm for detecting CoWs in complex situations
- Incorporating machine learning techniques to help identify and classify CoW scenarios more accurately
- Dissecting and analyzing more real-world cases to identify other potential edge cases and refine the algorithm as needed
- Utilizing advanced graph-based approaches and tools to improve performance and efficiency (MultiDiGraph potentially)
- Collaborating with the community to validate and improve the algorithm further
