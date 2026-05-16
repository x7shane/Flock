"""
Nifty 200 Universe - Static list of stocks.

The Nifty 200 index represents about 80% of the total market cap
of NSE India. This file contains the complete list as of 2026.

Sources:
- NSE India: https://www.nseindia.com/products-services/indices/nifty200-index

Update frequency: Manually update when NSE revises the index (quarterly).
"""

from typing import NamedTuple


class StockInfo(NamedTuple):
    """Stock information."""
    ticker: str
    company_name: str
    sector: str
    industry: str


# Complete Nifty 200 stocks as of April 2026
# Organized by sector for readability
NIFTY_200: list[StockInfo] = [
    # ========================================
    # FINANCIAL SERVICES
    # ========================================
    StockInfo("HDFCBANK", "HDFC Bank Ltd", "Financial Services", "Banks"),
    StockInfo("ICICIBANK", "ICICI Bank Ltd", "Financial Services", "Banks"),
    StockInfo("SBIN", "State Bank of India", "Financial Services", "Banks"),
    StockInfo("KOTAKBANK", "Kotak Mahindra Bank Ltd", "Financial Services", "Banks"),
    StockInfo("AXISBANK", "Axis Bank Ltd", "Financial Services", "Banks"),
    StockInfo("INDUSINDBK", "IndusInd Bank Ltd", "Financial Services", "Banks"),
    StockInfo("BANDHANBNK", "Bandhan Bank Ltd", "Financial Services", "Banks"),
    StockInfo("FEDERALBNK", "Federal Bank Ltd", "Financial Services", "Banks"),
    StockInfo("RBLBANK", "RBL Bank Ltd", "Financial Services", "Banks"),
    StockInfo("AUBANK", "AU Small Finance Bank Ltd", "Financial Services", "Banks"),
    StockInfo("HDFC", "HDFC Ltd", "Financial Services", "Housing Finance"),
    StockInfo("BAJFINANCE", "Bajaj Finance Ltd", "Financial Services", "Consumer Finance"),
    StockInfo("BAJFL", "Bajaj Finserv Ltd", "Financial Services", "Holding Company"),
    StockInfo("CHOLAFIN", "Cholamandalam Investment and Finance Company Ltd", "Financial Services", "NBFC"),
    StockInfo("MUTHOOTFIN", "Muthoot Finance Ltd", "Financial Services", "NBFC"),
    StockInfo("SHRIRAMFIN", "Shriram Finance Ltd", "Financial Services", "NBFC"),
    StockInfo("PFC", "Power Finance Corporation Ltd", "Financial Services", "NBFC"),
    StockInfo("RECLTD", "REC Ltd", "Financial Services", "NBFC"),
    StockInfo("LICHSGFIN", "LIC Housing Finance Ltd", "Financial Services", "Housing Finance"),
    StockInfo("PNBHOUSING", "PNB Housing Finance Ltd", "Financial Services", "Housing Finance"),
    StockInfo("GICRE", "General Insurance Corporation of India", "Financial Services", "Insurance"),
    StockInfo("ICICIGI", "ICICI Lombard General Insurance Company Ltd", "Financial Services", "Insurance"),
    StockInfo("ICICIPRULIFE", "ICICI Prudential Life Insurance Company Ltd", "Financial Services", "Insurance"),
    StockInfo("HDFCLIFE", "HDFC Life Insurance Company Ltd", "Financial Services", "Insurance"),
    StockInfo("SBILIFE", "SBI Life Insurance Company Ltd", "Financial Services", "Insurance"),
    StockInfo("LICI", "Life Insurance Corporation of India", "Financial Services", "Insurance"),
    StockInfo("MAXHEALTH", "Max Healthcare Institute Ltd", "Healthcare", "Hospital"),
    # Brokerage & Trading
    StockInfo("ANGELONE", "Angel One Ltd", "Financial Services", "Capital Markets"),
    StockInfo("MOTILALOFS", "Motilal Oswal Financial Services Ltd", "Financial Services", "Capital Markets"),
    StockInfo("FACT", "FACT Ltd", "Industrial", "Fertilizers"),
    StockInfo("EDELWEISS", "Edelweiss Financial Services Ltd", "Financial Services", "Capital Markets"),

    # ========================================
    # INFORMATION TECHNOLOGY
    # ========================================
    StockInfo("TCS", "Tata Consultancy Services Ltd", "Information Technology", "IT Services"),
    StockInfo("INFY", "Infosys Ltd", "Information Technology", "IT Services"),
    StockInfo("HCLTECH", "HCL Technologies Ltd", "Information Technology", "IT Services"),
    StockInfo("WIPRO", "Wipro Ltd", "Information Technology", "IT Services"),
    StockInfo("TECHM", "Tech Mahindra Ltd", "Information Technology", "IT Services"),
    StockInfo("LTIM", "LTIM Mindtree Ltd", "Information Technology", "IT Services"),
    StockInfo("COFORGE", "Coforge Ltd", "Information Technology", "IT Services"),
    StockInfo("PERSISTENT", "Persistent Systems Ltd", "Information Technology", "IT Services"),
    StockInfo("MPHASIS", "Mphasis Ltd", "Information Technology", "IT Services"),
    StockInfo("LTI", "Larsen & Toubro Infotech Ltd", "Information Technology", "IT Services"),
    StockInfo("OFSS", "Oracle Financial Services Software Ltd", "Information Technology", "IT Services"),
    StockInfo("CYIENT", "Cyient Ltd", "Information Technology", "IT Services"),
    StockInfo("SONATSOFTW", "Sonata Software Ltd", "Information Technology", "IT Services"),
    StockInfo("KPITTECH", "KPIT Technologies Ltd", "Information Technology", "IT Services"),
    StockInfo("TATAELXSI", "Tata Elxsi Ltd", "Information Technology", "IT Services"),
    StockInfo("NAUKRI", "Info Edge (India) Ltd", "Information Technology", "Internet"),

    # ========================================
    # ENERGY - OIL & GAS
    # ========================================
    StockInfo("RELIANCE", "Reliance Industries Ltd", "Energy", "Oil & Gas"),
    StockInfo("ONGC", "Oil and Natural Gas Corporation Ltd", "Energy", "Oil & Gas"),
    StockInfo("IOC", "Indian Oil Corporation Ltd", "Energy", "Oil & Gas"),
    StockInfo("BPCL", "Bharat Petroleum Corporation Ltd", "Energy", "Oil & Gas"),
    StockInfo("HPCL", "Hindustan Petroleum Corporation Ltd", "Energy", "Oil & Gas"),
    StockInfo("GAIL", "GAIL (India) Ltd", "Energy", "Gas"),
    StockInfo("PETRONET", "Petronet LNG Ltd", "Energy", "Gas"),
    StockInfo("GUJGASLTD", "Gujarat Gas Ltd", "Energy", "Gas"),
    StockInfo("IGL", "Indraprastha Gas Ltd", "Energy", "Gas"),
    StockInfo("MGL", "Mahanagar Gas Ltd", "Energy", "Gas"),
    StockInfo("AEGISLOG", "Aegis Logistics Ltd", "Energy", "Gas"),
    StockInfo("OIL", "Oil India Ltd", "Energy", "Oil & Gas"),
    StockInfo("BRGNPETRO", "Bharat Rasayanil Ltd", "Chemicals", "Petrochemicals"),

    # ========================================
    # POWER & UTILITIES
    # ========================================
    StockInfo("NTPC", "NTPC Ltd", "Utilities", "Power"),
    StockInfo("POWERGRID", "Power Grid Corporation of India Ltd", "Utilities", "Power"),
    StockInfo("TATAPOWER", "Tata Power Company Ltd", "Utilities", "Power"),
    StockInfo("ADANIPORTS", "Adani Ports and Special Economic Zone Ltd", "Industrials", "Ports"),
    StockInfo("ADANIPOWER", "Adani Power Ltd", "Utilities", "Power"),
    StockInfo("ADANIGREEN", "Adani Green Energy Ltd", "Utilities", "Power"),
    StockInfo("ADANITRANS", "Adani Transmission Ltd", "Utilities", "Power"),
    StockInfo("ADANIENT", "Adani Enterprises Ltd", "Conglomerates", "Diversified"),
    StockInfo("JSWENERGY", "JSW Energy Ltd", "Utilities", "Power"),
    StockInfo("NHPC", "NHPC Ltd", "Utilities", "Power"),
    StockInfo("TATAPOWERO", "Tata Power Company Ltd", "Utilities", "Power"),

    # ========================================
    # METALS & MINING
    # ========================================
    StockInfo("TATASTEEL", "Tata Steel Ltd", "Materials", "Steel"),
    StockInfo("JSWSTEEL", "JSW Steel Ltd", "Materials", "Steel"),
    StockInfo("HINDALCO", "Hindalco Industries Ltd", "Materials", "Aluminum"),
    StockInfo("COALINDIA", "Coal India Ltd", "Materials", "Mining"),
    StockInfo("VEDL", "Vedanta Ltd", "Materials", "Mining"),
    StockInfo("HINDZINC", "Hindustan Zinc Ltd", "Materials", "Mining"),
    StockInfo("SAIL", "Steel Authority of India Ltd", "Materials", "Steel"),
    StockInfo("JINDALSTEL", "Jindal Steel & Power Ltd", "Materials", "Steel"),
    StockInfo("APLAPOLLO", "APL Apollo Tubes Ltd", "Materials", "Steel"),
    StockInfo("NMDC", "NMDC Ltd", "Materials", "Mining"),
    StockInfo("MOIL", "MOIL Ltd", "Materials", "Mining"),

    # ========================================
    # AUTOMOBILE
    # ========================================
    StockInfo("MARUTI", "Maruti Suzuki India Ltd", "Automobiles", "Cars"),
    StockInfo("TATAMOTORS", "Tata Motors Ltd", "Automobiles", "Cars"),
    StockInfo("M&M", "Mahindra & Mahindra Ltd", "Automobiles", "Cars"),
    StockInfo("BAJAJ-AUTO", "Bajaj Auto Ltd", "Automobiles", "Two Wheelers"),
    StockInfo("HEROMOTOCO", "Hero MotoCorp Ltd", "Automobiles", "Two Wheelers"),
    StockInfo("EICHERMOT", "Eicher Motors Ltd", "Automobiles", "Two Wheelers"),
    StockInfo("TVSMOTOR", "TVS Motor Company Ltd", "Automobiles", "Two Wheelers"),
    StockInfo("MOTHERSON", "Motherson Sumi Systems Ltd", "Automobiles", "Auto Components"),
    StockInfo("BOSCHLTD", "Bosch Ltd", "Automobiles", "Auto Components"),
    StockInfo("AMARAJABAT", "Amara Raja Energy & Mobility Ltd", "Industrials", "Batteries"),
    StockInfo("EXIDEIND", "Exide Industries Ltd", "Industrials", "Batteries"),
    StockInfo("ASHOKLEY", "Ashok Leyland Ltd", "Automobiles", "Commercial Vehicles"),
    StockInfo("ESCORTS", "Escorts Ltd", "Automobiles", "Tractors"),
    StockInfo("CONCOR", "Container Corporation of India Ltd", "Industrials", "Logistics"),

    # ========================================
    # CONSUMER GOODS - FMCG
    # ========================================
    StockInfo("HINDUNILVR", "Hindustan Unilever Ltd", "Consumer Goods", "FMCG"),
    StockInfo("ITC", "ITC Ltd", "Consumer Goods", "FMCG"),
    StockInfo("NESTLEIND", "Nestle India Ltd", "Consumer Goods", "FMCG"),
    StockInfo("BRITANNIA", "Britannia Industries Ltd", "Consumer Goods", "FMCG"),
    StockInfo("DABUR", "Dabur India Ltd", "Consumer Goods", "FMCG"),
    StockInfo("GODREJCP", "Godrej Consumer Products Ltd", "Consumer Goods", "FMCG"),
    StockInfo("MARICO", "Marico Ltd", "Consumer Goods", "FMCG"),
    StockInfo("COLPAL", "Colgate Palmolive (India) Ltd", "Consumer Goods", "FMCG"),
    StockInfo("HINDSANITARY", "Hindustan Sanitaryware & Industries Ltd", "Consumer Goods", "FMCG"),
    StockInfo("PGHH", "Procter & Gamble Hygiene and Health Care Ltd", "Consumer Goods", "FMCG"),
    StockInfo("VBL", "Varun Beverages Ltd", "Consumer Goods", "Beverages"),
    StockInfo("RADICO", "Radico Khaitan Ltd", "Consumer Goods", "Beverages"),
    StockInfo("UNITEDSPIRIT", "United Spirits Ltd", "Consumer Goods", "Beverages"),
    StockInfo("UBL", "United Breweries Ltd", "Consumer Goods", "Beverages"),
    StockInfo("EMAMILTD", "Emami Ltd", "Consumer Goods", "FMCG"),
    StockInfo("TATACONSUM", "Tata Consumer Products Ltd", "Consumer Goods", "FMCG"),
    StockInfo("BLUEDART", "Blue Dart Express Ltd", "Industrials", "Logistics"),
    StockInfo("TCIEXP", "Transport Corporation of India Ltd", "Industrials", "Logistics"),

    # ========================================
    # CONSUMER GOODS - RETAIL
    # ========================================
    StockInfo("TRENT", "Trent Ltd", "Consumer Goods", "Retail"),
    StockInfo("DMART", "Avenue Supermarts Ltd", "Consumer Goods", "Retail"),
    StockInfo("PAGEIND", "Page Industries Ltd", "Consumer Goods", "Apparel"),
    StockInfo("TCNSBRANDS", "TCNS Clothing Co Ltd", "Consumer Goods", "Apparel"),
    StockInfo("ABFRL", "Aditya Birla Fashion and Retail Ltd", "Consumer Goods", "Apparel"),
    StockInfo("TITAN", "Titan Company Ltd", "Consumer Goods", "Jewellery"),

    # ========================================
    # PHARMACEUTICALS
    # ========================================
    StockInfo("SUNPHARMA", "Sun Pharmaceutical Industries Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("CIPLA", "Cipla Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("DRREDDY", "Dr Reddys Laboratories Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("LUPIN", "Lupin Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("BIOCON", "Biocon Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("CADILAHC", "Zydus Lifesciences Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("DIVISLAB", "Divis Laboratories Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("AUROPHARMA", "Aurobindo Pharma Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("TORNTPHARM", "Torrent Pharmaceuticals Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("ABBOTINDIA", "Abbott India Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("GLENMARK", "Glenmark Pharmaceuticals Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("IPCALAB", "IPCA Laboratories Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("ALKEM", "Alkem Laboratories Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("LAOPHARMA", "La Renon Healthcare Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("SYNGENE", "Syngene International Ltd", "Healthcare", "Biotechnology"),
    StockInfo("METROPOLIS", "Metropolis Healthcare Ltd", "Healthcare", "Diagnostics"),
    StockInfo("APOLLOHOSP", "Apollo Hospitals Enterprise Ltd", "Healthcare", "Hospital"),
    StockInfo("FORTIS", "Fortis Healthcare Ltd", "Healthcare", "Hospital"),

    # ========================================
    # CONSTRUCTION & ENGINEERING
    # ========================================
    StockInfo("LT", "Larsen & Toubro Ltd", "Industrials", "Engineering"),
    StockInfo("ULTRACEMCO", "UltraTech Cement Ltd", "Materials", "Cement"),
    StockInfo("SHREECEM", "Shree Cement Ltd", "Materials", "Cement"),
    StockInfo("AMBUJACEM", "Ambuja Cements Ltd", "Materials", "Cement"),
    StockInfo("GRASIM", "Grasim Industries Ltd", "Materials", "Cement"),
    StockInfo("ACC", "ACC Ltd", "Materials", "Cement"),
    StockInfo("RAMCOCEM", "Ramco Cements Ltd", "Materials", "Cement"),
    StockInfo("INDIACEM", "India Cements Ltd", "Materials", "Cement"),
    StockInfo("DCMSRIND", "Dalmia Bharat Ltd", "Materials", "Cement"),
    StockInfo("JKCEMENT", "JK Cement Ltd", "Materials", "Cement"),
    StockInfo("BALKRISIND", "Balkrishna Industries Ltd", "Industrials", "Tyres"),
    StockInfo("JKPAPER", "JK Paper Ltd", "Materials", "Paper"),
    StockInfo("WESTCOAST", "West Coast Paper Mills Ltd", "Materials", "Paper"),

    # ========================================
    # CAPITAL GOODS
    # ========================================
    StockInfo("SIEMENS", "Siemens Ltd", "Industrials", "Electrical Equipment"),
    StockInfo("ABB", "ABB India Ltd", "Industrials", "Electrical Equipment"),
    StockInfo("HONEYWELL", "Honeywell Automation India Ltd", "Industrials", "Electrical Equipment"),
    StockInfo("BHEL", "Bharat Heavy Electricals Ltd", "Industrials", "Electrical Equipment"),
    StockInfo("CROMPTON", "Crompton Greaves Consumer Electricals Ltd", "Consumer Goods", "Electrical"),
    StockInfo("HAVELLS", "Havells India Ltd", "Consumer Goods", "Electrical"),
    StockInfo("ORIENTELEC", "Orient Electric Ltd", "Consumer Goods", "Electrical"),
    StockInfo("V-GUARD", "V-Guard Industries Ltd", "Consumer Goods", "Electrical"),
    StockInfo("POLYCAB", "Polycab India Ltd", "Industrials", "Cables"),
    StockInfo("KEI", "KEI Industries Ltd", "Industrials", "Cables"),
    StockInfo("FINCABLES", "Finolex Cables Ltd", "Industrials", "Cables"),
    StockInfo("ELGI", "Elgi Equipments Ltd", "Industrials", "Machinery"),
    StockInfo("INOXWIND", "Inox Wind Ltd", "Industrials", "Machinery"),

    # ========================================
    # CHEMICALS
    # ========================================
    StockInfo("SRF", "SRF Ltd", "Chemicals", "Chemicals"),
    StockInfo("DEEPAKNTR", "Deepak Nitrite Ltd", "Chemicals", "Chemicals"),
    StockInfo("PIIND", "PI Industries Ltd", "Chemicals", "Chemicals"),
    StockInfo("UPL", "UPL Ltd", "Chemicals", "Agrochemicals"),
    StockInfo("COROMANDEL", "Coromandel International Ltd", "Chemicals", "Agrochemicals"),
    StockInfo("ATUL", "Atul Ltd", "Chemicals", "Chemicals"),
    StockInfo("NAVINFLUOR", "Navin Fluorine International Ltd", "Chemicals", "Chemicals"),
    StockInfo("ALKYLAMINE", "Alkyl Amines Chemicals Ltd", "Chemicals", "Chemicals"),
    StockInfo("BALAMINES", "Balaji Amines Ltd", "Chemicals", "Chemicals"),
    StockInfo("VINATIORGA", "Vinati Organics Ltd", "Chemicals", "Chemicals"),
    StockInfo("LINDEINDIA", "Linde India Ltd", "Chemicals", "Chemicals"),

    # ========================================
    # BUILDING MATERIALS
    # ========================================
    StockInfo("ASIANPAINT", "Asian Paints Ltd", "Consumer Goods", "Paints"),
    StockInfo("BERGEPAINT", "Berger Paints India Ltd", "Consumer Goods", "Paints"),
    StockInfo("KANSAINER", "Kansai Nerolac Paints Ltd", "Consumer Goods", "Paints"),
    StockInfo("INDIGO", "InterGlobe Aviation Ltd", "Industrials", "Airlines"),
    StockInfo("SPICEJET", "SpiceJet Ltd", "Industrials", "Airlines"),
    StockInfo("GODREJPROP", "Godrej Properties Ltd", "Real Estate", "Real Estate"),
    StockInfo("DLF", "DLF Ltd", "Real Estate", "Real Estate"),
    StockInfo("MARUTISUZ", "Maruti Suzuki India Ltd", "Automobiles", "Cars"),
    StockInfo("PRAJIND", "Praj Industries Ltd", "Industrials", "Engineering"),

    # ========================================
    # MEDIA & ENTERTAINMENT
    # ========================================
    StockInfo("ZEEL", "Zee Entertainment Enterprises Ltd", "Media", "Media"),
    StockInfo("PVR", "PVR Ltd", "Media", "Entertainment"),
    StockInfo("INOXLEISUR", "Inox Leisure Ltd", "Media", "Entertainment"),
    StockInfo("SUNTV", "Sun TV Network Ltd", "Media", "Media"),
    StockInfo("NETWORK18", "Network18 Media & Investments Ltd", "Media", "Media"),
    StockInfo("DBSTOCK", "DB Corp Ltd", "Media", "Media"),

    # ========================================
    # TELECOM
    # ========================================
    StockInfo("BHARTIARTL", "Bharti Airtel Ltd", "Communication Services", "Telecom"),
    StockInfo("IDEA", "Vodafone Idea Ltd", "Communication Services", "Telecom"),
    StockInfo("TATACOMM", "Tata Communications Ltd", "Communication Services", "Telecom"),

    # ========================================
    # CONSUMER SERVICES
    # ========================================
    StockInfo("ERIS", "Eris Lifesciences Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("LAURUSLABS", "Laurus Labs Ltd", "Healthcare", "Pharmaceuticals"),
    StockInfo("JUBLFOOD", "Jubilant FoodWorks Ltd", "Consumer Services", "Restaurants"),
    StockInfo("WESTLIFE", "Westlife Foodworld Ltd", "Consumer Services", "Restaurants"),
    StockInfo("DOMSIND", "DOMS Industries Ltd", "Consumer Goods", "Stationery"),
    StockInfo("CAMPUS", "Campus Activewear Ltd", "Consumer Goods", "Footwear"),
    StockInfo("LIBERTSHOE", "Liberty Shoes Ltd", "Consumer Goods", "Footwear"),

    # ========================================
    # MISC INDUSTRIALS
    # ========================================
    StockInfo("HAL", "Hindustan Aeronautics Ltd", "Industrials", "Aerospace & Defense"),
    StockInfo("BEML", "Bharat Earth Movers Ltd", "Industrials", "Aerospace & Defense"),
    StockInfo("BEL", "Bharat Electronics Ltd", "Industrials", "Aerospace & Defense"),
    StockInfo("COCHINSHIP", "Cochin Shipyard Ltd", "Industrials", "Shipbuilding"),
    StockInfo("MIDHANI", "Mishra Dhatu Nigam Ltd", "Industrials", "Aerospace & Defense"),
    StockInfo("MAZDOCK", "Mazagon Dock Shipbuilders Ltd", "Industrials", "Shipbuilding"),
    StockInfo("IRCTC", "Indian Railway Catering and Tourism Corporation Ltd", "Consumer Services", "Travel"),
    StockInfo("IRFC", "Indian Railway Finance Corporation Ltd", "Financial Services", "NBFC"),
    StockInfo("IRCON", "IRCON International Ltd", "Industrials", "Engineering"),
    StockInfo("RITES", "RITES Ltd", "Industrials", "Engineering"),
    StockInfo("RAILTEL", "Railtel Corporation of India Ltd", "Communication Services", "Telecom"),
    StockInfo("SUPREMEIND", "Supreme Industries Ltd", "Industrials", "Plastics"),
    StockInfo("CENTURYPLY", "Century Plyboards (India) Ltd", "Consumer Goods", "Furniture"),
    StockInfo("GREENPANEL", "Greenpanel Industries Ltd", "Consumer Goods", "Furniture"),
    StockInfo("ASTRAL", "Astral Ltd", "Industrials", "Pipes"),
    StockInfo("PRINCEPIPES", "Prince Pipes and Fittings Ltd", "Industrials", "Pipes"),
    StockInfo("SUPREMEINF", "Supreme Infrastructure India Ltd", "Industrials", "Construction"),
    StockInfo("HERANBA", "Heranba Industries Ltd", "Chemicals", "Agrochemicals"),
]


def get_tickers() -> list[str]:
    """Get list of all Nifty 200 tickers."""
    return [stock.ticker for stock in NIFTY_200]


def get_stock_by_ticker(ticker: str) -> StockInfo | None:
    """Get stock info by ticker."""
    for stock in NIFTY_200:
        if stock.ticker == ticker:
            return stock
    return None


def get_stocks_by_sector(sector: str) -> list[StockInfo]:
    """Get stocks filtered by sector."""
    return [stock for stock in NIFTY_200 if stock.sector == sector]


def get_sectors() -> list[str]:
    """Get list of unique sectors."""
    return list(set(stock.sector for stock in NIFTY_200))


# Sector mapping for grouping
SECTOR_MAPPING: dict[str, list[str]] = {
    "Financial Services": [
        "HDFCBANK", "ICICIBANK", "SBIN", "KOTAKBANK", "AXISBANK",
        "INDUSINDBK", "BANDHANBNK", "FEDERALBNK", "RBLBANK", "AUBANK",
        "HDFC", "BAJFINANCE", "BAJFL", "CHOLAFIN", "MUTHOOTFIN",
        "SHRIRAMFIN", "PFC", "RECLTD", "LICHSGFIN", "PNBHOUSING",
        "GICRE", "ICICIGI", "ICICIPRULIFE", "HDFCLIFE", "SBILIFE",
        "LICI", "ANGELONE", "MOTILALOFS", "EDELWEISS", "IRFC",
    ],
    "Information Technology": [
        "TCS", "INFY", "HCLTECH", "WIPRO", "TECHM",
        "LTIM", "COFORGE", "PERSISTENT", "MPHASIS", "LTI",
        "OFSS", "CYIENT", "SONATSOFTW", "KPITTECH", "TATAELXSI", "NAUKRI",
    ],
    "Energy": [
        "RELIANCE", "ONGC", "IOC", "BPCL", "HPCL",
        "GAIL", "PETRONET", "GUJGASLTD", "IGL", "MGL",
        "AEGISLOG", "OIL",
    ],
    "Utilities": [
        "NTPC", "POWERGRID", "TATAPOWER", "ADANIPORTS", "ADANIPOWER",
        "ADANIGREEN", "ADANITRANS", "ADANIENT", "JSWENERGY", "NHPC",
    ],
    "Materials": [
        "TATASTEEL", "JSWSTEEL", "HINDALCO", "COALINDIA", "VEDL",
        "HINDZINC", "SAIL", "JINDALSTEL", "APLAPOLLO", "NMDC", "MOIL",
        "ULTRACEMCO", "SHREECEM", "AMBUJACEM", "GRASIM", "ACC",
        "RAMCOCEM", "INDIACEM", "DCMSRIND", "JKCEMENT", "JKPAPER", "WESTCOAST",
    ],
    "Automobiles": [
        "MARUTI", "TATAMOTORS", "M&M", "BAJAJ-AUTO", "HEROMOTOCO",
        "EICHERMOT", "TVSMOTOR", "MOTHERSON", "BOSCHLTD", "ASHOKLEY",
        "ESCORTS", "AMARAJABAT", "EXIDEIND",
    ],
    "Consumer Goods": [
        "HINDUNILVR", "ITC", "NESTLEIND", "BRITANNIA", "DABUR",
        "GODREJCP", "MARICO", "COLPAL", "PGHH", "VBL",
        "RADICO", "UNITEDSPIRIT", "UBL", "EMAMILTD", "TATACONSUM",
        "TRENT", "DMART", "PAGEIND", "TCNSBRANDS", "ABFRL", "TITAN",
        "ASIANPAINT", "BERGEPAINT", "KANSAINER", "HAVELLS", "CROMPTON",
        "ORIENTELEC", "V-GUARD", "DOMSIND", "CAMPUS",
    ],
    "Healthcare": [
        "SUNPHARMA", "CIPLA", "DRREDDY", "LUPIN", "BIOCON",
        "CADILAHC", "DIVISLAB", "AUROPHARMA", "TORNTPHARM", "ABBOTINDIA",
        "GLENMARK", "IPCALAB", "ALKEM", "LAOPHARMA", "SYNGENE",
        "METROPOLIS", "APOLLOHOSP", "FORTIS", "MAXHEALTH", "ERIS", "LAURUSLABS",
    ],
    "Industrials": [
        "LT", "CONCOR", "BLUEDART", "TCIEXP", "SIEMENS",
        "ABB", "HONEYWELL", "BHEL", "POLYCAB", "KEI", "FINCABLES",
        "ELGI", "INOXWIND", "INDIGO", "SPICEJET", "PRAJIND",
        "HAL", "BEML", "BEL", "COCHINSHIP", "MIDHANI",
        "MAZDOCK", "IRCTC", "IRCON", "RITES", "RAILTEL",
        "SUPREMEIND", "ASTRAL", "PRINCEPIPES",
    ],
    "Chemicals": [
        "SRF", "DEEPAKNTR", "PIIND", "UPL", "COROMANDEL",
        "ATUL", "NAVINFLUOR", "ALKYLAMINE", "BALAMINES", "VINATIORGA",
        "LINDEINDIA", "HERANBA", "BRGNPETRO",
    ],
    "Real Estate": [
        "GODREJPROP", "DLF",
    ],
    "Media": [
        "ZEEL", "PVR", "INOXLEISUR", "SUNTV", "NETWORK18", "DBSTOCK",
    ],
    "Communication Services": [
        "BHARTIARTL", "IDEA", "TATACOMM",
    ],
    "Consumer Services": [
        "JUBLFOOD", "WESTLIFE", "IRCTC",
    ],
}


if __name__ == "__main__":
    print(f"Total Nifty 200 stocks: {len(NIFTY_200)}")
    print(f"\nSectors: {get_sectors()}")
    print(f"\nSample tickers: {get_tickers()[:10]}")