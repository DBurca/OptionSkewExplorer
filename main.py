import yfinance as yf
import pandas as pd
from datetime import datetime

def userSelect():
    print("=== Options Market Sentiment Calculator ===")

    # User selects ticker, expiration, percent OTM, and analysis criteria
    ticker = input("Enter a ticker (defaut SPY): ").strip().upper()
    exp = input("Enter an expiration date in YYYY-MM-DD (default 2025-12-19): ").strip()
    pct_in = input("Enter the percent OTM (default 5): ").strip()
    
    # Search criteria for options. Will be reinstated in a later update
    '''
    criteria = input("Which criteria would you like to analyze?\n" \
    "1 - Volume (default)\n" \
    "2 - Open Interest\n" \
    "3 - Implied Volatility\n"
    ).strip()
    '''
    criteria = 1

    # If no input is received, use defaults
    if not ticker:
        ticker = 'SPY'
    if not exp:
        exp = '2025-12-19'
    else:
        try:
            datetime.strptime(exp, '%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Using default: 2025-12-19")
            exp = '2025-12-19'
    
    try:
        pct = float(pct_in) if pct_in else 5.0
        if pct <= 0 or pct > 100:
            print("Percent OTM must be between 0 and 100. Using default: 5%")
            pct = 5.0
    except:
        print("Invalid percentage. Using default: 5%")
        pct = 5.0

    try:
        criteria = int(criteria) if criteria else 1
        if criteria < 1 or criteria > 3:
            print("Invalid analysis criteria selection, defaulting to 1")
        else:
            match criteria:
                case 1:
                    criteria = "volume"
                case 2:
                    criteria = "openInterest"
                case 3:
                    criteria = "impliedVolatility"
    except:
        print("An error occured with your analysis criteria, defaulting to 1")
        criteria = "volume"

    pct_decimal = float(pct)/100

    # Calculate percent from integer
    analyzeOpt(ticker, exp, pct_decimal, pct, criteria)
    return

def analyzeOpt(ticker, exp, pct_decimal, pct_display, criteria):
    # Using 'try' to catch errors such as bad data
    try:
        # Define the asset being used by the ticker inputed
        asset = yf.Ticker(ticker)

        # Most recent stock price
        stockPrice = asset.history(period='1d')['Close'].iloc[-1]

        # Derive calls and puts from the asset
        oChain = asset.option_chain(exp)
        calls = oChain.calls
        puts = oChain.puts

        # Check if options data exists
        if calls.empty or puts.empty:
            raise ValueError("No options data available for this stock or expiration")

        # Calculate target striked for OTM options
        callTargetStrike = stockPrice * (1 + pct_decimal)
        putTargetStrike = stockPrice * (1- pct_decimal)

        # Filter for OTM options (get all options beyond the target strikes)
        otmCalls = calls[calls['strike'] >= callTargetStrike].copy()
        otmPuts = puts[puts['strike'] <= putTargetStrike].copy()

        # Check if we have OTM options
        if otmCalls.empty or otmPuts.empty:
            print(f"Warning: Limited OTM options data at {pct_display}% level")

        # Display results
        displayResults(ticker, stockPrice, otmCalls, otmPuts, pct_display, criteria)

        # Anayze results
        calculateSentiment(otmCalls, otmPuts)
    except Exception as e:
        print(f"Error analyzing options: {str(e)}")
        print("Please check the ticker symbol and expiration date.")
        
    # Ask if user wants to analyze another ticker
    retry = input("\nAnalyze another ticker? (y/n): ").strip().lower()
    if retry in ['y', 'yes']:
        userSelect()

def displayResults(ticker, stockPrice, calls, puts, pct_display, criteria):
   # Display the analysis results
    print(f"\n=== Results for {ticker} ===")
    print(f"Current stock price: ${stockPrice:.2f}")
    print(f"Analyzing options {pct_display}% OTM")
    
    if not calls.empty:
        print(f"\nOTM Calls (strike >= ${stockPrice * (1 + pct_display/100):.2f}):")
        print(f"  Number of strikes: {len(calls)}")
        print(f"  Total volume: {calls['volume'].sum():,}")
        print(f"  Total open interest: {calls['openInterest'].sum():,}")
        
        #nlargest was originally volume

        # Show top 5 most active calls by volume
        top_calls = calls.nlargest(5, criteria)[['strike', 'volume', 'openInterest', 'impliedVolatility']]
        print(f"  Most active strikes by {criteria}:")
        for _, row in top_calls.iterrows():
            print(f"    ${row['strike']:.2f}: Vol={row['volume']:,}, OI={row['openInterest']:,}, IV={row['impliedVolatility']:.1%}")
    
    if not puts.empty:
        print(f"\nOTM Puts (strike <= ${stockPrice * (1 - pct_display/100):.2f}):")
        print(f"  Number of strikes: {len(puts)}")
        print(f"  Total volume: {puts['volume'].sum():,}")
        print(f"  Total open interest: {puts['openInterest'].sum():,}")
        
        # Show top 5 most active puts by volume
        top_puts = puts.nlargest(5, criteria)[['strike', 'volume', 'openInterest', 'impliedVolatility']]
        print(f"  Most active strikes by {criteria}:")
        for _, row in top_puts.iterrows():
            print(f"    ${row['strike']:.2f}: Vol={row['volume']:,}, OI={row['openInterest']:,}, IV={row['impliedVolatility']:.1%}")

def calculateSentiment(c, p):
    # Calculate comprehensive sentiment metrics
    print("\n=== Sentiment Analysis ===")
    
    if c.empty or p.empty:
        print("Insufficient options data for sentiment analysis")
        return
    
    # Calculate individual metrics
    pc_ratios = ratioPutCall(c, p)
    iv_metrics = impVol(c, p)
    vol_metrics = volPattern(c, p)
    
    # Display individual metrics with context
    print("\n1. Put/Call Ratios:")
    print(f"   Volume Ratio: {pc_ratios['volume_ratio']:.2f}")
    print(f"   Open Interest Ratio: {pc_ratios['oi_ratio']:.2f}")
    print(f"   Total Volume: {pc_ratios['call_volume']:,} calls, {pc_ratios['put_volume']:,} puts")
    validatePCRatio(pc_ratios['volume_ratio'])
    
    if iv_metrics:
        print("\n2. Implied Volatility Analysis:")
        print(f"   Average Call IV: {iv_metrics['avg_call_iv']:.1%}")
        print(f"   Average Put IV: {iv_metrics['avg_put_iv']:.1%}")
        print(f"   IV Skew (Put - Call): {iv_metrics['iv_skew']:.1%}")
        validateIVSkew(iv_metrics['iv_skew'])
    
    if vol_metrics:
        print("\n3. Volume Pattern Analysis:")
        print(f"   Call Vol/OI Ratio: {vol_metrics['call_vol_oi_ratio']:.2f}")
        print(f"   Put Vol/OI Ratio: {vol_metrics['put_vol_oi_ratio']:.2f}")
        print(f"   Fresh Positioning Bias: {vol_metrics['fresh_positioning']:.2f}")
        validateVolumePattern(vol_metrics)
    
    # Data quality assessment
    print("\n4. Data Quality Assessment:")
    assessDataQuality(c, p, pc_ratios)
    
    # Calculate composite sentiment score
    if iv_metrics and vol_metrics:
        sentiment_score = calcScore(pc_ratios, iv_metrics, vol_metrics)
        print(f"\n=== COMPOSITE SENTIMENT SCORE: {sentiment_score:.1f} ===")
        print(f"Interpretation: {interpretSentiment(sentiment_score)}")
        
        # Provide validation guidance
        # print("\n=== VALIDATION CHECKLIST ===")
        # provideValidationGuidance(sentiment_score, pc_ratios, iv_metrics)
    else:
        print("\nInsufficient data for composite sentiment score")

def ratioPutCall(c, p):
    # Calculate put/call ratios
    call_volume = c['volume'].sum()
    put_volume = p['volume'].sum()
    call_oi = c['openInterest'].sum()
    put_oi = p['openInterest'].sum()
    
    # Avoid division by zero
    volume_ratio = put_volume / call_volume if call_volume > 0 else 0
    oi_ratio = put_oi / call_oi if call_oi > 0 else 0
    
    return {
        'volume_ratio': volume_ratio,
        'oi_ratio': oi_ratio,
        'call_volume': call_volume,
        'put_volume': put_volume,
        'call_oi': call_oi,
        'put_oi': put_oi
    }

def impVol(c, p):
    # Calculate implied volatility metrics
    # Filter out zero or invalid IV values
    calls_with_iv = c[c['impliedVolatility'] > 0]
    puts_with_iv = p[p['impliedVolatility'] > 0]
    
    if len(calls_with_iv) == 0 or len(puts_with_iv) == 0:
        return None
    
    # Weight by volume for more accurate average
    call_iv_weighted = (calls_with_iv['impliedVolatility'] * calls_with_iv['volume']).sum() / calls_with_iv['volume'].sum()
    put_iv_weighted = (puts_with_iv['impliedVolatility'] * puts_with_iv['volume']).sum() / puts_with_iv['volume'].sum()
    
    # Fallback to simple average if no volume
    if calls_with_iv['volume'].sum() == 0:
        call_iv_weighted = calls_with_iv['impliedVolatility'].mean()
    if puts_with_iv['volume'].sum() == 0:
        put_iv_weighted = puts_with_iv['impliedVolatility'].mean()
    
    iv_skew = put_iv_weighted - call_iv_weighted
    
    return {
        'avg_call_iv': call_iv_weighted,
        'avg_put_iv': put_iv_weighted,
        'iv_skew': iv_skew
    }

def volPattern(c, p):
    # Analyze volume patterns
    # Replace zero open interest with 1 to avoid division errors
    calls_clean = c.copy()
    puts_clean = p.copy()
    
    calls_clean['openInterest'] = calls_clean['openInterest'].replace(0, 1)
    puts_clean['openInterest'] = puts_clean['openInterest'].replace(0, 1)
    
    # Calculate volume/OI ratios
    calls_clean['vol_oi_ratio'] = calls_clean['volume'] / calls_clean['openInterest']
    puts_clean['vol_oi_ratio'] = puts_clean['volume'] / puts_clean['openInterest']
    
    # Weight by volume for more meaningful averages
    total_call_volume = calls_clean['volume'].sum()
    total_put_volume = puts_clean['volume'].sum()
    
    if total_call_volume > 0 and total_put_volume > 0:
        avg_call_vol_oi = (calls_clean['vol_oi_ratio'] * calls_clean['volume']).sum() / total_call_volume
        avg_put_vol_oi = (puts_clean['vol_oi_ratio'] * puts_clean['volume']).sum() / total_put_volume
    else:
        avg_call_vol_oi = calls_clean['vol_oi_ratio'].mean()
        avg_put_vol_oi = puts_clean['vol_oi_ratio'].mean()
    
    # Fresh positioning bias: higher put vol/oi suggests more new bearish positions
    fresh_positioning = avg_put_vol_oi - avg_call_vol_oi
    
    return {
        'call_vol_oi_ratio': avg_call_vol_oi,
        'put_vol_oi_ratio': avg_put_vol_oi,
        'fresh_positioning': fresh_positioning
    }

def calcScore(pcRatio, ivMetrics, volMetrics):
    """Calculate composite sentiment score (-100 to +100)"""
    
    # Normalize Put/Call Volume Ratio (typical range: 0.3-3.0)
    # Lower ratio = bullish, higher ratio = bearish
    pc_vol_score = max(-100, min(100, (1.0 - pcRatio['volume_ratio']) * 50))
    
    # Normalize IV Skew (typical range: -0.05 to +0.15)
    # Negative skew = bullish, positive skew = bearish
    iv_score = max(-100, min(100, -ivMetrics['iv_skew'] * 500))
    
    # Normalize Fresh Positioning (volume/OI difference)
    # Negative = more fresh call buying (bullish), positive = more fresh put buying (bearish)
    vol_score = max(-100, min(100, -volMetrics['fresh_positioning'] * 25))
    
    # Apply weights
    weights = {
        'put_call_ratio': 0.4,
        'iv_skew': 0.3,
        'volume_analysis': 0.3
    }
    
    # Calculate weighted average
    composite_score = (
        pc_vol_score * weights['put_call_ratio'] +
        iv_score * weights['iv_skew'] +
        vol_score * weights['volume_analysis']
    )
    
    return composite_score

def validatePCRatio(volRatio):
    # Validate put/call ratio with historical context
    print("   Context:")
    if volRatio > 2.0:
        print("   ⚠️  Extremely high P/C ratio - check for unusual events")
    elif volRatio > 1.5:
        print("   📊 High P/C ratio - strong bearish signal")
    elif volRatio > 1.0:
        print("   📊 Elevated P/C ratio - moderate bearish signal")
    elif volRatio > 0.7:
        print("   📊 Normal P/C ratio range")
    else:
        print("   📊 Low P/C ratio - bullish signal")

def validateIVSkew(iv_skew):
    # Validate IV skew with typical ranges
    print("   Context:")
    if iv_skew > 0.10:
        print("   ⚠️  Very high put IV premium - extreme fear")
    elif iv_skew > 0.05:
        print("   📊 High put IV premium - bearish sentiment")
    elif iv_skew > 0.02:
        print("   📊 Moderate put IV premium - slight bearish bias")
    elif iv_skew > -0.02:
        print("   📊 Normal IV skew range")
    else:
        print("   📊 Call IV premium - bullish sentiment")

def validateVolumePattern(vol_metrics):
    # Validate volume patterns
    fresh_pos = vol_metrics['fresh_positioning']
    call_ratio = vol_metrics['call_vol_oi_ratio']
    put_ratio = vol_metrics['put_vol_oi_ratio']
    
    print("   Context:")
    if call_ratio > 1.0 and put_ratio > 1.0:
        print("   📊 High activity in both calls and puts - volatile market")
    elif put_ratio > 1.5:
        print("   📊 High put volume/OI - fresh bearish positioning")
    elif call_ratio > 1.5:
        print("   📊 High call volume/OI - fresh bullish positioning")
    
    if abs(fresh_pos) < 0.2:
        print("   📊 Balanced fresh positioning")

def assessDataQuality(calls, puts, pc_ratios):
    # Assess the reliability of the data
    total_volume = pc_ratios['call_volume'] + pc_ratios['put_volume']
    total_oi = pc_ratios['call_oi'] + pc_ratios['put_oi']
    
    quality_score = 0
    issues = []
    
    # Dynamic volume thresholds based on typical options activity
    volume_threshold = 50  # Lower threshold for individual stocks
    oi_threshold = 200     # Lower threshold for less liquid names
    
    # Volume assessment
    if total_volume < volume_threshold:
        issues.append("Low total volume - signal may be unreliable")
    elif total_volume > volume_threshold * 5:
        quality_score += 2  # Bonus for high volume
    else:
        quality_score += 1
    
    # Open interest assessment  
    if total_oi < oi_threshold:
        issues.append("Low open interest - limited liquidity")
    elif total_oi > oi_threshold * 3:
        quality_score += 2  # Bonus for high OI
    else:
        quality_score += 1
    
    # Balance check - ensure both calls and puts have meaningful activity
    min_activity = min(pc_ratios['call_volume'], pc_ratios['put_volume'])
    if min_activity < 5:
        issues.append("Very unbalanced call/put activity - one-sided signal")
    elif min_activity > 50:
        quality_score += 1
    
    # Strike range check
    if len(calls) < 2 or len(puts) < 2:
        issues.append("Very limited strike range - narrow analysis")
    elif len(calls) >= 5 and len(puts) >= 5:
        quality_score += 1
    
    # Liquidity quality check
    calls_with_volume = len(calls[calls['volume'] > 0])
    puts_with_volume = len(puts[puts['volume'] > 0])
    
    if calls_with_volume < 2 or puts_with_volume < 2:
        issues.append("Few strikes with actual trading activity")
    
    # Adjust scoring scale for better granularity
    max_score = 6
    print(f"   Quality Score: {quality_score}/{max_score}")
    
    if quality_score >= 5:
        print("   ✅ High quality data - reliable analysis")
    elif quality_score >= 3:
        print("   📊 Moderate quality data - reasonably reliable")
    else:
        print("   ⚠️  Lower quality data - use results with caution")
    
    if issues:
        print("   Considerations:")
        for issue in issues:
            print(f"   • {issue}")
    
    # Additional context for different ticker types
    if total_volume > 2000:
        print("   💡 High activity suggests institutional interest or major event")
    elif total_volume < 20:
        print("   💡 Consider using closer expiration or more liquid ticker for comparison")

def provideValidationGuidance(sentiment_score, pc_ratios, iv_metrics):
    # Provide specific validation steps
    print("To validate this signal:")
    
    print("1. 📈 Check recent price action & context:")
    print("   - Has the underlying dropped recently? (bearish signals stronger after declines)")
    print("   - Any sector-specific or company news affecting sentiment?")
    print("   - Check sector volatility and peer comparison")
    
    print("\n2. 🔍 Cross-reference with multiple parameters:")
    print("   - Try different expiration dates (near-term vs long-term)")
    print("   - Compare with different OTM levels (2%, 10%, 15%)")
    print("   - Test on sector ETF or related tickers for confirmation")
    
    if pc_ratios['volume_ratio'] > 1.5:
        print("\n3. ⚡ High P/C ratio - investigate:")
        print("   - Institutional hedging vs retail speculation?")
        print("   - Earnings, events, or announcements approaching?")
        print("   - Compare to typical P/C ratio for this ticker's sector")
    
    if iv_metrics['iv_skew'] > 0.05:
        print("\n4. 📊 High IV skew - validate:")
        print("   - Compare to the ticker's historical IV patterns")
        print("   - Check if upcoming catalysts justify put premium")
        print("   - Sector-wide fear vs company-specific concerns?")
    
    print(f"\n5. 🎯 Signal reliability assessment:")
    total_volume = pc_ratios['call_volume'] + pc_ratios['put_volume']
    if total_volume > 1000:
        print("   📊 High volume = More reliable signal")
    elif total_volume > 300:
        print("   📊 Moderate volume = Reasonably reliable")
    else:
        print("   ⚠️  Low volume = Less reliable, use caution")
    
    print("\n6. 🏢 Sector & ticker considerations:")
    print("   - High-beta stocks: More volatile sentiment swings")
    print("   - ETFs: Reflect broader market/sector sentiment") 
    print("   - Individual stocks: Check for company-specific catalysts")
    print("   - Longer expirations: More strategic positioning, less noise")

def interpretSentiment(score):
    # Interpret the sentiment score
    if score > 50:
        return "Strongly Bullish"
    elif score > 20:
        return "Moderately Bullish"
    elif score > -20:
        return "Neutral"
    elif score > -50:
        return "Moderately Bearish"
    else:
        return "Strongly Bearish"

if __name__ == "__main__":
    userSelect()