# Options Market Sentiment Calculator

Python tool that analyzes options market data to calculate sentiment scores for any ticker.

## Overview

This tool combines multiple options market indicators to provide a comprehensive sentiment analysis:
- **Put/Call Ratios** (volume and open interest)
- **Implied Volatility Skew** (put vs call IV premium)
- **Volume Pattern Analysis** (fresh positioning indicators)

The result is a composite sentiment score ranging from -100 (Strongly Bearish) to +100 (Strongly Bullish).

## Features

- Works with any optionable ticker (stocks, ETFs, indices)
- Configurable expiration dates and OTM levels
- Data quality assessment and validation checker
- Explanations of each metric and interpretation

## Requirements

```bash
pip install yfinance pandas
```

## Quick Start

1. Run the script:
   ```bash
   python options_sentiment.py
   ```

2. Enter your parameters:
   ```
   Enter a ticker (default SPY): PLTR
   Enter an expiration date in YYYY-MM-DD (default 2025-12-19): 2025-07-25
   Enter the percent OTM (default 5): 2
   ```

3. Get comprehensive sentiment analysis with validation guidance

## Example Output

```
=== Results for PLTR ===
Current stock price: $154.86
Analyzing options 2.0% OTM

OTM Calls (strike >= $157.96):
  Number of strikes: 18
  Total volume: 31,810
  Total open interest: 0
  Most active strikes by volume:
    $160.00: Vol=16,510.0, OI=0.0, IV=12.5%
    $165.00: Vol=7,111.0, OI=0.0, IV=25.0%
    $162.50: Vol=5,428.0, OI=0.0, IV=25.0%
    $172.50: Vol=1,153.0, OI=0.0, IV=50.0%
    $167.50: Vol=743.0, OI=0.0, IV=25.0%

OTM Puts (strike <= $151.76):
  Number of strikes: 46
  Total volume: 65,068.0
  Total open interest: 0.0
  Most active strikes by volume:
    $150.00: Vol=20,257.0, OI=0.0, IV=12.5%
    $149.00: Vol=15,298.0, OI=0.0, IV=25.0%
    $140.00: Vol=5,343.0, OI=0.0, IV=50.0%
    $148.00: Vol=4,035.0, OI=0.0, IV=25.0%
    $137.00: Vol=2,584.0, OI=0.0, IV=50.0%

=== Sentiment Analysis ===

1. Put/Call Ratios:
   Volume Ratio: 2.05
   Open Interest Ratio: 0.00
   Total Volume: 31,810 calls, 65,068.0 puts
   Context:
   ⚠️  Extremely high P/C ratio - check for unusual events

2. Implied Volatility Analysis:
   Average Call IV: 20.1%
   Average Put IV: 27.6%
   IV Skew (Put - Call): 7.5%
   Context:
   📊 High put IV premium - bearish sentiment

3. Volume Pattern Analysis:
   Call Vol/OI Ratio: 11154.78
   Put Vol/OI Ratio: 11042.97
   Fresh Positioning Bias: -111.81
   Context:
   📊 High activity in both calls and puts - volatile market

4. Data Quality Assessment:
   Quality Score: 4/6
   📊 Moderate quality data - reasonably reliable
   Considerations:
   • Low open interest - limited liquidity
   💡 High activity suggests institutional interest or major event

=== COMPOSITE SENTIMENT SCORE: -2.2 ===
Interpretation: Neutral
```

## The Metrics

### Put/Call Ratio
- **Volume Ratio**: Put volume ÷ Call volume
- **Interpretation**: Higher ratio = more bearish sentiment
- **Typical Range**: 0.5-2.0 (>1.5 = strong bearish, <0.7 = bullish)

### Implied Volatility Skew
- **Calculation**: Average Put IV - Average Call IV
- **Interpretation**: Positive skew = put premium (fear), negative = call premium (greed)
- **Typical Range**: -2% to +10% (>5% = significant fear premium)

### Volume Pattern Analysis
- **Vol/OI Ratio**: Volume ÷ Open Interest
- **Fresh Positioning**: Difference between put and call Vol/OI ratios
- **Interpretation**: Higher ratios = more new positions being opened

### Composite Score Calculation
The final sentiment score combines all metrics with weights:
- Put/Call Ratio: 40%
- IV Skew: 30%
- Volume Patterns: 30%

## Data Validation

1. **Multiple Timeframes**: Test 1-month, 3-month, and 6-month expirations
2. **Multiple OTM Levels**: Compare 5%, 10%, and 15% OTM options
3. **Peer Comparison**: Check similar stocks or sector ETFs
4. **Recent Events**: Look at earnings, news, or market events

## Limitations & Considerations

- **Low Volume Warning**: Less reliable with <100 total volume
- **Expiration Effects**: Weekly options may show different patterns than monthly
- **Data Delays**: yfinance data may have slight delays

## Advanced Usage Tips

### For Institutional Positioning
- Look for unusual OI combined with low volume (existing large positions)
- High volume with low OI suggests new institutional activity

### For Retail Sentiment
- Very high put/call ratios often indicate retail fear (contrarian signal)
- Extreme OTM activity typically retail speculation

### For Event Trading
- IV skew expansion before earnings/events
- Volume spikes in specific strikes may indicate informed trading

## Troubleshooting

**"No options data available"**
- Check if the ticker has options
- Verify expiration date format (YYYY-MM-DD)
- Try a closer expiration date

**"Low quality data warning"**
- Try a more liquid ticker or closer expiration
- Use a related ETF for sector sentiment

**Extreme sentiment scores**
- Validate with multiple metrics and timeframes
- Check for recent news or events affecting the underlying

## Upcoming features
- Possibly implementing additional options metrics (gamma, charm, etc.)
- Adding a chart/GUI
- Ability to stream real-time data

## License
Open source

## Credits
Claude.ai, an AI coding assistant, was partially used in the creation of this program and README.
---

*Disclaimer: This tool is for educational and informational purposes only. Options trading involves substantial risk and is not suitable for all investors. Always conduct your own research and consider consulting with a financial advisor.*