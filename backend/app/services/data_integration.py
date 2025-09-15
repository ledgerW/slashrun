"""Data integration layer for external APIs and scenario template generation."""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import aiohttp
from ..core.config import settings
from ..models.state import GlobalState, CountryState, Macro, External, Finance, Trade, EnergyFood, Security, Sentiment

logger = logging.getLogger(__name__)


class DataProvider:
    """Base class for external data providers."""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout))
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_data(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Fetch data from API endpoint with retry logic."""
        if not self.session:
            raise RuntimeError("DataProvider must be used as async context manager")
        
        params = params or {}
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        for attempt in range(settings.api_settings.max_retries):
            try:
                async with self.session.get(url, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    elif response.status == 429:  # Rate limited
                        wait_time = (attempt + 1) * settings.api_settings.retry_backoff_factor
                        logger.warning(f"Rate limited by {url}, waiting {wait_time}s")
                        await asyncio.sleep(wait_time)
                    else:
                        response.raise_for_status()
            except aiohttp.ClientError as e:
                if attempt == settings.api_settings.max_retries - 1:
                    logger.error(f"Failed to fetch {url} after {settings.api_settings.max_retries} attempts: {e}")
                    raise
                wait_time = (attempt + 1) * settings.api_settings.retry_backoff_factor
                await asyncio.sleep(wait_time)
        
        raise RuntimeError(f"Failed to fetch data from {url}")


class WorldBankProvider(DataProvider):
    """World Bank WDI API provider."""
    
    def __init__(self):
        super().__init__(settings.api_settings.world_bank_base_url)
    
    async def get_indicator(self, country: str, indicator: str, date: str = "2023") -> Optional[float]:
        """Get specific indicator for country."""
        try:
            endpoint = f"country/{country}/indicator/{indicator}"
            params = {"format": "json", "date": date}
            data = await self.fetch_data(endpoint, params)
            
            if len(data) > 1 and data[1]:
                # World Bank API returns [metadata, data]
                for entry in data[1]:
                    if entry.get("value") is not None:
                        return float(entry["value"])
            return None
        except Exception as e:
            logger.warning(f"Failed to get {indicator} for {country}: {e}")
            return None
    
    async def get_macro_indicators(self, country: str) -> Dict[str, Optional[float]]:
        """Get key macroeconomic indicators."""
        indicators = {
            "gdp": "NY.GDP.MKTP.CD",  # GDP current USD
            "inflation": "FP.CPI.TOTL.ZG",  # CPI YoY %
            "unemployment": "SL.UEM.TOTL.ZS",  # Unemployment rate %
            "debt_gdp": "GC.DOD.TOTL.GD.ZS",  # Central gov debt % GDP
            "exports_gdp": "NE.EXP.GNFS.ZS",  # Exports % GDP
            "imports_gdp": "NE.IMP.GNFS.ZS"   # Imports % GDP
        }
        
        results = {}
        for key, indicator_code in indicators.items():
            value = await self.get_indicator(country, indicator_code)
            if key in ["inflation", "unemployment", "debt_gdp", "exports_gdp", "imports_gdp"] and value:
                value = value / 100.0  # Convert percentages to decimals
            results[key] = value
        
        return results


class FREDProvider(DataProvider):
    """Federal Reserve Economic Data API provider."""
    
    def __init__(self):
        super().__init__(settings.api_settings.fred_base_url)
        self.api_key = settings.api_settings.fred_api_key
    
    async def get_series(self, series_id: str, limit: int = 1) -> Optional[float]:
        """Get latest value from FRED series."""
        if not self.api_key:
            logger.warning("FRED API key not configured")
            return None
        
        try:
            endpoint = "series/observations"
            params = {
                "series_id": series_id,
                "api_key": self.api_key,
                "file_type": "json",
                "limit": limit,
                "sort_order": "desc"
            }
            data = await self.fetch_data(endpoint, params)
            
            observations = data.get("observations", [])
            if observations and observations[0].get("value") != ".":
                return float(observations[0]["value"])
            return None
        except Exception as e:
            logger.warning(f"Failed to get FRED series {series_id}: {e}")
            return None
    
    async def get_us_indicators(self) -> Dict[str, Optional[float]]:
        """Get key US economic indicators from FRED."""
        series = {
            "policy_rate": "FEDFUNDS",  # Federal funds rate
            "sovereign_yield": "DGS10",  # 10-year Treasury rate
            "fx_rate": "DEXUSEU",  # USD/EUR exchange rate (inverted)
        }
        
        results = {}
        for key, series_id in series.items():
            value = await self.get_series(series_id)
            if key in ["policy_rate", "sovereign_yield"] and value:
                value = value / 100.0  # Convert percentages to decimals
            elif key == "fx_rate" and value:
                value = 1.0 / value  # Invert EUR/USD to USD/EUR
            results[key] = value
        
        return results


class IMFProvider(DataProvider):
    """IMF IFS API provider."""
    
    def __init__(self):
        super().__init__(settings.api_settings.imf_base_url)
    
    async def get_country_data(self, country: str, indicator: str) -> Optional[float]:
        """Get IMF data for country and indicator."""
        try:
            # Simplified IMF API call - actual implementation would need proper indicator codes
            endpoint = f"CompactData/IFS/M.{country}.{indicator}"
            data = await self.fetch_data(endpoint)
            
            # Parse IMF SDMX-JSON format (simplified)
            if "CompactData" in data and "DataSet" in data["CompactData"]:
                series = data["CompactData"]["DataSet"]["Series"]
                if series and "@OBS_VALUE" in series[-1]:
                    return float(series[-1]["@OBS_VALUE"])
            return None
        except Exception as e:
            logger.warning(f"Failed to get IMF data for {country}.{indicator}: {e}")
            return None


class ScenarioTemplateGenerator:
    """Generate scenario templates with real data integration."""
    
    def __init__(self):
        self.mvs_countries = ["USA", "CHN", "DEU", "JPN", "GBR", "FRA", "IND", "BRA", "CAN", "AUS"]
        self.fis_countries = [
            "USA", "CHN", "DEU", "JPN", "GBR", "FRA", "IND", "BRA", "CAN", "AUS",
            "RUS", "IDN", "MEX", "TUR", "KOR", "SAU", "NGA", "ZAF", "ARG", "THA",
            "NLD", "CHE", "BEL", "IRL", "ISR", "ARE", "SGP", "NOR", "SWE", "DNK"
        ]
    
    async def generate_mvs_template(self) -> GlobalState:
        """Generate Minimum Viable Scenario template."""
        countries = {}
        
        # Initialize with fallback values first
        for country_code in self.mvs_countries:
            countries[country_code] = self._create_fallback_country(country_code)
        
        # Attempt to fetch real data
        try:
            await self._populate_real_data(countries, is_mvs=True)
        except Exception as e:
            logger.warning(f"Failed to populate real data, using fallbacks: {e}")
        
        return GlobalState(
            t=0,
            base_ccy="USD",
            countries=countries,
            trade_matrix=self._generate_basic_trade_matrix(list(countries.keys())),
            interbank_matrix={},  # Empty for MVS
            alliance_graph=self._generate_basic_alliances(),
            sanctions={},
            io_coefficients={},  # Empty for MVS
            commodity_prices={"oil_brent": 85.0, "natgas_TTF": 30.0}
        )
    
    async def generate_fis_template(self) -> GlobalState:
        """Generate Full Information Scenario template."""
        countries = {}
        
        # Initialize with fallback values
        for country_code in self.fis_countries:
            countries[country_code] = self._create_fallback_country(country_code)
        
        # Attempt to fetch comprehensive real data
        try:
            await self._populate_real_data(countries, is_mvs=False)
        except Exception as e:
            logger.warning(f"Failed to populate comprehensive data, using fallbacks: {e}")
        
        return GlobalState(
            t=0,
            base_ccy="USD",
            countries=countries,
            trade_matrix=self._generate_comprehensive_trade_matrix(list(countries.keys())),
            interbank_matrix=self._generate_interbank_matrix(),
            alliance_graph=self._generate_comprehensive_alliances(),
            sanctions=self._generate_sanctions_matrix(),
            io_coefficients=self._generate_io_coefficients(),
            commodity_prices={
                "oil_brent": 85.0, "natgas_TTF": 30.0, "wheat": 250.0, 
                "copper": 8500.0, "gold": 2000.0, "silver": 25.0
            }
        )
    
    def _create_fallback_country(self, country_code: str) -> CountryState:
        """Create country with fallback values based on income group and size."""
        # Income group fallbacks (simplified categorization)
        income_groups = {
            "USA": "HIC", "DEU": "HIC", "JPN": "HIC", "GBR": "HIC", "FRA": "HIC",
            "CAN": "HIC", "AUS": "HIC", "CHE": "HIC", "NLD": "HIC", "BEL": "HIC",
            "CHN": "UMIC", "BRA": "UMIC", "RUS": "UMIC", "MEX": "UMIC", "TUR": "UMIC",
            "IND": "LMIC", "IDN": "LMIC", "THA": "LMIC", "NGA": "LMIC", "ZAF": "LMIC"
        }
        
        income_group = income_groups.get(country_code, "LMIC")
        
        # Fallback values by income group
        fallbacks = {
            "HIC": {
                "inflation": 0.025, "unemployment": 0.055, "debt_gdp": 0.85,
                "policy_rate": 0.03, "sovereign_yield": 0.035, "milex_gdp": 0.02,
                "tariff_mfn_avg": 0.03, "ntm_index": 0.35, "approval": 0.55
            },
            "UMIC": {
                "inflation": 0.045, "unemployment": 0.075, "debt_gdp": 0.55,
                "policy_rate": 0.055, "sovereign_yield": 0.065, "milex_gdp": 0.025,
                "tariff_mfn_avg": 0.08, "ntm_index": 0.30, "approval": 0.50
            },
            "LMIC": {
                "inflation": 0.065, "unemployment": 0.095, "debt_gdp": 0.45,
                "policy_rate": 0.075, "sovereign_yield": 0.085, "milex_gdp": 0.015,
                "tariff_mfn_avg": 0.12, "ntm_index": 0.25, "approval": 0.45
            }
        }
        
        fb = fallbacks[income_group]
        
        return CountryState(
            name=country_code,
            macro=Macro(
                gdp=None,  # To be populated with real data
                potential_gdp=None,
                inflation=fb["inflation"],
                unemployment=fb["unemployment"],
                output_gap=0.0,
                primary_balance=0.0,
                debt_gdp=fb["debt_gdp"],
                neutral_rate=0.02,
                policy_rate=fb["policy_rate"]
            ),
            external=External(
                fx_rate=1.0 if country_code == "USA" else None,
                reserves_usd=None,
                current_account_gdp=0.0
            ),
            finance=Finance(
                sovereign_yield=fb["sovereign_yield"],
                credit_spread=0.01,
                bank_tier1_ratio=0.12
            ),
            trade=Trade(
                exports_gdp=None,
                imports_gdp=None,
                tariff_mfn_avg=fb["tariff_mfn_avg"],
                ntm_index=fb["ntm_index"]
            ),
            energy=EnergyFood(
                energy_stock_to_use=1.0,
                food_price_index=120.0,
                energy_price_index=100.0
            ),
            security=Security(
                milex_gdp=fb["milex_gdp"],
                personnel=None,
                conflict_intensity=0.0
            ),
            sentiment=Sentiment(
                gdelt_tone=0.0,
                trends_salience=50.0,
                policy_pressure=0.2,
                approval=fb["approval"]
            )
        )
    
    async def _populate_real_data(self, countries: Dict[str, CountryState], is_mvs: bool = True):
        """Populate countries with real data from external APIs."""
        async with WorldBankProvider() as wb:
            for country_code, country in countries.items():
                if country_code == "USA":
                    # Special handling for USA with FRED data
                    async with FREDProvider() as fred:
                        fred_data = await fred.get_us_indicators()
                        if fred_data.get("policy_rate") is not None:
                            country.macro.policy_rate = fred_data["policy_rate"]
                        if fred_data.get("sovereign_yield") is not None:
                            country.finance.sovereign_yield = fred_data["sovereign_yield"]
                
                # Get World Bank data for all countries
                wb_data = await wb.get_macro_indicators(country_code)
                
                if wb_data.get("gdp") is not None:
                    country.macro.gdp = wb_data["gdp"]
                    # Estimate potential GDP as 95% of current (simplified)
                    country.macro.potential_gdp = wb_data["gdp"] * 0.95
                    country.macro.output_gap = (wb_data["gdp"] - country.macro.potential_gdp) / country.macro.potential_gdp
                
                if wb_data.get("inflation") is not None:
                    country.macro.inflation = wb_data["inflation"]
                
                if wb_data.get("unemployment") is not None:
                    country.macro.unemployment = wb_data["unemployment"]
                
                if wb_data.get("debt_gdp") is not None:
                    country.macro.debt_gdp = wb_data["debt_gdp"]
                
                if wb_data.get("exports_gdp") is not None:
                    country.trade.exports_gdp = wb_data["exports_gdp"]
                
                if wb_data.get("imports_gdp") is not None:
                    country.trade.imports_gdp = wb_data["imports_gdp"]
    
    def _generate_basic_trade_matrix(self, countries: List[str]) -> Dict[str, Dict[str, float]]:
        """Generate simplified trade matrix for MVS."""
        matrix = {}
        major_traders = {"USA": 0.15, "CHN": 0.18, "DEU": 0.12, "JPN": 0.06, "GBR": 0.05}
        
        for country in countries:
            matrix[country] = {}
            if country in major_traders:
                # Distribute trade shares among other countries
                share_per_partner = major_traders[country] / (len(countries) - 1)
                for partner in countries:
                    if partner != country:
                        matrix[country][partner] = share_per_partner
        
        return matrix
    
    def _generate_comprehensive_trade_matrix(self, countries: List[str]) -> Dict[str, Dict[str, float]]:
        """Generate comprehensive trade matrix for FIS with realistic bilateral flows."""
        # Simplified implementation - real version would use UN Comtrade data
        matrix = {}
        
        # Major trade relationships (simplified)
        trade_relationships = {
            "CHN": {"USA": 0.18, "DEU": 0.08, "JPN": 0.06, "KOR": 0.05},
            "USA": {"CHN": 0.16, "MEX": 0.15, "CAN": 0.13, "JPN": 0.04},
            "DEU": {"USA": 0.09, "CHN": 0.08, "FRA": 0.08, "NLD": 0.07},
        }
        
        for country in countries:
            matrix[country] = trade_relationships.get(country, {})
        
        return matrix
    
    def _generate_basic_alliances(self) -> Dict[str, Dict[str, float]]:
        """Generate basic alliance structure for MVS."""
        return {
            "USA": {"CAN": 1.0, "GBR": 1.0, "FRA": 1.0, "DEU": 1.0, "JPN": 1.0, "AUS": 1.0},
            "CHN": {"RUS": 0.7} if "RUS" in self.mvs_countries else {},
            "RUS": {"CHN": 0.7} if "CHN" in self.mvs_countries else {}
        }
    
    def _generate_comprehensive_alliances(self) -> Dict[str, Dict[str, float]]:
        """Generate comprehensive alliance structure for FIS."""
        return {
            "USA": {"CAN": 1.0, "GBR": 1.0, "FRA": 1.0, "DEU": 1.0, "JPN": 1.0, "AUS": 1.0, "KOR": 1.0},
            "CHN": {"RUS": 0.7, "IDN": 0.5, "BRA": 0.3},
            "RUS": {"CHN": 0.7, "IND": 0.4, "BRA": 0.3},
            "IND": {"RUS": 0.4, "BRA": 0.3},
            "NATO": {"USA": 1.0, "GBR": 1.0, "FRA": 1.0, "DEU": 1.0, "CAN": 1.0, "TUR": 1.0, "NOR": 1.0}
        }
    
    def _generate_interbank_matrix(self) -> Dict[str, Dict[str, float]]:
        """Generate interbank exposure matrix (USD billions)."""
        # Based on BIS Consolidated Banking Statistics (simplified)
        return {
            "USA": {"GBR": 120.0, "JPN": 80.0, "CHE": 60.0, "DEU": 45.0},
            "GBR": {"USA": 140.0, "DEU": 60.0, "FRA": 50.0, "IRL": 40.0},
            "JPN": {"USA": 85.0, "GBR": 35.0, "AUS": 25.0, "SGP": 20.0},
            "DEU": {"GBR": 55.0, "USA": 40.0, "FRA": 35.0, "NLD": 30.0}
        }
    
    def _generate_sanctions_matrix(self) -> Dict[str, Dict[str, float]]:
        """Generate sanctions intensity matrix."""
        # Based on GSDB data (simplified)
        return {
            "USA": {"RUS": 0.9, "IRN": 0.8, "PRK": 0.95, "VEN": 0.7},
            "EU27": {"RUS": 0.85, "IRN": 0.6, "BLR": 0.7},
            "RUS": {"UKR": 0.9},
            "CHN": {"TWN": 0.3}
        }
    
    def _generate_io_coefficients(self) -> Dict[str, Dict[str, float]]:
        """Generate input-output coefficients (simplified)."""
        # Based on OECD ICIO structure (highly simplified)
        return {
            "Agriculture": {"Food": 0.65, "Chemicals": 0.15},
            "Mining": {"Manufacturing": 0.45, "Energy": 0.35, "Construction": 0.20},
            "Manufacturing": {"Services": 0.25, "Construction": 0.20, "Transport": 0.15},
            "Energy": {"Manufacturing": 0.40, "Services": 0.30, "Transport": 0.20},
            "Services": {"Manufacturing": 0.20, "Construction": 0.15, "Government": 0.25}
        }


# Template generator instance
template_generator = ScenarioTemplateGenerator()


async def generate_mvs_scenario() -> GlobalState:
    """Generate Minimum Viable Scenario with real data integration."""
    return await template_generator.generate_mvs_template()


async def generate_fis_scenario() -> GlobalState:
    """Generate Full Information Scenario with comprehensive data."""
    return await template_generator.generate_fis_template()


# Export main functions
__all__ = [
    "DataProvider",
    "WorldBankProvider", 
    "FREDProvider",
    "IMFProvider",
    "ScenarioTemplateGenerator",
    "generate_mvs_scenario",
    "generate_fis_scenario",
]
