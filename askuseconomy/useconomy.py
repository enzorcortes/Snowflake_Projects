from snowflake.snowpark import Session
from snowflake.snowpark import functions as F
from snowflake.snowpark.types import DoubleType

# -- 1. Connect to Snowflake ------------------------------------------------
connection_params = {
    "account": "<your-account>",
    "user": "<youruser>",
    "password": "<yourpassword>",
    "role": "ACCOUNTADMIN",
    "warehouse": "COMPUTE_WH",
    "database": "ECON_AGENT_DB",
    "schema": "ANALYTICS"
}
session = Session.builder.configs(connection_params).create()
print("Connected to Snowflake!")

# -- 2. Read the two source tables -------------------------------------------
econ = session.table(
    "SNOWFLAKE_PUBLIC_DATA_FREE.PUBLIC_DATA_FREE.FINANCIAL_ECONOMIC_INDICATORS_TIMESERIES"
)
housing = session.table(
    "SNOWFLAKE_PUBLIC_DATA_FREE.PUBLIC_DATA_FREE.FREDDIE_MAC_HOUSING_TIMESERIES"
)

# -- 3. Extract CPI ----------------------------------------------------------
cpi = (
    econ
    .filter(F.col("GEO_ID") == "country/USA")
    .filter(F.col("VARIABLE_NAME") == "CPI: All items, Monthly, 1982-84 Index Date (Seasonally adjusted)")
    .select(
    F.col("DATE"),
    F.col("VALUE").cast(DoubleType()).alias("VALUE"),
    F.lit("CPI").alias("METRIC")
    )
)
print("CPI rows:", cpi.count())

# -- 4. Extract Unemployment Rate --------------------------------------------
unemployment = (
    econ
    .filter(F.col("GEO_ID") == "country/USA")
    .filter(F.col("VARIABLE_NAME") == "Current Labor Force: Unemployment Rate - 20 yrs. & over, Monthly (Seasonally adjusted)")
    .select(
    F.col("DATE"),
    F.col("VALUE").cast(DoubleType()).alias("VALUE"),
    F.lit("UNEMPLOYMENT_RATE").alias("METRIC")
    )
)
print("Unemployment rows:", unemployment.count())

# -- 5. Extract Mortgage Rate (from a different table!) ----------------------
mortgage = (
    housing
    .filter(F.col("VARIABLE_NAME") == "30-Year Fixed Rate Mortgage Rate, National Average")
    .select(
    F.col("DATE"),
    F.col("VALUE").cast(DoubleType()).alias("VALUE"),
    F.lit("MORTGAGE_RATE_30Y").alias("METRIC")
    )
)
print("Mortgage rows:", mortgage.count())

# -- 6. Union all three into one DataFrame -----------------------------------
combined = cpi.union_all(unemployment).union_all(mortgage)
print("\nCombined data sample:")
combined.show(15)

# -- 7. Pivot: one row per date, one column per metric -----------------------
dashboard = (
    combined
    .pivot("METRIC", ["CPI", "UNEMPLOYMENT_RATE", "MORTGAGE_RATE_30Y"])
    .agg(F.max("VALUE"))
    .sort(F.col("DATE").desc())
)

# -- 8. Preview the result ----------------------------------------------------
print("\nFinal pivoted dashboard:")
dashboard.show(20)
print(f"Total rows: {dashboard.count()}")
print(f"Columns: {dashboard.columns}")

session.close()
print("\nLooks good! Now we'll promote this to a Dynamic Table.")