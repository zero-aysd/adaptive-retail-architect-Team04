from pathlib import Path
import json
from datetime import datetime, timedelta
import random
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
from pytrends.request import TrendReq
from langchain.tools import tool
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import logging 

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def make_trends_client():
    return TrendReq(hl="en-US", tz=330)


def fetch_interest_over_time(keywords, geo, timeframe, gprop):
    pytrend.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo, gprop=gprop)
    df = pytrend.interest_over_time()
    return df

def fetch_related_queries(keywords, geo, timeframe, gprop):
    pytrend.build_payload(kw_list=keywords, timeframe=timeframe, geo=geo, gprop=gprop)
    return pytrend.related_queries()

def fetch_realtime_trends(cat="all", geo="IN"):
    try:
        df = pytrend.realtime_trending_searches(geo=geo)
    except Exception as e:
        return pd.DataFrame()
    return df

def fetch_state_interest(keywords, sub_geo, timeframe, gprop):
    pytrend.build_payload(kw_list=keywords, timeframe=timeframe, geo=sub_geo, gprop=gprop)
    df = pytrend.interest_over_time()
    return df

def package_signals(iot_df, state_df, rq_top_df, city_hint="Surat", state_code="IN-GJ"):
    def top_keyword(df, window=-48):
        # rank by mean interest over last 'window' rows
        sub = df.iloc[window:] if len(df) + window > 0 else df
        means = sub.drop(columns=[c for c in sub.columns if c == "isPartial"], errors="ignore").mean().sort_values(ascending=False)
        return [{"keyword": k, "score": float(v)} for k, v in means.items()]

    payload = {
        "as_of": datetime.utcnow().isoformat() + "Z",
        "market": {
            "country": "IN",
            "state": state_code,
            "city_proxy": city_hint
        },
        "signals": {
            "interest_over_time_national": top_keyword(iot_df),
            "interest_over_time_state": top_keyword(state_df),
            "related_queries_top": rq_top_df.head(50).to_dict(orient="records")
        }
    }
    return payload


# @retry(
#     stop=stop_after_attempt(3),            # Retry up to 3 times
#     wait=wait_exponential(multiplier=2, min=2, max=10),  # Exponential backoff
#     retry=retry_if_exception_type(Exception)  # Retry on any exception
# )
# def run_market_analyst(
# keywords="",
# geo="",
# sub_geo="",
# timeframe="today 3-m",
# gprop="froogle",
# mock=False
# ):
#         """
#         Run a complete market trend analysis pipeline using Google Trends data.

#         This function acts as a high-level orchestrator for gathering, transforming,
#         and packaging trend insights for a given set of keywords. It fetches interest 
#         over time, geographic (state-level) interest, and related queries data, 
#         processes and merges them into a structured payload for downstream analysis 
#         or visualization.

#         Args:
#             keywords (list[str]):  
#                 A list of target keywords to analyze. Defaults to `KEYWORDS`.
#             geo (str):  
#                 The primary geographic region code (e.g., "IN" for India). Defaults to `GEO`.
#             sub_geo (str):  
#                 The sub-geographic region code (e.g., a state code like "IN-GJ"). Defaults to `SUB_GEO`.
#             timeframe (str):  
#                 The timeframe for which to fetch trends data (e.g., "today 12-m" or "now 7-d"). Defaults to `TIMEFRAME`.
#             gprop (str):  
#                 The Google property to query trends for. Common values include:
#                 - "" (default, web search)
#                 - "images"
#                 - "news"
#                 - "youtube"
#                 - "froogle" (shopping)
#             mock (bool):  
#                 If True, runs the function in mock/test mode without calling the live Google Trends API. Defaults to `MOCK`.

#         Globals Modified:
#             MOCK (bool): Updated to the provided `mock` argument.
#             pytrend (TrendReq): Initialized global Google Trends client used across helper functions.

#         Workflow:
#             1. Initializes a Google Trends client using `make_trends_client()`.
#             2. Fetches:
#             - Interest over time via `fetch_interest_over_time()`
#             - State-level interest via `fetch_state_interest()`
#             - Related queries via `fetch_related_queries()`
#             3. Flattens related queries into a unified DataFrame sorted by keyword and value.
#             4. Packages all processed trend signals using `package_signals()` for downstream consumption.

#         Returns:
#             dict: A structured dictionary containing:
#                 - **payload (dict):**  
#                 Consolidated signals and metadata output from `package_signals()`.
#                 - **artifacts (dict):**  
#                 Absolute paths to generated artifact CSV files:
#                     - `interest_over_time_csv`: Interest over time trends file.
#                     - `state_interest_over_time_csv`: State-level trends file.

