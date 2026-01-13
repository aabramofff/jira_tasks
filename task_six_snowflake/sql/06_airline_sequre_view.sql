USE DATABASE AIRLINE_DWH;
USE SCHEMA INTEGRATION;

-- Security policy creation
-- If current role - 'ACCOUNTADMIN', see everything. 
-- In other cases (для теста) we will limit the viewing to only one country, for example 'United States'
CREATE OR REPLACE ROW ACCESS POLICY airport_security_policy
    AS (country_code VARCHAR) RETURNS BOOLEAN ->
        CURRENT_ROLE() = 'ACCOUNTADMIN' 
        OR country_code = 'US';


-- Security Policy Application
ALTER TABLE AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS 
ADD ROW ACCESS POLICY airport_security_policy ON (AIRPORT_NAME); 

-- Secure View Creation
CREATE OR REPLACE SECURE VIEW AIRLINE_DWH.ANALYTICS.SECURE_FLIGHT_REPORT AS
SELECT 
    PASSENGER_ID,
    AIRPORT_NAME,
    DEPARTURE_DATE,
    FLIGHT_STATUS
FROM AIRLINE_DWH.INTEGRATION.FACT_FLIGHTS;
        