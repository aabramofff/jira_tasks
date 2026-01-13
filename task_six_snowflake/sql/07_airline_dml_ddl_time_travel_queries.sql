-- Step 0: Remeber the current time (just in case)
SET base_time = CURRENT_TIMESTAMP();

-- DML Query №1: "Mistake" — renamed all pilots as 'Unknown'
UPDATE AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS 
SET PILOT_NAME = 'Unknown';

-- DML Query №2: Use Time Travel, to see the data as it was 2 minutes ago
SELECT PILOT_NAME, COUNT(*) 
FROM AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS 
AT(OFFSET => -120) 
GROUP BY 1;

-- Restoring the names of the pilots using Time Travel feature
CREATE OR REPLACE TABLE AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS AS
SELECT * FROM AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS 
AT(OFFSET => -600);

-- DDL Query №1: "Accident" — FACT table has been deleted
DROP TABLE AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS;

-- Checkout: query'll throw an error "Object does not exist"
-- SELECT * FROM AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS;

-- DDL Qery №2: Instant tables and data restoring 
UNDROP TABLE AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS;

-- Checkout: data is here!
SELECT COUNT(*) FROM AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS;