#         Example:
#             >>> result = run_market_analyst(
#             ...     keywords=["electric cars", "solar panels"],
#             ...     geo="IN",
#             ...     sub_geo="IN-GJ",
#             ...     timeframe="today 3-m"
#             ... )
#             >>> result["payload"].keys()
#             dict_keys(["signals", "metadata"])
#         """
#         try:
#             global MOCK
#             MOCK = mock
#             global pytrend
#             pytrend = make_trends_client()
#         except Exception as e:
#             logger.exception("Failed to initialize Google Trends client.")
#             raise RuntimeError(f"Google Trends client initialization failed: {e}")
#             iot_df = fetch_interest_over_time(keywords, geo, timeframe, gprop)
#             state_df = fetch_state_interest(keywords, sub_geo, timeframe, gprop)
#             rq = fetch_related_queries(keywords, geo, timeframe, gprop)

#             # flatten related queries
#             rows = []
#             for kw, parts in rq.items():
#                 top_df = parts.get("top")
#                 if isinstance(top_df, pd.DataFrame):
#                     for _, r in top_df.iterrows():
#                         rows.append({"keyword": kw, "query": r["query"], "value": int(r["value"])})
#             rq_top_df = pd.DataFrame(rows).sort_values(["keyword", "value"], ascending=[True, False]).reset_index(drop=True)

#             payload = package_signals(iot_df, state_df, rq_top_df, city_hint="Surat", state_code=sub_geo)
#             # Save CSVs (for artifacts)
#             # iot_path = ARTIFACT_DIR / "interest_over_time_latest.csv"
#             # state_path = ARTIFACT_DIR / f"interest_over_time_{sub_geo}_latest.csv"
#             # iot_df.to_csv(iot_path)
#             # state_df.to_csv(state_path)
#             return {
#                 "payload": payload,
#                 "artifacts": {
#                     # "interest_over_time_csv": str((ARTIFACT_DIR / "interest_over_time_latest.csv").resolve()),
#                     # "state_interest_over_time_csv": str((ARTIFACT_DIR / f"interest_over_time_{sub_geo}_latest.csv").resolve())
#                 }
#             }

@retry(
    stop=stop_after_attempt(3),            # Retry up to 3 times
    wait=wait_exponential(multiplier=2, min=2, max=10),  # Exponential backoff
    retry=retry_if_exception_type(Exception)  # Retry on any exception
)
def run_market_analyst(
    keywords="",
    geo="",
    sub_geo="",
    timeframe="today 3-m",
    gprop="froogle",
    mock=False
):
    """
    Run a complete market trend analysis pipeline using Google Trends data.

    Includes retry logic (via Tenacity) and structured exception handling.
    """
    try:
        global MOCK
        MOCK = mock
        global pytrend
        pytrend = make_trends_client()
        logger.info("Initialized Google Trends client successfully.")
    except Exception as e:
        logger.exception("Failed to initialize Google Trends client.")
        raise RuntimeError(f"Google Trends client initialization failed: {e}")

    try:
        logger.info("Fetching interest over time data...")
        iot_df = fetch_interest_over_time(keywords, geo, timeframe, gprop)
    except Exception as e:
        logger.exception("Error fetching interest over time data.")
        raise RuntimeError(f"Interest over time fetch failed: {e}")

    try:
        logger.info("Fetching state-level interest data...")
        state_df = fetch_state_interest(keywords, sub_geo, timeframe, gprop)
    except Exception as e:
        logger.exception("Error fetching state-level interest data.")
        raise RuntimeError(f"State-level interest fetch failed: {e}")

    try:
        logger.info("Fetching related queries data...")
        rq = fetch_related_queries(keywords, geo, timeframe, gprop)
    except Exception as e:
        logger.exception("Error fetching related queries.")
        raise RuntimeError(f"Related queries fetch failed: {e}")

    try:
        logger.info("Flattening related queries data...")
        rows = []
        for kw, parts in rq.items():
            top_df = parts.get("top")
            if isinstance(top_df, pd.DataFrame):
                for _, r in top_df.iterrows():
                    rows.append({
                        "keyword": kw,
                        "query": r["query"],
                        "value": int(r["value"])
                    })

        rq_top_df = pd.DataFrame(rows).sort_values(
            ["keyword", "value"],
            ascending=[True, False]
        ).reset_index(drop=True)
    except Exception as e:
        logger.exception("Error flattening related queries.")
        raise RuntimeError(f"Failed to flatten related queries: {e}")

    try:
        logger.info("Packaging signals...")
        payload = package_signals(iot_df, state_df, rq_top_df, city_hint="Surat", state_code=sub_geo)
    except Exception as e:
        logger.exception("Error packaging signals.")
        raise RuntimeError(f"Signal packaging failed: {e}")

    logger.info("Market analysis completed successfully.")
    return {
        "payload": payload,
        "artifacts": {
            # Example placeholders for artifact paths
            # "interest_over_time_csv": str((ARTIFACT_DIR / "interest_over_time_latest.csv").resolve()),
            # "state_interest_over_time_csv": str((ARTIFACT_DIR / f"interest_over_time_{sub_geo}_latest.csv").resolve())
        }
    }